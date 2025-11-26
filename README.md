# MLOps Real-Time Predictive System (RPS) - Crypto Volatility Prediction

## 🎯 Project Overview

A production-ready MLOps pipeline for predicting Bitcoin (BTC) price volatility using CoinCap API. This system implements:
- Automated data ingestion and quality checks
- Continuous model training and versioning
- CI/CD with automated model comparison
- Real-time monitoring and drift detection

**Predictive Task**: Predict BTC price volatility (1-hour ahead prediction)

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  CoinCap    │────▶│   Airflow    │────▶│   MinIO     │
│    API      │     │     DAG      │     │  (Storage)  │
└─────────────┘     └──────────────┘     └─────────────┘
                           │                      │
                           ▼                      ▼
                    ┌──────────────┐       ┌─────────────┐
                    │    MLflow    │◀──────│     DVC     │
                    │   (Dagshub)  │       │  (Version)  │
                    └──────────────┘       └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   FastAPI    │
                    │   (Docker)   │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐     ┌─────────────┐
                    │  Prometheus  │────▶│   Grafana   │
                    │  (Metrics)   │     │ (Dashboard) │
                    └──────────────┘     └─────────────┘
```

---

## 📋 Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Git
- 8GB RAM minimum
- GitHub account
- DagHub account (free)

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone repository
git clone <your-repo-url>
cd mlops-rps-crypto

# Create virtual environment
conda create -n mlops-rps python=3.9 -y
conda activate mlops-rps

# Install dependencies
pip install -r requirements.txt

# Initialize DVC
dvc init
```

### 2. Configure Environment Variables

Create `.env` file:

```bash
# CoinCap API
COINCAP_API_KEY=bb3aff5cf39fcdb0348872abb812aa2cbaa34c5a9e61e024d6a0573597f753ba

# MinIO (Local S3)
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
MINIO_ENDPOINT=http://localhost:9000

# MLflow (DagHub)
MLFLOW_TRACKING_URI=https://dagshub.com/<your-username>/mlops-rps-crypto.mlflow
MLFLOW_TRACKING_USERNAME=<your-dagshub-username>
MLFLOW_TRACKING_PASSWORD=<your-dagshub-token>

# DVC Remote
DVC_REMOTE_URL=s3://mlops-data
```

### 3. Start Infrastructure

```bash
# Start all services (Airflow, MinIO, Prometheus, Grafana)
docker-compose up -d

# Verify services
docker-compose ps
```

**Access URLs:**
- Airflow: http://localhost:8080 (admin/admin)
- MinIO: http://localhost:9001 (minioadmin/minioadmin123)
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### 4. Setup DVC Remote

```bash
# Configure DVC to use MinIO
dvc remote add -d minio s3://mlops-data
dvc remote modify minio endpointurl http://localhost:9000
dvc remote modify minio access_key_id minioadmin
dvc remote modify minio secret_access_key minioadmin123

# Create bucket in MinIO (via UI or mc client)
```

### 5. Setup DagHub

```bash
# Login to dagshub.com and create new repo: mlops-rps-crypto
# Add remote
git remote add dagshub https://dagshub.com/<your-username>/mlops-rps-crypto.git

# Configure MLflow
export MLFLOW_TRACKING_URI=https://dagshub.com/<your-username>/mlops-rps-crypto.mlflow
export MLFLOW_TRACKING_USERNAME=<your-username>
export MLFLOW_TRACKING_PASSWORD=<your-token>
```

### 6. Run Initial Pipeline

```bash
# Trigger Airflow DAG manually
# Go to http://localhost:8080
# Enable and trigger: crypto_volatility_pipeline

# Or run locally for testing
python src/data/extract.py
python src/data/transform.py
python src/models/train.py
```

---

## 📁 Project Structure

```
mlops-rps-crypto/
├── .github/
│   └── workflows/           # CI/CD pipelines
│       ├── dev-ci.yml       # Dev branch checks
│       ├── test-ci.yml      # Model comparison with CML
│       └── prod-cd.yml      # Production deployment
├── airflow/
│   ├── dags/
│   │   └── crypto_pipeline_dag.py  # Main orchestration DAG
│   ├── logs/
│   └── plugins/
├── src/
│   ├── data/
│   │   ├── extract.py       # API data extraction
│   │   ├── transform.py     # Feature engineering
│   │   └── quality_check.py # Data validation
│   ├── models/
│   │   ├── train.py         # Model training with MLflow
│   │   └── predict.py       # Inference logic
│   └── api/
│       └── app.py           # FastAPI serving endpoint
├── monitoring/
│   ├── prometheus.yml       # Prometheus config
│   └── grafana/
│       └── dashboards/      # Pre-built dashboards
├── tests/
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_model.py
├── data/
│   ├── raw/                 # Raw API data
│   └── processed/           # Transformed datasets
├── models/                  # Trained model artifacts
├── reports/                 # Pandas profiling reports
├── Dockerfile              # API container
├── docker-compose.yml      # All services orchestration
├── requirements.txt        # Python dependencies
├── .dvc/                   # DVC configuration
├── .dvcignore
├── .gitignore
├── .env.example
└── README.md
```

---

## 🔄 Git Workflow (Branching Strategy)

### Branch Structure

```
master (production)
  ↑
test (staging)
  ↑
dev (development)
  ↑
feature/* (individual features)
```

### Development Flow

1. **Create Feature Branch**
```bash
git checkout dev
git pull origin dev
git checkout -b feature/model-improvement
```

2. **Develop and Commit**
```bash
git add .
git commit -m "feat: improve feature engineering"
git push origin feature/model-improvement
```

3. **Pull Request to Dev**
- Create PR: feature/model-improvement → dev
- CI runs: linting + unit tests
- Merge after approval

4. **Pull Request to Test**
- Create PR: dev → test
- CI runs: full pipeline + CML model comparison
- **Automated model comparison report posted in PR**
- Merge only if new model performs better

5. **Pull Request to Master**
- Create PR: test → master
- CD pipeline: builds Docker image, pushes to registry
- Deploy to production

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Lint code
flake8 src/
black src/ --check

# Type checking
mypy src/
```

---

## 📊 Monitoring

### Prometheus Metrics

The FastAPI app exposes:
- `http_requests_total`: Total API requests
- `prediction_latency_seconds`: Inference time
- `data_drift_ratio`: Out-of-distribution features ratio
- `model_prediction_value`: Actual prediction values

### Grafana Dashboards

1. **Model Performance Dashboard**
   - Prediction latency trends
   - Request rate
   - Error rates

2. **Data Drift Dashboard**
   - Feature distribution changes
   - OOD detection alerts

3. **System Health Dashboard**
   - Container resource usage
   - API uptime

### Alerts

Configured alerts:
- Inference latency > 500ms
- Data drift ratio > 0.15
- API error rate > 5%

---

## 🐳 Docker Deployment

### Build Image

```bash
# Build API container
docker build -t crypto-predictor:v1.0.0 .

# Test locally
docker run -p 8000:8000 \
  -e MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI \
  crypto-predictor:v1.0.0
```

### Push to Registry

```bash
# Tag image
docker tag crypto-predictor:v1.0.0 <dockerhub-username>/crypto-predictor:v1.0.0

# Push
docker push <dockerhub-username>/crypto-predictor:v1.0.0
```

### Health Check

```bash
# Check API health
curl http://localhost:8000/health

# Test prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [0.5, 0.3, 0.8, 0.2, 0.6]}'
```

---

## 📈 Model Performance

### Baseline Metrics

- **RMSE**: < 0.05 (on normalized data)
- **MAE**: < 0.03
- **R²**: > 0.75
- **Inference Time**: < 100ms

### Feature Engineering

1. **Price Features**
   - Price change % (1h, 4h, 24h)
   - Price momentum indicators

2. **Volume Features**
   - Volume moving averages
   - Volume change %

3. **Volatility Features**
   - Rolling standard deviation
   - High-Low range %

4. **Temporal Features**
   - Hour of day (cyclical encoding)
   - Day of week
   - Weekend indicator

---

## 🔧 Troubleshooting

### Common Issues

1. **Airflow DAG not showing**
   - Check logs: `docker-compose logs airflow-webserver`
   - Verify DAG syntax: `python airflow/dags/crypto_pipeline_dag.py`

2. **MLflow connection fails**
   - Verify DagHub credentials in `.env`
   - Check network connectivity

3. **DVC push fails**
   - Ensure MinIO is running
   - Verify bucket exists
   - Check credentials

4. **API returns 500 error**
   - Check model is loaded: view logs
   - Verify input feature format
   - Ensure MLflow model exists

### Logs

```bash
# Airflow logs
docker-compose logs airflow-scheduler

# API logs
docker-compose logs api

# Prometheus logs
docker-compose logs prometheus
```

---

## 📚 Additional Resources

- [CoinCap API Docs](https://docs.coincap.io/)
- [Apache Airflow Docs](https://airflow.apache.org/docs/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [DVC Documentation](https://dvc.org/doc)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 👥 Team Members

- [Member 1]
- [Member 2]
- [Member 3]

---

## 📝 License

MIT License

---

## 🎓 Submission Checklist

- [ ] All 4 phases implemented
- [ ] Airflow DAG running successfully
- [ ] DVC data versioning configured
- [ ] MLflow experiments tracked on DagHub
- [ ] GitHub Actions CI/CD pipelines working
- [ ] CML model comparison in PRs
- [ ] Docker image built and pushed
- [ ] Prometheus + Grafana monitoring active
- [ ] Complete documentation
- [ ] Demo video recorded

---

**Project Deadline**: November 30, 2025
