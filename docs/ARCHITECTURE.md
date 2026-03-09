# System Architecture

## High-Level Overview

The Nutrition Recommendation System is built on a modular, scalable architecture combining machine learning, data processing, and web services.

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Interface Layer                       │
│  ┌──────────────────┐  ┌──────────────────────────────────┐ │
│  │   FastAPI Web    │  │  Streamlit Dashboard / HTML      │ │
│  │   Dashboard      │  │  Interactive Visualizations      │ │
│  └────────┬─────────┘  └────┬─────────────────────────────┘ │
└───────────┼──────────────────┼──────────────────────────────┘
            │                  │
┌───────────┼──────────────────┼──────────────────────────────┐
│           ▼                  ▼           API Layer          │
│  ┌──────────────────────────────────┐                       │
│  │  FastAPI Application (main.py)   │                       │
│  │  - Routes & Endpoints            │                       │
│  │  - Input Validation              │                       │
│  │  - Response Formatting           │                       │
│  └────────────────┬─────────────────┘                       │
│                   │                                         │
└───────────────────┼─────────────────────────────────────────┘
                    │
┌───────────────────┼─────────────────────────────────────────┐
│                   ▼              Recommendation Engine      │
│  ┌───────────────────────────────────────┐                  │
│  │  NutritionRecommender Class           │                  │
│  │  ┌─────────────────────────────────┐  │                  │
│  │  │ 1. ML Classifier (70% weight)   │  │                  │
│  │  │    Gradient Boosting Model      │  │                  │
│  │  └─────────────────────────────────┘  │                  │
│  │  ┌─────────────────────────────────┐  │                  │
│  │  │ 2. Collaborative Filtering (20%)│  │                  │
│  │  │    KNN Similarity Search        │  │                  │
│  │  └─────────────────────────────────┘  │                  │
│  │  ┌─────────────────────────────────┐  │                  │
│  │  │ 3. Content-Based (10% weight)   │  │                  │
│  │  │    Rule Engine & Nutrition      │  │                  │
│  │  │    Plan Matching                │  │                  │
│  │  └─────────────────────────────────┘  │                  │
│  └───────────────────────────────────────┘                  │
│                   │                                         │
└───────────────────┼─────────────────────────────────────────┘
                    │
┌───────────────────┼─────────────────────────────────────────┐
│                   ▼         ML Model Layer                  │
│  ┌─────────────────────┐  ┌─────────────────────────────┐   │
│  │  Classifier Models  │  │  Similarity Models          │   │
│  │  ┌───────────────┐  │  │  ┌─────────────────────────┐│   │
│  │  │ Gradient      │  │  │  │ KNN (cosine metric)     ││   │
│  │  │ Boosting      │  │  │  │ Trained on full dataset ││   │
│  │  │ 95.2% CV Acc  │  │  │  │ k=6 neighbors           ││   │
│  │  └───────────────┘  │  │  └─────────────────────────┘│   │
│  │  Random Forest      │  │  Feature Scaling            │   │
│  │  MLP Neural Net     │  │  StandardScaler             │   │
│  │  KNN / LogReg       │  │  Label Encoders             │   │
│  └─────────────────────┘  └─────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                    │
┌───────────────────┼─────────────────────────────────────────┐
│                   ▼           Data Processing Layer         │
│  ┌──────────────────────────────────┐                       │
│  │  UCI Obesity Dataset             │                       │
│  │  - 2,111 records                 │                       │
│  │  - 17 features + target          │                       │
│  └────────┬────────────────┬────────┘                       │
│           │                │                                │
│  ┌────────▼──┐    ┌────────▼──────────┐                    │
│  │ Feature   │    │ Feature           │                    │
│  │ Engineering   │ Scaling &         │                    │
│  │ - BMI calc    │ Encoding          │                    │
│  │ - Activity    │ - Label Encoding  │                    │
│  │ - Diet Score  │ - StandardScaler  │                    │
│  │ - Health Idx  │ - Train/Test Split│                    │
│  └───────────────┘    └────────────────┘                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                    │
┌───────────────────┼─────────────────────────────────────────┐
│                   ▼           External Services             │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐   │
│  │ PostgreSQL   │  │ Redis Cache  │  │ MLflow Tracking│   │
│  │ Database     │  │ (optional)   │  │ (optional)     │   │
│  └──────────────┘  └──────────────┘  └────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. **Web Interface Layer**

#### FastAPI Backend
- Lightweight async web framework
- Auto-generated API documentation (Swagger UI)
- Pydantic request/response validation
- Built-in CORS support
- Health check endpoints

#### Streamlit Dashboard (Optional)
- Interactive web app for data exploration
- Real-time visualizations
- User input forms without coding

### 2. **API Layer**

**Endpoints:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| GET | `/bmi` | Calculate BMI from height/weight |
| POST | `/recommend` | Get personalized nutrition plan |
| GET | `/similar-users` | Find similar user profiles |
| GET | `/profile/{user_id}` | Retrieve user recommendations |

### 3. **Recommendation Engine**

**Hybrid Scoring:**
```
Final Score = (0.7 × ML_Prediction) + (0.2 × Collaborative) + (0.1 × Content)
```

#### Component 1: ML Classifier (70%)
- **Model**: Gradient Boosting Classifier
- **Input**: 19 engineered features
- **Output**: Obesity level (7 classes)
- **Performance**: 94.78% test accuracy
- **Training**: 5-fold CV on 2,111 records

#### Component 2: Collaborative Filtering (20%)
- **Algorithm**: KNN with cosine similarity
- **Purpose**: Find similar users
- **k value**: 6 neighbors
- **Validation**: Similar users' outcomes

#### Component 3: Content-Based (10%)
- **Type**: Rule engine
- **Coverage**: 7 obesity levels
- **Rules**: WHO guidelines + clinical best practices
- **Output**: Nutrition plans + alerts

### 4. **ML Model Layer**

**Model Comparison:**

```
Model              │ CV Accuracy │ Test Acc │ Macro F1 │ Selection
───────────────────┼─────────────┼──────────┼──────────┼──────────
Gradient Boosting  │   95.21%    │  94.78%  │  94.32%  │ ✅ Selected
Random Forest      │   93.87%    │  93.21%  │  92.65%  │
MLP Neural Net     │   92.14%    │  91.56%  │  90.87%  │
KNN Classifier     │   89.43%    │  88.76%  │  87.98%  │
Logistic Regression│   87.65%    │  86.92%  │  85.14%  │
```

**Hyperparameters (Gradient Boosting):**
- n_estimators: 150
- learning_rate: 0.1
- max_depth: 5
- subsample: 0.8
- random_state: 42

### 5. **Data Processing Layer**

**Feature Engineering:**

| Feature | Type | Description |
|---------|------|-------------|
| BMI | Derived | Weight / (Height²) |
| ActivityScore | Derived | FAF × CH2O |
| DietScore | Derived | (FCVC × NCP) - FAVC |
| HealthIndex | Derived | FAF + FCVC + CH2O - TUE |

**Preprocessing Pipeline:**
1. Load raw data (2,111 records)
2. Label encode categoricals (8 features)
3. Calculate derived features (4 features)
4. Standardize all features (StandardScaler)
5. Split: 80% train / 20% test (stratified)

### 6. **External Services**

#### PostgreSQL Database
- User profiles and history
- Recommendation records
- Prediction logs

#### Redis Cache
- Session management
- API response caching
- User preference caching

#### MLflow
- Experiment tracking
- Model versioning
- Metrics comparison

## Data Flow

### Request Flow

```
Client Request
   │
   ▼
FastAPI Endpoint
   │
   ├─► Input Validation (Pydantic)
   │
   ▼
NutritionRecommender
   │
   ├─► Preprocessing (Scaling, Encoding)
   │
   ├─► Prediction
   │   ├─ ML Classification
   │   ├─ KNN Similarity
   │   └─ Content Matching
   │
   ├─► Hybrid Scoring
   │
   ▼
Result Aggregation
   ├─ Obesity Level
   ├─ Nutrition Plan
   ├─ Similar Users
   ├─ Health Alerts
   │
   ▼
JSON Response
   │
   ▼
Client
```

### Training Flow

```
UCI Dataset (2,111 records)
   │
   ▼
EDA & Visualization
   │
   ▼
Data Preprocessing
   ├─ Label Encoding
   ├─ Feature Engineering
   ├─ Standardization
   │
   ▼
Train/Test Split (80/20)
   │
   ▼
Model Training
   ├─ 5-Fold CV for Validation
   ├─ Hyperparameter Tuning
   ├─ Feature Importance
   │
   ▼
Model Evaluation
   ├─ Confusion Matrix
   ├─ Classification Report
   ├─ Performance Metrics
   │
   ▼
Save Artifacts
   ├─ Trained Model (pickle)
   ├─ Scaler
   ├─ Label Encoders
   ├─ Cosine Similarity Matrix
```

## Scaling Considerations

### Horizontal Scaling
- **Load Balancer**: Nginx/HAProxy
- **API Instances**: Multiple FastAPI containers
- **Database**: Read replicas for PostgreSQL
- **Cache**: Redis cluster

### Vertical Scaling
- **GPU Support**: CUDA for model inference
- **Memory**: Optimize feature matrices
- **Storage**: Distributed file systems (S3)

## Security Architecture

```
Internet
   │
   ▼
WAF (Web Application Firewall)
   │
   ▼
Rate Limiter
   │
   ▼
SSL/TLS Encryption
   │
   ▼
API Authentication (JWT)
   │
   ▼
Input Validation
   │
   ▼
Model Inference (Sandboxed)
   │
   ▼
Database
   ├─ Row-Level Security
   ├─ Connection Pooling
   └─ Encrypted Sensitive Data
```

## Performance Optimizations

1. **Caching**: Redis for frequent queries
2. **Batch Processing**: Process multiple users efficiently
3. **Model Optimization**: Quantization for faster inference
4. **Database**: Indexed queries on user_id, obesity_level
5. **Async Processing**: Non-blocking API calls

## Monitoring & Observability

- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry / Jaeger
- **Alerts**: PagerDuty integration

