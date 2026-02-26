import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import io

st.set_page_config(page_title="Book Recommendation Dashboard", layout="wide")
st.title("📚 Smart Book Recommendation & Insight Dashboard")

# Configuration
API_URL = "http://127.0.0.1:8000"
DATA_PATH = "Data/processed/processed_ratings.csv"
BOOK_LOOKUP_PATH = "Data/processed/book_lookup.csv"
METADATA_PATH = "Data/processed/metadata.json"
METRICS_CSV = "reports/metrics.csv"

GENRE_SUGGESTIONS = [
    "mythology", "romance", "mystery", "thriller", "fantasy",
    "science", "history", "biography", "horror", "adventure",
    "philosophy", "psychology", "cooking", "travel", "poetry"
]


@st.cache_data
def load_ratings():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return None


@st.cache_data
def load_books():
    if os.path.exists(BOOK_LOOKUP_PATH):
        return pd.read_csv(BOOK_LOOKUP_PATH)
    return None


@st.cache_data
def load_metadata():
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, 'r') as f:
            return json.load(f)
    return None


@st.cache_data
def load_metrics():
    if os.path.exists(METRICS_CSV):
        return pd.read_csv(METRICS_CSV)
    return None


ratings_df = load_ratings()
books_df = load_books()
metadata = load_metadata()

tab1, tab2, tab3 = st.tabs(["📊 Dataset Insights", "🔍 Get Recommendations", "📈 Model Performance"])

# ── Tab 1: Dataset Overview ───────────────────────────────────────────────────
with tab1:
    st.header("Dataset Overview")
    if ratings_df is not None:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Ratings", f"{len(ratings_df):,}")
        col2.metric("Total Users", f"{ratings_df['user_id'].nunique():,}")
        col3.metric("Total Books", f"{ratings_df['isbn'].nunique():,}")
        col4.metric("Avg Rating", round(ratings_df['rating'].mean(), 2))

        st.subheader("Rating Distribution")
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.countplot(
            x='rating', data=ratings_df, palette='viridis',
            order=sorted(ratings_df['rating'].unique()), ax=ax
        )
        ax.set_xlabel("Book Rating (1-10 scale)")
        ax.set_ylabel("Count")
        st.pyplot(fig)

        if books_df is not None:
            st.subheader("Top 10 Most Rated Books")
            top_books = ratings_df['isbn'].value_counts().head(10).reset_index()
            top_books.columns = ['isbn', 'num_ratings']
            top_books = top_books.merge(books_df, on='isbn', how='left')
            st.dataframe(
                top_books[['book_title', 'book_author', 'num_ratings']].reset_index(drop=True),
                use_container_width=True
            )
    else:
        st.warning("Processed data not found. Please run `python src/preprocess.py` first.")

# ── Tab 2: Genre / Type-Based Recommendations ─────────────────────────────────
with tab2:
    st.header("🔍 Find Top Books by Genre or Theme")
    st.markdown(
        "Enter a **genre, theme, or keyword** (e.g. *mythology*, *romance*, *stephen king*, *war*) "
        "and get the most popular matching books ranked by reader rating."
    )

    st.markdown("**Quick picks:**")
    cols = st.columns(len(GENRE_SUGGESTIONS))
    selected_genre = st.session_state.get("selected_genre", "")
    for i, genre in enumerate(GENRE_SUGGESTIONS):
        if cols[i].button(genre.capitalize(), key=f"btn_{genre}"):
            selected_genre = genre
            st.session_state["selected_genre"] = genre

    st.markdown("---")
    col_input, col_count = st.columns([3, 1])
    with col_input:
        book_type = st.text_input(
            "Or type a keyword / genre:",
            value=selected_genre,
            placeholder="e.g. mythology, romance, harry potter..."
        )
    with col_count:
        top_k = st.number_input("Results to show", min_value=5, max_value=50, value=10, step=5)

    if st.button("🔎 Search Books", type="primary"):
        if not book_type.strip():
            st.warning("Please enter a keyword or select a genre above.")
        else:
            with st.spinner(f"Searching for '{book_type}' books..."):
                try:
                    response = requests.post(
                        f"{API_URL}/recommend/by_type",
                        json={"book_type": book_type.strip(), "top_k": int(top_k)}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        recs = data.get("recommendations", [])
                        if not recs:
                            st.info(f"No books found matching **'{book_type}'**. Try a different keyword.")
                        else:
                            st.success(
                                f"Found **{data.get('matched_count', len(recs))}** books matching "
                                f"**'{book_type}'** — showing top {len(recs)} by popularity."
                            )
                            rec_df = pd.DataFrame(recs)
                            rec_df.index = rec_df.index + 1
                            rec_df = rec_df.rename(columns={
                                "book_title": "Title", "book_author": "Author",
                                "isbn": "ISBN", "avg_rating": "Avg Rating",
                                "num_ratings": "# Ratings", "popularity_score": "Score"
                            })
                            st.dataframe(
                                rec_df[["Title", "Author", "Avg Rating", "# Ratings", "Score", "ISBN"]],
                                use_container_width=True
                            )
                    else:
                        st.error(f"API Error: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Could not connect to API. (Error: {e})")
                    st.info(f"Make sure the API is running at: {API_URL}")

# ── Tab 3: Model Performance & Metrics Export ─────────────────────────────────
with tab3:
    st.header("📈 Model Performance & Metrics Export")

    # Live stats from API
    try:
        stats_resp = requests.get(f"{API_URL}/stats", timeout=3)
        if stats_resp.status_code == 200:
            stats = stats_resp.json()
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Users", f"{stats.get('total_users', 'N/A'):,}")
            col2.metric("Total Books", f"{stats.get('total_books', 'N/A'):,}")
            col3.metric("Total Ratings", f"{stats.get('total_ratings', 'N/A'):,}")
            col4.metric("Avg Rating", round(stats.get("avg_rating", 0), 2))
    except Exception:
        st.caption("_Live stats unavailable — start the API to see live counts._")

    st.divider()

    # ── Metrics History ───────────────────────────────────────────────────────
    metrics_df = load_metrics()

    if metrics_df is not None and not metrics_df.empty:
        st.subheader("📋 Training Runs History")
        display_cols = ["timestamp", "epochs", "embedding_dim", "batch_size",
                        "test_mse", "test_mae", "test_rmse"]
        available_cols = [c for c in display_cols if c in metrics_df.columns]
        st.dataframe(metrics_df[available_cols].sort_values("timestamp", ascending=False).reset_index(drop=True),
                     use_container_width=True)

        # ── Download Button ───────────────────────────────────────────────────
        csv_bytes = metrics_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Metrics CSV",
            data=csv_bytes,
            file_name="book_rec_metrics.csv",
            mime="text/csv"
        )

        # ── Performance Line Chart ────────────────────────────────────────────
        if len(metrics_df) > 1:
            st.subheader("📉 Metrics Over Training Runs")
            chart_df = metrics_df[["timestamp", "test_mse", "test_mae", "test_rmse"]].copy()
            chart_df = chart_df.set_index("timestamp")
            st.line_chart(chart_df, use_container_width=True)
        else:
            st.subheader("Latest Run Metrics")
            last = metrics_df.iloc[-1]
            m1, m2, m3 = st.columns(3)
            m1.metric("Test MSE", round(last.get("test_mse", 0), 4))
            m2.metric("Test MAE", round(last.get("test_mae", 0), 4))
            m3.metric("Test RMSE", round(last.get("test_rmse", 0), 4))
    else:
        st.info(
            "No metrics history found yet.\n\n"
            "Run `python src/train.py` to generate `reports/metrics.csv`."
        )
        # Show last known metrics from training
        st.subheader("Last Known Metrics (from latest run)")
        m1, m2, m3 = st.columns(3)
        m1.metric("Test MSE", "2.9133")
        m2.metric("Test MAE", "1.3436")
        m3.metric("Test RMSE", "1.7068")

    st.divider()
    st.caption("Full run history tracked via MLflow — run `mlflow ui` from the project root.")
