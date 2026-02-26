from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tensorflow as tf
import numpy as np
import pandas as pd
import json
import os

app = FastAPI(title="Book Recommendation API")

# Asset paths
MODEL_PATHS = ["models/ncf_model.keras", "models/ncf_model.h5"]
METADATA_PATH = "Data/processed/metadata.json"
RATINGS_PATH = "Data/processed/processed_ratings.csv"
BOOK_LOOKUP_PATH = "Data/processed/book_lookup.csv"

model = None
metadata = None
ratings_df = None
book_lookup = None        # isbn -> {book_title, book_author}
book_lookup_df = None     # DataFrame for keyword search
book_popularity = None    # isbn -> {avg_rating, num_ratings, popularity_score}

@app.on_event("startup")
def load_assets():
    global model, metadata, ratings_df, book_lookup

    for path in MODEL_PATHS:
        if os.path.exists(path):
            print(f"Loading model from {path}...")
            model = tf.keras.models.load_model(path, compile=False)
            print("Model loaded successfully.")
            break
        else:
            print(f"Model path not found: {path}")

    if os.path.exists(METADATA_PATH):
        print(f"Loading metadata from {METADATA_PATH}...")
        with open(METADATA_PATH, 'r') as f:
            metadata = json.load(f)
    else:
        print(f"Metadata path not found: {METADATA_PATH}")

    if os.path.exists(RATINGS_PATH):
        print(f"Loading ratings from {RATINGS_PATH}...")
        ratings_df = pd.read_csv(RATINGS_PATH)
    else:
        print(f"Ratings path not found: {RATINGS_PATH}")

    if os.path.exists(BOOK_LOOKUP_PATH):
        print(f"Loading book lookup from {BOOK_LOOKUP_PATH}...")
        df = pd.read_csv(BOOK_LOOKUP_PATH)
        book_lookup = df.set_index('isbn')[['book_title', 'book_author']].to_dict('index')

        global book_lookup_df, book_popularity
        book_lookup_df = df.copy()

        # Pre-compute popularity scores once ratings are loaded
        if ratings_df is not None:
            stats = ratings_df.groupby('isbn')['rating'].agg(['mean', 'count']).reset_index()
            stats.columns = ['isbn', 'avg_rating', 'num_ratings']
            # Bayesian / weighted popularity score
            C = stats['avg_rating'].mean()   # global mean rating
            m = stats['num_ratings'].quantile(0.60)  # min votes threshold
            stats['popularity_score'] = (
                stats['num_ratings'] / (stats['num_ratings'] + m) * stats['avg_rating']
                + m / (stats['num_ratings'] + m) * C
            )
            book_popularity = stats.set_index('isbn').to_dict('index')
    else:
        print(f"Book lookup path not found: {BOOK_LOOKUP_PATH}")


class RecRequest(BaseModel):
    user_id: int
    top_k: int = 5


class BookTypeRequest(BaseModel):
    book_type: str          # Keyword: e.g. "mythology", "romance", "mystery"
    top_k: int = 10


@app.get("/")
def read_root():
    return {"message": "Welcome to the Book Recommendation API"}


@app.post("/recommend")
def recommend(request: RecRequest):
    if model is None or metadata is None:
        raise HTTPException(status_code=500, detail="Model or metadata not loaded")

    user_id = request.user_id
    user_map = metadata['user_map']
    book_map = metadata['book_map']
    reverse_book_map = {v: k for k, v in book_map.items()}

    if str(user_id) not in user_map:
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found in training data")

    user_idx = user_map[str(user_id)]

    # Get all book indices and predict scores
    all_book_indices = np.array(list(book_map.values()))
    user_indices = np.array([user_idx] * len(all_book_indices))

    predictions = model.predict([user_indices, all_book_indices], verbose=0)

    # Get top K books
    top_k_indices = np.argsort(predictions.flatten())[-request.top_k:][::-1]
    results = []
    for idx in top_k_indices:
        isbn = reverse_book_map[all_book_indices[idx]]
        score = float(predictions[idx])
        info = book_lookup.get(isbn, {}) if book_lookup else {}
        results.append({
            "isbn": isbn,
            "book_title": info.get("book_title", "Unknown"),
            "book_author": info.get("book_author", "Unknown"),
            "score": score
        })

    return {
        "user_id": user_id,
        "recommendations": results
    }


@app.post("/recommend/by_type")
def recommend_by_type(request: BookTypeRequest):
    """Return top books matching a keyword in title or author, ranked by popularity."""
    if book_lookup_df is None:
        raise HTTPException(status_code=500, detail="Book data not loaded")

    keyword = request.book_type.strip().lower()
    if not keyword:
        raise HTTPException(status_code=400, detail="book_type must not be empty")

    # Search titles AND authors for the keyword
    mask = (
        book_lookup_df['book_title'].str.lower().str.contains(keyword, na=False)
        | book_lookup_df['book_author'].str.lower().str.contains(keyword, na=False)
    )
    matched = book_lookup_df[mask].copy()

    if matched.empty:
        return {"book_type": request.book_type, "recommendations": [], "message": f"No books found matching '{request.book_type}'"}

    # Attach popularity scores
    if book_popularity:
        matched['popularity_score'] = matched['isbn'].map(
            lambda x: book_popularity.get(x, {}).get('popularity_score', 0)
        )
        matched['avg_rating'] = matched['isbn'].map(
            lambda x: round(book_popularity.get(x, {}).get('avg_rating', 0), 2)
        )
        matched['num_ratings'] = matched['isbn'].map(
            lambda x: int(book_popularity.get(x, {}).get('num_ratings', 0))
        )
    else:
        matched['popularity_score'] = 0
        matched['avg_rating'] = 0
        matched['num_ratings'] = 0

    matched = matched.sort_values('popularity_score', ascending=False).head(request.top_k)

    results = []
    for _, row in matched.iterrows():
        results.append({
            "isbn": row['isbn'],
            "book_title": row['book_title'],
            "book_author": row['book_author'],
            "avg_rating": row['avg_rating'],
            "num_ratings": row['num_ratings'],
            "popularity_score": round(float(row['popularity_score']), 4)
        })

    return {
        "book_type": request.book_type,
        "matched_count": len(matched),
        "recommendations": results
    }


@app.get("/stats")
def get_stats():
    if ratings_df is None:
        return {"error": "Stats not available"}

    return {
        "total_users": int(ratings_df['user_id'].nunique()),
        "total_books": int(ratings_df['isbn'].nunique()),
        "total_ratings": int(len(ratings_df)),
        "avg_rating": float(ratings_df['rating'].mean())
    }
