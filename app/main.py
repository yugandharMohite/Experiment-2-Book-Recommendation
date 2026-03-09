from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
import numpy as np
import pandas as pd
import json
import os
import sys
from datetime import datetime
import csv

# Add src to path to import model definitions
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from model import MatrixFactorization, NCF, HybridRecommender

app = FastAPI(title="Movie Recommendation API")

# --- Activity Logging ---
def log_api_request(endpoint: str, user_id: str = None, keyword: str = None, top_k: int = None):
    """Helper to log API requests to a CSV file."""
    try:
        report_dir = "reports"
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
            
        csv_path = os.path.join(report_dir, "api_requests.csv")
        file_exists = os.path.exists(csv_path)
        
        with open(csv_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['timestamp', 'endpoint', 'user_id', 'keyword', 'top_k'])
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                endpoint,
                user_id if user_id else '',
                keyword if keyword else '',
                top_k if top_k else ''
            ])
    except Exception as e:
        print(f"Error logging API request: {e}")


# Asset paths
MF_MODEL_PATH = "models/mf_model.pt"
NCF_MODEL_PATH = "models/ncf_model.pt"
COSINE_SIM_PATH = "models/cosine_sim.npy"

METADATA_PATH = "Data/processed/metadata.json"
RATINGS_PATH = "Data/processed/processed_ratings.csv"
MOVIE_LOOKUP_PATH = "Data/processed/movie_lookup.csv"

# Global Objects
hybrid = None
ratings_df = None
movie_lookup_list = None
movie_popularity = None 

@app.on_event("startup")
def load_assets():
    global hybrid, ratings_df, movie_lookup_list, movie_popularity

    if not os.path.exists(METADATA_PATH):
        print(f"Metadata path not found: {METADATA_PATH}")
        return

    with open(METADATA_PATH, 'r') as f:
        metadata = json.load(f)
        
    num_users = metadata['num_users']
    num_movies = metadata['num_movies']
    user_map = metadata['user_map']
    movie_map = metadata['movie_map']

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Load MF
    mf_model = MatrixFactorization(num_users, num_movies, n_factors=100).to(device)
    if os.path.exists(MF_MODEL_PATH):
        mf_model.load_state_dict(torch.load(MF_MODEL_PATH, map_location=device))
        print("Loaded MF model")
    
    # Load NCF
    ncf_model = NCF(num_users, num_movies, emb_dim=64, mlp_layers=[128, 64, 32]).to(device)
    if os.path.exists(NCF_MODEL_PATH):
        ncf_model.load_state_dict(torch.load(NCF_MODEL_PATH, map_location=device))
        print("Loaded NCF model")
        
    # Load Cosine Sim
    cosine_sim = np.zeros((num_movies, num_movies))
    if os.path.exists(COSINE_SIM_PATH):
        cosine_sim = np.load(COSINE_SIM_PATH)
        print("Loaded cosine similarity matrix")

    # Load Movie Lookup
    movie_lookup = {}
    if os.path.exists(MOVIE_LOOKUP_PATH):
        print(f"Loading movie lookup from {MOVIE_LOOKUP_PATH}...")
        df = pd.read_csv(MOVIE_LOOKUP_PATH)
        movie_lookup_list = df.copy()
        movie_lookup = df.set_index('movie_id').to_dict('index')

    if os.path.exists(RATINGS_PATH):
        print(f"Loading ratings from {RATINGS_PATH}...")
        ratings_df = pd.read_csv(RATINGS_PATH)
        
        # Pre-compute popularity scores
        stats = ratings_df.groupby('movie_id')['rating'].agg(['mean', 'count']).reset_index()
        stats.columns = ['movie_id', 'avg_rating', 'num_ratings']
        C = stats['avg_rating'].mean()
        m = stats['num_ratings'].quantile(0.60) 
        stats['popularity_score'] = (
            stats['num_ratings'] / (stats['num_ratings'] + m) * stats['avg_rating']
            + m / (stats['num_ratings'] + m) * C
        )
        movie_popularity = stats.set_index('movie_id').to_dict('index')
    
    # Initialize Hybrid
    hybrid = HybridRecommender(
        mf_model=mf_model,
        ncf_model=ncf_model,
        cosine_sim=cosine_sim,
        movie_lookup=movie_lookup,
        user_map=user_map,
        movie_map=movie_map,
        w_svd=0.45, w_ncf=0.45, w_content=0.10
    )


class RecRequest(BaseModel):
    user_id: int
    top_k: int = 5


class MovieTypeRequest(BaseModel):
    movie_type: str          
    top_k: int = 10


@app.get("/")
def read_root():
    return {"message": "Welcome to the Movie Recommendation API (Hybrid MF+NCF+Content)"}


@app.post("/recommend")
def recommend(request: RecRequest):
    log_api_request(endpoint="/recommend", user_id=str(request.user_id), top_k=request.top_k)
    
    if hybrid is None:
        raise HTTPException(status_code=500, detail="Models not loaded properly")

    user_id = request.user_id
    if str(user_id) not in hybrid.user_map:
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found in training data")

    recommendations = hybrid.recommend(str(user_id), n=request.top_k, ratings_df=ratings_df, exclude_seen=True)
    
    return {
        "user_id": user_id,
        "recommendations": recommendations
    }


@app.post("/recommend/by_type")
def recommend_by_type(request: MovieTypeRequest):
    """Return top movies matching a genre/keyword in title, ranked by popularity."""
    log_api_request(endpoint="/recommend/by_type", keyword=request.movie_type, top_k=request.top_k)
    
    if movie_lookup_list is None:
        raise HTTPException(status_code=500, detail="Movie data not loaded")

    keyword = request.movie_type.strip().lower()
    if not keyword:
        raise HTTPException(status_code=400, detail="movie_type must not be empty")

    mask = (
        movie_lookup_list['title'].str.lower().str.contains(keyword, na=False)
        | movie_lookup_list['genre_str'].str.lower().str.contains(keyword, na=False)
    )
    matched = movie_lookup_list[mask].copy()

    if matched.empty:
        return {"movie_type": request.movie_type, "recommendations": [], "message": f"No movies found matching '{request.movie_type}'"}

    # Attach popularity scores
    if movie_popularity:
        matched['popularity_score'] = matched['movie_id'].map(
            lambda x: movie_popularity.get(x, {}).get('popularity_score', 0)
        )
        matched['avg_rating'] = matched['movie_id'].map(
            lambda x: round(movie_popularity.get(x, {}).get('avg_rating', 0), 2)
        )
        matched['num_ratings'] = matched['movie_id'].map(
            lambda x: int(movie_popularity.get(x, {}).get('num_ratings', 0))
        )
    else:
        matched['popularity_score'] = 0
        matched['avg_rating'] = 0
        matched['num_ratings'] = 0

    matched = matched.sort_values('popularity_score', ascending=False).head(request.top_k)

    results = []
    for _, row in matched.iterrows():
        results.append({
            "movie_id": int(row['movie_id']),
            "title": row['title'],
            "genres": row['genre_str'],
            "avg_rating": row['avg_rating'],
            "num_ratings": row['num_ratings'],
            "popularity_score": round(float(row['popularity_score']), 4)
        })

    return {
        "movie_type": request.movie_type,
        "matched_count": len(matched),
        "recommendations": results
    }


@app.get("/stats")
def get_stats():
    if ratings_df is None:
        return {"error": "Stats not available"}

    return {
        "total_users": int(ratings_df['user_id'].nunique()),
        "total_movies": int(ratings_df['movie_id'].nunique()),
        "total_ratings": int(len(ratings_df)),
        "avg_rating": float(ratings_df['rating'].mean())
    }

