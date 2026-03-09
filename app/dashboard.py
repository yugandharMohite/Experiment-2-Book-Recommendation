import streamlit as st
import pandas as pd
import requests
import matplotlib.subplots as subplots
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import io

st.set_page_config(page_title="Movie Recommendation Dashboard", layout="wide")
st.title("🎬 Smart Movie Recommendation & Insight Dashboard")

# Configuration
API_URL = "http://127.0.0.1:8000"
DATA_PATH = "Data/processed/processed_ratings.csv"
MOVIE_LOOKUP_PATH = "Data/processed/movie_lookup.csv"
METADATA_PATH = "Data/processed/metadata.json"
METRICS_CSV = "reports/metrics.csv"

GENRE_SUGGESTIONS = [
    "action", "adventure", "animation", "children", "comedy",
    "crime", "documentary", "drama", "fantasy", "film-noir",
    "horror", "musical", "mystery", "romance", "sci-fi", 
    "thriller", "war", "western"
]

@st.cache_data
def load_ratings():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return None

@st.cache_data
def load_movies():
    if os.path.exists(MOVIE_LOOKUP_PATH):
        return pd.read_csv(MOVIE_LOOKUP_PATH)
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
movies_df = load_movies()
metadata = load_metadata()

tab1, tab2, tab3 = st.tabs(["📊 Dataset Insights", "🔍 Get Recommendations", "📈 Model Performance"])

# ── Tab 1: Dataset Overview ───────────────────────────────────────────────────
with tab1:
    st.header("Dataset Overview")
    if ratings_df is not None:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Ratings", f"{len(ratings_df):,}")
        col2.metric("Total Users", f"{ratings_df['user_id'].nunique():,}")
        col3.metric("Total Movies", f"{ratings_df['movie_id'].nunique():,}")
        col4.metric("Avg Rating", round(ratings_df['rating'].mean(), 2))

        st.subheader("Rating Distribution")
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.countplot(
            x='rating', data=ratings_df, palette='viridis',
            order=sorted(ratings_df['rating'].unique()), ax=ax
        )
        ax.set_xlabel("Movie Rating (1-5 scale)")
        ax.set_ylabel("Count")
        st.pyplot(fig)

        if movies_df is not None:
            st.subheader("Top 10 Most Rated Movies")
            top_mvs = ratings_df['movie_id'].value_counts().head(10).reset_index()
            top_mvs.columns = ['movie_id', 'num_ratings']
            top_mvs = top_mvs.merge(movies_df, on='movie_id', how='left')
            st.dataframe(
                top_mvs[['title', 'genre_str', 'num_ratings']].reset_index(drop=True),
                use_container_width=True
            )
    else:
        st.warning("Processed data not found. Please run `python src/preprocess.py` first.")

# ── Tab 2: Genre / Type-Based Recommendations ─────────────────────────────────
with tab2:
    st.header("🔍 Find Top Movies by Genre or Theme")
    st.markdown(
        "Enter a **genre or keyword** (e.g. *action*, *sci-fi*, *star wars*) "
        "and get the most popular matching movies ranked by popularity score."
    )

    st.markdown("**Quick picks:**")
    cols = st.columns(6)
    selected_genre = st.session_state.get("selected_genre", "")
    for i, genre in enumerate(GENRE_SUGGESTIONS[:18]):
        col_idx = i % 6
        if cols[col_idx].button(genre.capitalize(), key=f"btn_{genre}"):
            selected_genre = genre
            st.session_state["selected_genre"] = genre

    st.markdown("---")
    col_input, col_count = st.columns([3, 1])
    with col_input:
        movie_type = st.text_input(
            "Or type a keyword / genre:",
            value=selected_genre,
            placeholder="e.g. sci-fi, romance, star wars..."
        )
    with col_count:
        top_k = st.number_input("Results to show", min_value=5, max_value=50, value=10, step=5)

    if st.button("🔎 Search Movies", type="primary"):
        if not movie_type.strip():
            st.warning("Please enter a keyword or select a genre above.")
        else:
            with st.spinner(f"Searching for '{movie_type}' movies..."):
                try:
                    response = requests.post(
                        f"{API_URL}/recommend/by_type",
                        json={"movie_type": movie_type.strip(), "top_k": int(top_k)}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        recs = data.get("recommendations", [])
                        if not recs:
                            st.info(f"No movies found matching **'{movie_type}'**. Try a different keyword.")
                        else:
                            st.success(
                                f"Found **{data.get('matched_count', len(recs))}** movies matching "
                                f"**'{movie_type}'** — showing top {len(recs)} by popularity."
                            )
                            rec_df = pd.DataFrame(recs)
                            rec_df.index = rec_df.index + 1
                            rec_df = rec_df.rename(columns={
                                "title": "Title", "genres": "Genres",
                                "avg_rating": "Avg Rating",
                                "num_ratings": "# Ratings", "popularity_score": "Score"
                            })
                            st.dataframe(
                                rec_df[["Title", "Genres", "Avg Rating", "# Ratings", "Score"]],
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
            col2.metric("Total Movies", f"{stats.get('total_movies', 'N/A'):,}")
            col3.metric("Total Ratings", f"{stats.get('total_ratings', 'N/A'):,}")
            col4.metric("Avg Rating", round(stats.get("avg_rating", 0), 2))
    except Exception:
        st.caption("_Live stats unavailable — start the API to see live counts._")

    st.divider()

    # ── Metrics History ───────────────────────────────────────────────────────
    metrics_df = load_metrics()

    if metrics_df is not None and not metrics_df.empty:
        st.subheader("📋 Training Runs History")
        # Adjust display columns for new metric names
        display_cols = ["timestamp", "epochs", "test_mf_rmse", "test_ncf_rmse", "hybrid_rmse_estimate"]
        available_cols = [c for c in display_cols if c in metrics_df.columns]
        st.dataframe(metrics_df[available_cols].sort_values("timestamp", ascending=False).reset_index(drop=True),
                     use_container_width=True)

        # ── Download Button ───────────────────────────────────────────────────
        csv_bytes = metrics_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Metrics CSV",
            data=csv_bytes,
            file_name="movie_rec_metrics.csv",
            mime="text/csv"
        )

        # ── Performance Line Chart ────────────────────────────────────────────
        valid_metric_cols = [c for c in ["test_mf_rmse", "test_ncf_rmse", "hybrid_rmse_estimate"] if c in metrics_df.columns]
        if len(metrics_df) > 1 and valid_metric_cols:
            st.subheader("📉 Metrics Over Training Runs")
            chart_df = metrics_df[["timestamp"] + valid_metric_cols].copy()
            chart_df = chart_df.set_index("timestamp")
            st.line_chart(chart_df, use_container_width=True)
        else:
            st.subheader("Latest Run Metrics")
            last = metrics_df.iloc[-1]
            m1, m2, m3 = st.columns(3)
            m1.metric("MF RMSE", round(last.get("test_mf_rmse", 0), 4))
            m2.metric("NCF RMSE", round(last.get("test_ncf_rmse", 0), 4))
            m3.metric("Hybrid RMSE (Est)", round(last.get("hybrid_rmse_estimate", 0), 4))
    else:
        st.info(
            "No metrics history found yet.\n\n"
            "Run `python src/train.py` to generate `reports/metrics.csv`."
        )

    st.divider()
    st.caption("Full run history tracked via MLflow — run `mlflow ui` from the project root.")
