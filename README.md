# MLOps Real-Time Predictive System (RPS) - Crypto Volatility Prediction

## 🎯 Project Overview

A production-ready MLOps pipeline for predicting Bitcoin (BTC) price volatility using CryptoCompare API (free tier). This system implements:
- Automated data ingestion and quality checks
- Continuous model training and versioning
- CI/CD with automated model comparison
- Real-time monitoring and drift detection

**Predictive Task**: Predict BTC price volatility (1-hour ahead prediction)

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ CryptoCompare│────▶│   Airflow    │────▶│   MinIO     │
│    API       │     │     DAG      │     │  (Storage)  │
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
cd Bitcoin-MLOPS

# Create virtual environment (optional, for local development)
conda create -n mlops-crypto python=3.9 -y
conda activate mlops-crypto

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` file in the project root:

```bash
# CryptoCompare API (Free - No key required)
DATA_SOURCE=cryptocompare
CRYPTO_ASSET=BTC
CRYPTO_CURRENCY=USD

# MLflow (DagHub)
MLFLOW_TRACKING_URI=https://dagshub.com/zainulabidin776/bitcoin-price-predictor.mlflow
MLFLOW_TRACKING_USERNAME=zainulabidin776
MLFLOW_TRACKING_PASSWORD=4844315bd4005fdc92de947532a3ed2347d0028e

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET=mlops-data
MINIO_SECURE=false

# Airflow Configuration
AIRFLOW_HOME=/opt/airflow
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
AIRFLOW__CORE__FERNET_KEY=81HqDtbqAywKSOumSha3BhWNOdQ26slT6K0YaZeZyPs=
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__WEBSERVER__SECRET_KEY=z8kF2mN9pQ4rT7vX3cB6eH1jL5wY0aD8

# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Model Configuration
MODEL_NAME=crypto-volatility-predictor
MODEL_STAGE=Production
```

### 3. Start Infrastructure with Docker Compose

```bash
# Navigate to project directory
cd Bitcoin-MLOPS

# Start all services (PostgreSQL, Airflow, MinIO, Prometheus, Grafana, FastAPI)
docker compose up --build

# Or run in detached mode
docker compose up -d

# Verify all services are running
docker compose ps
```

**Wait 2-3 minutes** for all services to initialize, especially Airflow init.

**Access URLs:**
- **Airflow**: http://localhost:8081 (admin/admin) - *Note: Port 8081 if 8080 is in use*
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin123)
- **MinIO API**: http://localhost:9000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **FastAPI**: http://localhost:8000/docs

### 4. Verify Services Are Running

```bash
# Check all containers are healthy
docker compose ps

# Expected output: All services should show "Up" status
# - postgres-1: Up (healthy)
# - airflow-webserver-1: Up
# - airflow-scheduler-1: Up
# - airflow-init-1: Exited (0) - This is normal, init runs once
# - minio-1: Up
# - prometheus-1: Up
# - grafana-1: Up
# - api-1: Up

# Check logs if any service fails
docker compose logs <service-name>
```

### 5. Access Airflow UI and Enable DAG

1. **Open Airflow UI**: http://localhost:8081 (or http://localhost:8080 if port 8080 is free)
2. **Login**: Username: `admin`, Password: `admin`
3. **Find DAG**: Look for `crypto_pipeline_dag` in the DAGs list
4. **Enable DAG**: Toggle the switch to ON (blue)
5. **Trigger DAG**: Click the "Play" button to run manually

### 6. Test the Pipeline Locally (Optional)

```bash
# Activate conda environment
conda activate mlops-crypto

# Run data extraction (uses CryptoCompare API - free, no key needed)
python src/data/extract.py

# Run quality checks
python src/data/quality_check.py

# Transform features
python src/data/transform.py

# Train model
python src/models/train.py
```

### 7. Setup DVC Remote (Optional)

```bash
# Initialize DVC (if not already done)
dvc init

# Configure DVC to use MinIO
dvc remote add -d minio s3://mlops-data
dvc remote modify minio endpointurl http://localhost:9000
dvc remote modify minio access_key_id minioadmin
dvc remote modify minio secret_access_key minioadmin123

# Create bucket in MinIO via UI: http://localhost:9001
# Login: minioadmin/minioadmin123
# Create bucket: mlops-data
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

1. **Airflow webserver won't start - Port 8080 already in use**
   ```bash
   # Check what's using port 8080
   netstat -ano | findstr :8080
   
   # Solution: Port is already mapped to 8081 in docker-compose.yml
   # Access Airflow at: http://localhost:8081
   # Or change the port mapping in docker-compose.yml if needed
   ```

2. **Airflow init container fails**
   ```bash
   # Check init logs
   docker compose logs airflow-init
   
   # Common issue: _PIP_ADDITIONAL_REQUIREMENTS causing pip install failures
   # Solution: Already fixed - _PIP_ADDITIONAL_REQUIREMENTS is commented out
   # If you need those packages, build a custom Airflow image instead
   ```

3. **Airflow DAG not showing**
   ```bash
   # Check scheduler logs
   docker compose logs airflow-scheduler
   
   # Verify DAG file exists
   ls airflow/dags/crypto_pipeline_dag.py
   
   # Restart scheduler
   docker compose restart airflow-scheduler
   ```

4. **MLflow connection fails**
   ```bash
   # Verify DagHub credentials in .env file
   # Test connection
   python -c "import mlflow; mlflow.set_tracking_uri('https://dagshub.com/zainulabidin776/bitcoin-price-predictor.mlflow'); print('Connected')"
   ```

5. **DVC push fails**
   ```bash
   # Ensure MinIO is running
   docker compose ps minio
   
   # Verify bucket exists via MinIO UI: http://localhost:9001
   # Check credentials in .env
   ```

6. **API returns 500 error or "No model found"**
   ```bash
   # Check API logs
   docker compose logs api
   
   # This is expected if no model has been trained yet
   # Train a model first via Airflow DAG or locally
   python src/models/train.py
   ```

7. **Services won't start**
   ```bash
   # Stop all services
   docker compose down
   
   # Remove volumes (WARNING: deletes data)
   docker compose down -v
   
   # Start fresh
   docker compose up --build
   ```

### Viewing Logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs airflow-scheduler
docker compose logs airflow-webserver
docker compose logs api
docker compose logs postgres

# Follow logs in real-time
docker compose logs -f airflow-scheduler
```

---

## 📚 Additional Resources

- [CryptoCompare API Docs](https://min-api.cryptocompare.com/documentation)
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
