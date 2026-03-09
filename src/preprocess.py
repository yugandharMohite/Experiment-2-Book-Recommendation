import pandas as pd
import numpy as np
import os
import json

# Resolve project root regardless of where the script is run from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == 'src' else SCRIPT_DIR

def load_data(data_dir):
    """Load MovieLens 100K dataset files."""
    # Load Ratings
    ratings = pd.read_csv(
        os.path.join(data_dir, 'u.data'),
        sep='\t',
        names=['user_id', 'movie_id', 'rating', 'timestamp']
    )

    # Load Movies
    genre_cols = ['unknown', 'Action', 'Adventure', 'Animation', 'Childrens', 'Comedy',
                  'Crime', 'Documentary', 'Drama', 'Fantasy', 'FilmNoir', 'Horror',
                  'Musical', 'Mystery', 'Romance', 'SciFi', 'Thriller', 'War', 'Western']
    movies = pd.read_csv(
        os.path.join(data_dir, 'u.item'),
        sep='|',
        encoding='latin-1',
        names=['movie_id', 'title', 'release_date', 'video_release', 'imdb_url'] + genre_cols
    )
    movies = movies[['movie_id', 'title'] + genre_cols]

    # Create a unified genre string per movie
    movies['genre_str'] = movies[genre_cols].apply(
        lambda row: ' '.join([g for g, v in zip(genre_cols, row) if v == 1]), axis=1
    )

    # Load Users (just for demographics, not used in core models right now)
    users = pd.read_csv(
        os.path.join(data_dir, 'u.user'),
        sep='|',
        names=['user_id', 'age', 'gender', 'occupation', 'zip_code']
    )

    return ratings, movies, users


def preprocess_data(ratings, movies, users):
    """Preprocess and filter data for training."""
    # ML-100k is 1-5 stars. We can keep all ratings mapping to explicit feedback.
    
    # We don't really need to filter sparsity for 100k as every user has >= 20 ratings.
    print(f"Loaded {len(ratings)} ratings, "
          f"{ratings['user_id'].nunique()} users, "
          f"{ratings['movie_id'].nunique()} movies.")

    # Map user_id and movie_id to continuous integer indices for embedding layers
    # ML-100K IDs are 1-indexed integers, but we will cleanly re-map them just in case
    user_map = {uid: i for i, uid in enumerate(sorted(ratings['user_id'].unique()))}
    movie_map = {mid: i for i, mid in enumerate(sorted(ratings['movie_id'].unique()))}

    ratings['user_idx'] = ratings['user_id'].map(user_map)
    ratings['movie_idx'] = ratings['movie_id'].map(movie_map)

    return ratings, user_map, movie_map, movies


if __name__ == "__main__":
    # Updated to the MovieLens directory
    DATA_DIR = os.path.join(PROJECT_ROOT, "Data", "ml-100k (1)", "ml-100k")
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, "Data", "processed")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print("Loading MovieLens data...")
    ratings, movies, users = load_data(DATA_DIR)

    print("Preprocessing data...")
    ratings, user_map, movie_map, movies = preprocess_data(ratings, movies, users)

    # Save processed ratings
    ratings.to_csv(os.path.join(OUTPUT_DIR, 'processed_ratings.csv'), index=False)

    # Build a movie lookup: movie_id -> title + genre_str
    movie_lookup = movies[movies['movie_id'].isin(movie_map.keys())][['movie_id', 'title', 'genre_str']].drop_duplicates('movie_id')
    movie_lookup.to_csv(os.path.join(OUTPUT_DIR, 'movie_lookup.csv'), index=False)

    # Save metadata
    metadata = {
        'num_users': len(user_map),
        'num_movies': len(movie_map),
        'user_map': {str(k): int(v) for k, v in user_map.items()},
        'movie_map': {str(k): int(v) for k, v in movie_map.items()}
    }
    with open(os.path.join(OUTPUT_DIR, 'metadata.json'), 'w') as f:
        json.dump(metadata, f)

    print(f"Data processed and saved to {OUTPUT_DIR}")

    # --- Generate Analytical Reports ---
    print("Generating analytical CSV reports...")
    reports_dir = os.path.join(PROJECT_ROOT, "reports")
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    # 1. User Activity Summary
    user_stats = ratings.groupby('user_id')['rating'].agg(['count', 'mean']).reset_index()
    user_stats.columns = ['user_id', 'total_ratings_given', 'average_rating_given']
    user_activity = user_stats.merge(users[['user_id', 'age', 'gender', 'occupation']], on='user_id', how='left')
    user_activity.to_csv(os.path.join(reports_dir, 'user_activity.csv'), index=False)
    print(f"User activity summary exported to {os.path.join(reports_dir, 'user_activity.csv')}")

    # 2. Movie Popularity Metrics
    movie_stats = ratings.groupby('movie_id')['rating'].agg(['count', 'mean']).reset_index()
    movie_stats.columns = ['movie_id', 'total_ratings_received', 'average_rating']
    
    # Bayesian / weighted popularity score formula (consistent with main.py)
    C = movie_stats['average_rating'].mean()
    m = movie_stats['total_ratings_received'].quantile(0.60)
    
    movie_stats['popularity_score'] = (
        (movie_stats['total_ratings_received'] / (movie_stats['total_ratings_received'] + m) * movie_stats['average_rating']) +
        (m / (movie_stats['total_ratings_received'] + m) * C)
    )
    
    # Add movie titles and genres
    movie_metrics = movie_stats.merge(movies[['movie_id', 'title', 'genre_str']], on='movie_id', how='left')
    # Reorder columns
    movie_metrics = movie_metrics[['movie_id', 'title', 'genre_str', 'total_ratings_received', 'average_rating', 'popularity_score']]
    movie_metrics.sort_values('popularity_score', ascending=False, inplace=True)
    movie_metrics.to_csv(os.path.join(reports_dir, 'movie_metrics.csv'), index=False)
    print(f"Movie popularity metrics exported to {os.path.join(reports_dir, 'movie_metrics.csv')}")

    print("Analytical reports generation complete.")
