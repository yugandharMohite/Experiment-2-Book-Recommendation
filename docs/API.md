# API Reference

## Overview

The Nutrition Recommendation System exposes a RESTful API built with FastAPI. All endpoints return JSON responses and support standard HTTP methods.

**Base URL:** `http://api-server:8000`  
**API Documentation:** `http://api-server:8000/docs` (Swagger UI)  
**OpenAPI Schema:** `http://api-server:8000/openapi.json`

## Authentication

Currently, the API operates in open mode. For production deployments, implement JWT authentication:

```python
from fastapi.security import HTTPBearer
security = HTTPBearer()

@app.get("/protected")
async def protected_endpoint(credentials: HTTPAuthCredentials = Depends(security)):
    return {"message": "Authenticated"}
```

## Response Format

### Success Response (200 OK)
```json
{
  "status": "success",
  "data": { /* endpoint-specific data */ },
  "message": "Operation completed successfully"
}
```

### Error Response (400, 404, 500)
```json
{
  "status": "error",
  "code": "INVALID_INPUT",
  "message": "Detailed error message",
  "errors": [
    {
      "field": "age",
      "message": "Age must be between 1 and 120"
    }
  ]
}
```

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Purpose:** Verify API and model availability

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2026-03-10T10:30:00Z",
  "version": "1.0.0"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### 2. BMI Calculator

**Endpoint:** `GET /bmi`

**Purpose:** Calculate BMI and obesity classification

**Query Parameters:**
| Param | Type | Required | Range | Description |
|-------|------|----------|-------|-------------|
| height_cm | float | Yes | 100-250 | Height in centimeters |
| weight_kg | float | Yes | 20-300 | Weight in kilograms |

**Response:**
```json
{
  "height_cm": 180,
  "weight_kg": 75,
  "bmi": 23.15,
  "category": "Normal Weight",
  "bmi_range": {
    "min": 18.5,
    "max": 25.0
  },
  "weight_to_healthy": 0,
  "status": "healthy"
}
```

**Example:**
```bash
curl "http://localhost:8000/bmi?height_cm=180&weight_kg=75"

# Response
{
  "height_cm": 180,
  "weight_kg": 75,
  "bmi": 23.15,
  "category": "Normal Weight",
  "bmi_range": { "min": 18.5, "max": 25.0 },
  "weight_to_healthy": 0,
  "status": "healthy"
}
```

---

### 3. Get Recommendation

**Endpoint:** `POST /recommend`

**Purpose:** Generate personalized nutrition recommendation

**Request Body:**
```json
{
  "gender": "Male",
  "age": 35,
  "height": 1.70,
  "weight": 110,
  "family_history": "yes",
  "favc": "yes",
  "fcvc": 1,
  "ncp": 3,
  "caec": "Always",
  "smoke": "no",
  "ch2o": 1,
  "scc": "no",
  "faf": 0,
  "tue": 3,
  "calc": "Frequently",
  "mtrans": "Automobile"
}
```

**Field Descriptions:**

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| gender | string | "Male", "Female" | User gender |
| age | integer | 1-120 | Age in years |
| height | float | 1.0-2.5 | Height in meters |
| weight | float | 20-300 | Weight in kilograms |
| family_history | string | "yes", "no" | Family history of obesity |
| favc | string | "yes", "no" | Frequent high caloric food |
| fcvc | float | 0-3 | Frequency of vegetable consumption (meal freq) |
| ncp | integer | 1-5 | Number of main meals per day |
| caec | string | "no", "Sometimes", "Frequently", "Always" | Snacking between meals |
| smoke | string | "yes", "no" | Smoking habit |
| ch2o | float | 1-3 | Daily water consumption (liters) |
| scc | string | "yes", "no" | Calories consumption monitoring |
| faf | float | 0-5 | Physical activity frequency (times/week) |
| tue | float | 0-2+ | Technology device usage time (hours/day) |
| calc | string | "no", "Sometimes", "Frequently", "Always" | Alcohol consumption |
| mtrans | string | "Automobile", "Bike", "Motorbike", "Public_Transportation", "Walking" | Transportation used |

**Response:**
```json
{
  "status": "success",
  "data": {
    "user_profile": {
      "bmi": 38.05,
      "height": 1.70,
      "weight": 110,
      "age": 35
    },
    "prediction": {
      "obesity_level": "Obesity_Type_I",
      "confidence": 0.96,
      "probabilities": {
        "Insufficient_Weight": 0.001,
        "Normal_Weight": 0.002,
        "Overweight_Level_I": 0.015,
        "Overweight_Level_II": 0.008,
        "Obesity_Type_I": 0.96,
        "Obesity_Type_II": 0.012,
        "Obesity_Type_III": 0.002
      }
    },
    "recommendation": {
      "obesity_level": "Obesity_Type_I",
      "calorie_target": "1200–1500 kcal/day",
      "macros": "Carbs 30% | Protein 40% | Fat 30%",
      "hydration": "3.0 litres/day",
      "exercise": "Low-impact cardio daily (45 min), consult physiotherapist",
      "priority": "⚠️  Consult dietitian. Strict calorie control + high protein",
      "meal_plan": [
        "Protein smoothie with spinach & chia seeds",
        "Grilled turkey breast + roasted vegetables",
        "Large mixed salad + boiled eggs",
        "Lentil soup (no bread)"
      ],
      "foods_to_increase": [
        "Leafy greens",
        "High-protein foods",
        "Fibre",
        "Water"
      ],
      "foods_to_avoid": [
        "Sugar",
        "Alcohol",
        "Refined carbs",
        "High-fat dairy",
        "Fast food"
      ]
    },
    "personalized_alerts": [
      "High caloric food consumption detected",
      "Low water intake — increase hydration urgently",
      "Very low physical activity — start with 20 min walks",
      "High tech device usage — sedentary risk, reduce screen time"
    ],
    "similar_users": [
      {
        "user_id": 42,
        "age": 36,
        "bmi": 38.2,
        "obesity_level": "Obesity_Type_I",
        "similarity": 0.9876,
        "physical_activity": 0.5,
        "water_intake": 1.2
      }
    ],
    "timestamp": "2026-03-10T10:30:00Z"
  }
}
```

**Error Responses:**

- Invalid input (400):
```json
{
  "status": "error",
  "code": "INVALID_INPUT",
  "message": "Validation error",
  "errors": [
    {
      "field": "age",
      "message": "age must be between 1 and 120"
    }
  ]
}
```

- Model not loaded (500):
```json
{
  "status": "error",
  "code": "MODEL_ERROR",
  "message": "Model not loaded. Please try again later."
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "Male",
    "age": 35,
    "height": 1.70,
    "weight": 110,
    "family_history": "yes",
    "favc": "yes",
    "fcvc": 1,
    "ncp": 3,
    "caec": "Always",
    "smoke": "no",
    "ch2o": 1,
    "scc": "no",
    "faf": 0,
    "tue": 3,
    "calc": "Frequently",
    "mtrans": "Automobile"
  }'
```

**Example (Python):**
```python
import requests

user_data = {
    "gender": "Female",
    "age": 28,
    "height": 1.62,
    "weight": 80,
    "family_history": "no",
    "favc": "no",
    "fcvc": 2,
    "ncp": 3,
    "caec": "Sometimes",
    "smoke": "no",
    "ch2o": 2,
    "scc": "yes",
    "faf": 2,
    "tue": 1,
    "calc": "Sometimes",
    "mtrans": "Public_Transportation"
}

response = requests.post(
    "http://localhost:8000/recommend",
    json=user_data
)
result = response.json()
print(f"Obesity Level: {result['data']['prediction']['obesity_level']}")
print(f"Confidence: {result['data']['prediction']['confidence']:.1%}")
```

---

### 4. Find Similar Users

**Endpoint:** `GET /similar-users`

**Purpose:** Find users with similar profiles

**Query Parameters:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| user_id | integer | Yes | - | Index of user in dataset |
| k | integer | No | 5 | Number of similar users to return |

**Response:**
```json
{
  "status": "success",
  "data": {
    "query_user_id": 42,
    "similar_users": [
      {
        "rank": 1,
        "user_id": 15,
        "similarity_score": 0.9876,
        "age": 36,
        "bmi": 38.2,
        "obesity_level": "Obesity_Type_I",
        "physical_activity": 0.5,
        "water_intake": 1.2,
        "vegetable_consumption": 1.1
      },
      {
        "rank": 2,
        "user_id": 87,
        "similarity_score": 0.9654,
        "age": 34,
        "bmi": 37.8,
        "obesity_level": "Obesity_Type_I",
        "physical_activity": 0.6,
        "water_intake": 1.3,
        "vegetable_consumption": 1.0
      }
    ],
    "total_similar_users": 2
  }
}
```

**Example:**
```bash
curl "http://localhost:8000/similar-users?user_id=42&k=5"
```

---

### 5. Batch Prediction (Optional)

**Endpoint:** `POST /batch-recommend`

**Purpose:** Process multiple users in one request

**Request Body:**
```json
{
  "users": [
    {
      "user_id": 1,
      "gender": "Male",
      "age": 35,
      "height": 1.70,
      "weight": 110,
      ...
    },
    {
      "user_id": 2,
      "gender": "Female",
      "age": 28,
      ...
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_processed": 2,
    "total_successful": 2,
    "total_failed": 0,
    "results": [
      {
        "user_id": 1,
        "obesity_level": "Obesity_Type_I",
        "confidence": 0.95,
        "status": "success"
      },
      {
        "user_id": 2,
        "obesity_level": "Normal_Weight",
        "confidence": 0.98,
        "status": "success"
      }
    ]
  }
}
```

---

## Rate Limiting

**Current:** No rate limiting (development)  
**Production:** Recommended limits:
- 100 requests per minute per IP
- 1,000 requests per hour per API key

---

## Webhooks (Optional)

Enable asynchronous notifications:

```python
@app.post("/subscribe")
async def subscribe_to_updates(webhook_url: str):
    # Subscribe to prediction updates
    return {"webhook_id": "wh_123"}
```

---

## Pagination

For endpoints returning lists, use pagination:

```bash
GET /predictions?page=1&limit=50
GET /users?offset=100&count=25
```

---

## Changelog

### v1.0.0
- Initial API release
- `/health`, `/bmi`, `/recommend`, `/similar-users` endpoints
- Full Pydantic validation

### v1.1.0 (Planned)
- Batch processing endpoint
- User authentication with JWT
- Rate limiting
- Webhooks support

