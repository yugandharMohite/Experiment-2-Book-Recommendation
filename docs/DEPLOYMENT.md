# Deployment Guide

This guide covers production deployment strategies for the Nutrition Recommendation System.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Platforms](#cloud-platforms)
5. [Security](#security)
6. [Monitoring & Logging](#monitoring--logging)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- Docker & Docker Compose
- Python 3.12+
- Git
- 2GB+ RAM
- 5GB+ storage

### Optional
- AWS/Azure/GCP account
- Kubernetes cluster
- Load balancer (Nginx, HAProxy)

---

## Local Development

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/nutrition-recommender.git
cd nutrition-recommender
```

### 2. Set Up Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your local settings
```

### 4. Train Model
```bash
python train_and_save_model.py
```

### 5. Run Tests
```bash
pytest tests/ -v --cov=src
```

### 6. Start Development Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit: `http://localhost:8000`

---

## Docker Deployment

### Single Container Deployment

#### 1. Build Image
```bash
docker build -t nutrition-recommender:latest .
```

#### 2. Run Container
```bash
docker run -d \
  --name nutrition-api \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/Data:/app/Data \
  nutrition-recommender:latest
```

#### 3. Verify
```bash
curl http://localhost:8000/health
```

#### 4. View Logs
```bash
docker logs -f nutrition-api
```

#### 5. Stop Container
```bash
docker stop nutrition-api
docker rm nutrition-api
```

---

### Docker Compose Deployment (Recommended for Dev)

#### 1. Start All Services
```bash
docker-compose up -d
```

Services:
- API (`http://localhost:8000`)
- Database (`localhost:5432`)
- Redis (`localhost:6379`)
- MLflow (`http://localhost:5000`)
- Dashboard (`http://localhost:8501`)

#### 2. Check Status
```bash
docker-compose ps
docker-compose logs -f nutrition-api
```

#### 3. Run Tests in Container
```bash
docker-compose exec nutrition-api pytest tests/ -v
```

#### 4. Stop Services
```bash
docker-compose down
docker-compose down -v  # Also remove volumes
```

---

## Cloud Platforms

### AWS EC2 Deployment

#### 1. Launch EC2 Instance
```bash
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.small \
  --key-name your-key \
  --security-group-ids sg-12345678 \
  --iam-instance-profile Name=EC2-Docker-Role
```

#### 2. SSH into Instance
```bash
ssh -i your-key.pem ubuntu@your-instance-public-ip
```

#### 3. Install Dependencies
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
```

#### 4. Deploy Application
```bash
git clone https://github.com/yourusername/nutrition-recommender.git
cd nutrition-recommender
docker-compose up -d
```

#### 5. Configure Security Group
- Allow inbound HTTP (80)
- Allow inbound HTTPS (443)
- Allow inbound SSH (22) from your IP

#### 6. Set Up Nginx Reverse Proxy
```nginx
upstream nutrition_api {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://nutrition_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

### AWS ECS (Containerized Microservices)

#### 1. Create ECR Repository
```bash
aws ecr create-repository --repository-name nutrition-recommender
```

#### 2. Push Image to ECR
```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

docker tag nutrition-recommender:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/nutrition-recommender:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/nutrition-recommender:latest
```

#### 3. Create ECS Task Definition
```json
{
  "containerDefinitions": [
    {
      "name": "nutrition-api",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/nutrition-recommender:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogsAwslogs",
        "options": {
          "awslogs-group": "/ecs/nutrition-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 4. Create ECS Service
```bash
aws ecs create-service \
  --cluster nutrition-cluster \
  --service-name nutrition-api \
  --task-definition nutrition-api:1 \
  --desired-count 2 \
  --launch-type EC2
```

---

### GCP Cloud Run

#### 1. Enable Cloud Run
```bash
gcloud services enable run
```

#### 2. Deploy
```bash
gcloud run deploy nutrition-recommender \
  --source . \
  --platform managed \
  --region us-central1 \
  --memory 1Gi \
  --timeout 600 \
  --set-env-vars "ENVIRONMENT=production"
```

#### 3. Get Service URL
```bash
gcloud run services list
curl https://nutrition-recommender-xyz.run.app/health
```

---

### Kubernetes Deployment

#### 1. Create Namespace
```bash
kubectl create namespace nutrition
```

#### 2. Create Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nutrition-api
  namespace: nutrition
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nutrition-api
  template:
    metadata:
      labels:
        app: nutrition-api
    spec:
      containers:
      - name: api
        image: your-registry/nutrition-recommender:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        env:
        - name: ENVIRONMENT
          value: "production"
```

#### 3. Create Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nutrition-api-service
  namespace: nutrition
spec:
  selector:
    app: nutrition-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

#### 4. Apply Configuration
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl get svc -n nutrition
```

---

## Security

### 1. Environment Variables
```bash
# Never commit secrets!
# Use .env files (in .gitignore)
# Or CI/CD secret management
```

### 2. SSL/TLS Certificates
```bash
# Using Let's Encrypt with Certbot
sudo certbot certonly --standalone -d your-domain.com

# Configure in docker-compose or nginx
```

### 3. Database Security
```bash
# Use strong passwords
# Enable connection encryption
# Restrict network access

# PostgreSQL connection string with SSL:
DATABASE_URL=postgresql://user:password@host:5432/db?sslmode=require
```

### 4. API Authentication (Future)
```python
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from fastapi import Depends, HTTPException

security = HTTPBearer()

@app.post("/recommend")
async def secure_recommend(
    credentials: HTTPAuthCredentials = Depends(security),
    user_data: UserRequest
):
    # Verify JWT token
    token = credentials.credentials
    # Validation logic...
    return get_recommendation(user_data)
```

### 5. Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/recommend")
@limiter.limit("100/minute")
async def limited_recommend(request: Request, user_data: UserRequest):
    return get_recommendation(user_data)
```

---

## Monitoring & Logging

### 1. Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, generate_latest

requests_total = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
request_duration = Histogram('api_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    requests_total.labels(method=request.method, endpoint=request.url.path).inc()
    request_duration.observe(duration)
    return response
```

### 2. Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### 3. Health Checks
```bash
# Docker health check
curl -f http://localhost:8000/health || exit 1

# Kubernetes liveness probe
kubectl logs -n nutrition pod/nutrition-api-xyz
```

### 4. Monitoring Stack (Optional)
```bash
# Prometheus
docker run -d -p 9090:9090 prom/prometheus

# Grafana
docker run -d -p 3000:3000 grafana/grafana

# ELK Stack
docker-compose -f elk-docker-compose.yml up -d
```

---

## Scaling Strategies

### Horizontal Scaling
```bash
# Docker Compose - Scale services
docker-compose up -d --scale nutrition-api=3

# Kubernetes - Scale replicas
kubectl scale deployment nutrition-api --replicas=5 -n nutrition
```

### Load Balancing
```nginx
upstream nutrition_backend {
    server api-1:8000 weight=5;
    server api-2:8000 weight=5;
    server api-3:8000 weight=3;
}

server {
    listen 80;
    location / {
        proxy_pass http://nutrition_backend;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Database Optimization
```bash
# Connection pooling with PgBouncer
pgbouncer.ini:
[databases]
nutrition_db = host=db_server port=5432 dbname=nutrition_db
max_client_conn = 1000
default_pool_size = 25
```

---

## Troubleshooting

### 1. Container Won't Start
```bash
# Check logs
docker logs nutrition-api

# Inspect image
docker history nutrition-recommender:latest

# Run interactively
docker run -it nutrition-recommender:latest /bin/bash
```

### 2. Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Use different port
docker run -p 8001:8000 nutrition-recommender
```

### 3. Model Loading Failure
```bash
# Check model file exists
ls -la models/nutrition_model.pkl

# Verify pickle integrity
python -c "import pickle; pickle.load(open('models/nutrition_model.pkl', 'rb'))"

# Retrain model
docker-compose exec nutrition-api python train_and_save_model.py
```

### 4. Database Connection Issues
```bash
# Test PostgreSQL connection
psql -h localhost -U nutrition_user -d nutrition_db

# Check environment variables
docker-compose exec nutrition-api env | grep DATABASE

# Restart database
docker-compose restart nutrition-db
```

### 5. High Memory Usage
```bash
# Monitor container memory
docker stats nutrition-api

# Limit memory
docker run -m 1g nutrition-recommender

# Profile memory usage
python -m memory_profiler train_and_save_model.py
```

---

## Production Checklist

- [ ] Environment variables configured
- [ ] SSL/TLS certificates installed
- [ ] Database backups configured
- [ ] Monitoring and alerting enabled
- [ ] Logging centralized (ELK/CloudWatch)
- [ ] Rate limiting implemented
- [ ] Auto-scaling policies set
- [ ] Disaster recovery plan documented
- [ ] Load testing completed (target: 1000 req/s)
- [ ] Security audit passed
- [ ] Documentation updated
- [ ] On-call rotation established

---

## Support

For deployment issues:
1. Check logs: `docker logs <container>`
2. Review [Architecture](./ARCHITECTURE.md)
3. Open GitHub issue with details
4. Contact DevOps team

