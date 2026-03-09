"""
Unit tests for the Nutrition Recommendation API.
Run with: pytest tests/ -v
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from recommender import load_artifacts

client = TestClient(app)

# Ensure the model is trained/available before running tests
@pytest.fixture(scope="module", autouse=True)
def setup_model():
    # If the model doesn't exist, we skip tests that require it
    try:
        load_artifacts()
    except FileNotFoundError:
        pytest.skip("Model artifacts not found. Run train_and_save_model.py first.")

# ── Tests ─────────────────────────────────────────────────────────

def test_root_returns_200():
    """GET / should return 200."""
    response = client.get("/")
    assert response.status_code == 200

def test_health_check_returns_valid_structure():
    """GET /health should return model status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "model_loaded" in data
    assert data["model_loaded"] is True

def test_bmi_calculator():
    """GET /bmi should correctly calculate BMI."""
    response = client.get("/bmi?height_cm=180&weight_kg=75")
    assert response.status_code == 200
    data = response.json()
    assert data["bmi"] == 23.15
    assert data["category"] == "Normal Weight"
    assert "healthy_weight_range" in data

def test_bmi_calculator_invalid_input():
    """GET /bmi with invalid input should return 422."""
    response = client.get("/bmi?height_cm=-10&weight_kg=75")
    assert response.status_code == 422

def test_list_plans():
    """GET /plans should return a list of plans."""
    response = client.get("/plans")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "calorie_target" in data[0]

def test_recommendation_valid_user():
    """POST /recommend should return a nutrition plan."""
    payload = {
        "name": "Test User",
        "gender": "Female",
        "age": 28,
        "height_cm": 165,
        "weight_kg": 60,
        "family_history_obesity": "no",
        "high_caloric_food": "yes",
        "vegetable_frequency": 2.5,
        "main_meals_per_day": 3,
        "snacking": "Sometimes",
        "smoker": "no",
        "water_intake_litres": 2,
        "calorie_monitoring": "no",
        "physical_activity_days": 3,
        "tech_device_hours": 2,
        "alcohol_frequency": "Sometimes",
        "transport_mode": "Automobile",
        "diet_preference": "none",
        "allergies": [],
        "health_goal": "maintain"
    }
    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["name"] == "Test User"
    assert data["bmi"] == 22.04
    assert "macros" in data
    assert "meal_plan" in data
    assert len(data["similar_users"]) > 0

def test_recommendation_invalid_payload():
    """POST /recommend with missing fields should 422."""
    payload = {
        "name": "Test User"
        # missing all required fields
    }
    response = client.post("/recommend", json=payload)
    assert response.status_code == 422
