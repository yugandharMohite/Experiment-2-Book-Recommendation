import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from preprocess import load_data, preprocess_data

# Resolve project root regardless of where the script is run from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == 'src' else SCRIPT_DIR


def run_eda(data_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ratings, books, users = load_data(data_dir)
    ratings_filtered, user_map, book_map, books = preprocess_data(ratings, books, users)

    # 1. Rating Distribution
    plt.figure(figsize=(10, 6))
    sns.countplot(x='rating', data=ratings_filtered, palette='viridis', order=sorted(ratings_filtered['rating'].unique()))
    plt.title('Distribution of Book Ratings (Explicit, 1-10)')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.savefig(os.path.join(output_dir, 'rating_dist.png'))
    plt.close()

    # 2. Top 10 Most Rated Books
    top_rated = ratings_filtered.groupby('isbn').size().sort_values(ascending=False).head(10)
    top_rated_titles = books[books['isbn'].isin(top_rated.index)][['isbn', 'book_title', 'book_author']].drop_duplicates('isbn')
    top_10 = top_rated.reset_index().merge(top_rated_titles, on='isbn')
    top_10.columns = ['isbn', 'count', 'title', 'author']

    plt.figure(figsize=(12, 8))
    sns.barplot(x='count', y='title', data=top_10, palette='magma')
    plt.title('Top 10 Most Rated Books')
    plt.xlabel('Number of Ratings')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'top_10_books.png'))
    plt.close()

    # 3. User Age Distribution
    users_clean = users[users['age'].notna() & (users['age'] > 5) & (users['age'] < 100)]
    plt.figure(figsize=(10, 6))
    sns.histplot(users_clean['age'], bins=30, kde=True, color='teal')
    plt.title('User Age Distribution')
    plt.xlabel('Age')
    plt.savefig(os.path.join(output_dir, 'user_age_dist.png'))
    plt.close()

    # 4. Ratings per user
    ratings_per_user = ratings_filtered.groupby('user_id').size()
    plt.figure(figsize=(10, 6))
    sns.histplot(ratings_per_user.clip(upper=100), bins=50, color='purple')
    plt.title('Ratings per User (clipped at 100)')
    plt.xlabel('Number of Ratings')
    plt.savefig(os.path.join(output_dir, 'ratings_per_user.png'))
    plt.close()

    print(f"EDA plots saved to {output_dir}")


if __name__ == "__main__":
    DATA_DIR = os.path.join(PROJECT_ROOT, "Data", "Book Data")
    EDA_OUTPUT = os.path.join(PROJECT_ROOT, "reports", "figures")
    run_eda(DATA_DIR, EDA_OUTPUT)
