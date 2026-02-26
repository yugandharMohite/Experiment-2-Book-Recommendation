import pandas as pd
import numpy as np
import os
import json

# Resolve project root regardless of where the script is run from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == 'src' else SCRIPT_DIR

def load_data(data_dir):
    """Load Book-Crossing dataset files."""
    # Load Ratings
    ratings = pd.read_csv(
        os.path.join(data_dir, 'Ratings.csv'),
        encoding='latin-1'
    )
    # Standardize column names
    ratings.columns = ['user_id', 'isbn', 'rating']

    # Load Books
    books = pd.read_csv(
        os.path.join(data_dir, 'Books.csv'),
        encoding='latin-1',
        on_bad_lines='skip'
    )
    books.columns = ['isbn', 'book_title', 'book_author', 'year_of_publication',
                     'publisher', 'image_url_s', 'image_url_m', 'image_url_l']

    # Load Users
    users = pd.read_csv(
        os.path.join(data_dir, 'Users.csv'),
        encoding='latin-1'
    )
    users.columns = ['user_id', 'location', 'age']

    return ratings, books, users


def preprocess_data(ratings, books, users):
    """Preprocess and filter data for training."""
    # Keep only explicit ratings (rating > 0)
    ratings = ratings[ratings['rating'] > 0].copy()

    # Remove users and books with very few interactions to reduce sparsity
    min_book_ratings = 5
    min_user_ratings = 5

    book_counts = ratings['isbn'].value_counts()
    user_counts = ratings['user_id'].value_counts()

    ratings = ratings[ratings['isbn'].isin(book_counts[book_counts >= min_book_ratings].index)]
    ratings = ratings[ratings['user_id'].isin(user_counts[user_counts >= min_user_ratings].index)]

    print(f"Filtered to {len(ratings)} ratings, "
          f"{ratings['user_id'].nunique()} users, "
          f"{ratings['isbn'].nunique()} books.")

    # Map user_id and isbn to continuous integer indices for embedding layers
    user_map = {uid: i for i, uid in enumerate(sorted(ratings['user_id'].unique()))}
    book_map = {isbn: i for i, isbn in enumerate(sorted(ratings['isbn'].unique()))}

    ratings['user_idx'] = ratings['user_id'].map(user_map)
    ratings['book_idx'] = ratings['isbn'].map(book_map)

    return ratings, user_map, book_map, books


if __name__ == "__main__":
    DATA_DIR = os.path.join(PROJECT_ROOT, "Data", "Book Data")
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, "Data", "processed")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print("Loading data...")
    ratings, books, users = load_data(DATA_DIR)

    print("Preprocessing data...")
    ratings, user_map, book_map, books = preprocess_data(ratings, books, users)

    # Save processed ratings
    ratings.to_csv(os.path.join(OUTPUT_DIR, 'processed_ratings.csv'), index=False)

    # Build a book title lookup: isbn -> title + author
    book_lookup = books[books['isbn'].isin(book_map.keys())][['isbn', 'book_title', 'book_author']].drop_duplicates('isbn')
    book_lookup.to_csv(os.path.join(OUTPUT_DIR, 'book_lookup.csv'), index=False)

    # Save metadata
    metadata = {
        'num_users': len(user_map),
        'num_books': len(book_map),
        'user_map': {str(k): int(v) for k, v in user_map.items()},
        'book_map': {str(k): int(v) for k, v in book_map.items()}
    }
    with open(os.path.join(OUTPUT_DIR, 'metadata.json'), 'w') as f:
        json.dump(metadata, f)

    print(f"Data processed and saved to {OUTPUT_DIR}")
