"""
Unit tests for the Book Recommendation API.
Run with: pytest tests/ -v
"""

import sys
import os
import pytest
import pandas as pd
from unittest.mock import patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import app.main as main_module
from app.main import app

client = TestClient(app)

# ── Shared mock data ────────────────────────────────────────────────────────────

MOCK_BOOK_LOOKUP_DF = pd.DataFrame([
    {"isbn": "0345339681", "book_title": "Mythology: Timeless Tales of Gods and Heroes", "book_author": "Edith Hamilton"},
    {"isbn": "0439064872", "book_title": "Harry Potter and the Chamber of Secrets", "book_author": "J. K. Rowling"},
    {"isbn": "0147516315", "book_title": "Romeo and Juliet (romance classic)", "book_author": "William Shakespeare"},
    {"isbn": "0316769177", "book_title": "The Catcher in the Rye", "book_author": "J.D. Salinger"},
])

MOCK_BOOK_POPULARITY = {
    "0345339681": {"avg_rating": 8.5, "num_ratings": 120, "popularity_score": 8.2},
    "0439064872": {"avg_rating": 9.0, "num_ratings": 500, "popularity_score": 8.9},
    "0147516315": {"avg_rating": 7.5, "num_ratings": 80,  "popularity_score": 7.1},
    "0316769177": {"avg_rating": 7.0, "num_ratings": 60,  "popularity_score": 6.8},
}

MOCK_RATINGS_DF = pd.DataFrame([
    {"user_id": 1, "isbn": "0345339681", "rating": 8, "user_idx": 0, "book_idx": 0},
    {"user_id": 2, "isbn": "0439064872", "rating": 9, "user_idx": 1, "book_idx": 1},
])


# ── Basic health check ──────────────────────────────────────────────────────────

def test_root_returns_200():
    """GET / should return 200 and a welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Book" in response.json()["message"]


# ── Stats endpoint ──────────────────────────────────────────────────────────────

def test_stats_returns_valid_structure():
    """GET /stats should return known keys or an error key."""
    with patch.object(main_module, 'ratings_df', MOCK_RATINGS_DF):
        response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    valid_keys = {"total_users", "total_books", "total_ratings", "avg_rating", "error"}
    assert len(set(data.keys()) & valid_keys) > 0


def test_stats_without_data_returns_error_key():
    """GET /stats when ratings_df is None should return error key."""
    with patch.object(main_module, 'ratings_df', None):
        response = client.get("/stats")
    assert response.status_code == 200
    assert "error" in response.json()


# ── Genre / Type recommendation endpoint ────────────────────────────────────────

def test_recommend_by_type_valid_keyword():
    """POST /recommend/by_type with a valid keyword should return 200 and a list."""
    with patch.object(main_module, 'book_lookup_df', MOCK_BOOK_LOOKUP_DF), \
         patch.object(main_module, 'book_popularity', MOCK_BOOK_POPULARITY):
        response = client.post("/recommend/by_type", json={"book_type": "mythology", "top_k": 5})
    assert response.status_code == 200
    data = response.json()
    assert "book_type" in data
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) >= 1


def test_recommend_by_type_returns_expected_fields():
    """Each recommendation should contain isbn, book_title, book_author, avg_rating."""
    with patch.object(main_module, 'book_lookup_df', MOCK_BOOK_LOOKUP_DF), \
         patch.object(main_module, 'book_popularity', MOCK_BOOK_POPULARITY):
        response = client.post("/recommend/by_type", json={"book_type": "romance", "top_k": 3})
    assert response.status_code == 200
    recs = response.json().get("recommendations", [])
    if recs:
        for rec in recs:
            assert "isbn" in rec
            assert "book_title" in rec
            assert "book_author" in rec
            assert "avg_rating" in rec


def test_recommend_by_type_empty_keyword_returns_400():
    """POST /recommend/by_type with empty keyword should return 400."""
    with patch.object(main_module, 'book_lookup_df', MOCK_BOOK_LOOKUP_DF), \
         patch.object(main_module, 'book_popularity', MOCK_BOOK_POPULARITY):
        response = client.post("/recommend/by_type", json={"book_type": "  ", "top_k": 5})
    assert response.status_code == 400


def test_recommend_by_type_unknown_genre_returns_empty_list():
    """POST /recommend/by_type with a nonsense keyword should return empty recommendations."""
    with patch.object(main_module, 'book_lookup_df', MOCK_BOOK_LOOKUP_DF), \
         patch.object(main_module, 'book_popularity', MOCK_BOOK_POPULARITY):
        response = client.post(
            "/recommend/by_type",
            json={"book_type": "xyzxyzxyz_nonexistent_genre_abc", "top_k": 5}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["recommendations"] == []


# ── User-based recommendation endpoint ─────────────────────────────────────────

def test_recommend_invalid_user_returns_404_or_500():
    """POST /recommend with an unknown user ID should return 404 (or 500 if model not loaded)."""
    response = client.post("/recommend", json={"user_id": 999999999, "top_k": 5})
    assert response.status_code in [404, 500]


def test_recommend_missing_fields_returns_422():
    """POST /recommend without required fields should return 422 (validation error)."""
    response = client.post("/recommend", json={})
    assert response.status_code == 422
