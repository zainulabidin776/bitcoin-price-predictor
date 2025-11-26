# Quick Start Guide

## ⚡ 5-Minute Setup

### Prerequisites
- Docker & Docker Compose installed
- Python 3.9+ installed
- Git installed
- 8GB RAM available

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd mlops-rps-crypto

# Run automated setup
chmod +x setup.sh
./setup.sh
```

### Step 2: Configure Environment

Create `.env` file in project root with your credentials:

```bash
# CryptoCompare API (Free - No key required)
DATA_SOURCE=cryptocompare
CRYPTO_ASSET=BTC
CRYPTO_CURRENCY=USD

# Required: DagHub/MLflow (create free account at dagshub.com)
MLFLOW_TRACKING_URI=https://dagshub.com/YOUR_USERNAME/bitcoin-price-predictor.mlflow
MLFLOW_TRACKING_USERNAME=your_dagshub_username
MLFLOW_TRACKING_PASSWORD=your_dagshub_token

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET=mlops-data

# Airflow Configuration
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
```

### Step 3: Start Services

```bash
# Navigate to project directory
cd Bitcoin-MLOPS

# Start all services (builds images and starts containers)
docker compose up --build

# Or run in background (detached mode)
docker compose up -d --build

# Wait 2-3 minutes for services to initialize
# Especially wait for airflow-init to complete

# Verify all services are running
docker compose ps
```

**Expected Services:**
- ✅ postgres-1: Up (healthy)
- ✅ airflow-init-1: Exited (0) - Normal, runs once
- ✅ airflow-webserver-1: Up
- ✅ airflow-scheduler-1: Up
- ✅ minio-1: Up
- ✅ prometheus-1: Up
- ✅ grafana-1: Up
- ✅ api-1: Up

### Step 4: Access Dashboards

**Wait 2-3 minutes** after starting services, then access:

| Service | URL | Credentials | What to Check |
|---------|-----|-------------|---------------|
| **Airflow** | http://localhost:8081 | admin / admin | Should show DAGs page |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin123 | Should show buckets |
| **Prometheus** | http://localhost:9090 | - | Should show Prometheus UI |
| **Grafana** | http://localhost:3000 | admin / admin | Should show login page |
| **FastAPI Docs** | http://localhost:8000/docs | - | Should show Swagger UI |
| **FastAPI Health** | http://localhost:8000/health | - | Should return JSON |

**⚠️ Note:** If port 8080 is in use, Airflow uses port 8081 (configured in docker-compose.yml)

### Step 5: Run First Pipeline

1. **Open Airflow UI**: http://localhost:8081 (or http://localhost:8080)
2. **Login**: Username: `admin`, Password: `admin`
3. **Find DAG**: Look for `crypto_pipeline_dag` in the DAGs list
4. **Enable DAG**: Toggle switch from OFF (gray) to ON (blue)
5. **Trigger DAG**: Click the "Play" button (▶️) to run manually
6. **Monitor**: Click on DAG name to see task execution in real-time

**Expected Duration:** 10-15 minutes for full pipeline execution

---

## 🧪 Test the API

```bash
# Check health
curl http://localhost:8000/health

# Make prediction (example)
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [0.05, -0.02, 0.03, 0.01, -0.01, 0.04, 1.002, 0.998, 1.001,
                 0.0001, -0.0002, 0.0003, 0.0004, 0.0005, 0.015, 0.012,
                 0.001, 0.003, 0.002, 0.003, 0.001, 45.5, 0.707, 0.707,
                 -0.434, 0.901, 0, 120.5, 50000, 49800, 49950, 49700, 50100,
                 0.0003, 0.0004, 0.0002]
  }'
```

---

## 📊 View Monitoring

### Prometheus Metrics
http://localhost:9090

Query examples:
- `http_requests_total` - Total API requests
- `prediction_latency_seconds` - Prediction latency
- `data_drift_ratio` - Data drift detection

### Grafana Dashboards
http://localhost:3000

1. Login (admin/admin)
2. Navigate to Dashboards
3. Import dashboard from `monitoring/grafana/dashboards/`

---

## 🔄 Development Workflow

### Create a Feature

```bash
# Switch to dev branch
git checkout dev

# Create feature branch
git checkout -b feature/my-improvement

# Make changes and test
# ... edit code ...

# Commit and push
git add .
git commit -m "feat: describe your change"
git push origin feature/my-improvement
```

### Pull Request Workflow

1. **feature → dev**: Triggers linting + unit tests
2. **dev → test**: Triggers full pipeline + CML model comparison
3. **test → master**: Triggers Docker build + deployment

---

## 🐛 Troubleshooting

### Services won't start
```bash
# Check logs for errors
docker compose logs

# Check specific service
docker compose logs airflow-init
docker compose logs airflow-webserver

# Restart specific service
docker compose restart airflow-webserver

# Complete restart
docker compose down
docker compose up --build
```

### Airflow init fails
```bash
# Check init logs
docker compose logs airflow-init

# Common issue: Already fixed - _PIP_ADDITIONAL_REQUIREMENTS is commented out
# If you see pip install errors, the fix is already in docker-compose.yml
```

### Airflow webserver port conflict
```bash
# Port 8080 already in use - Solution: Use port 8081
# Access at: http://localhost:8081
# Or change port in docker-compose.yml line 67
```

### Airflow DAG not appearing
```bash
# Check scheduler logs
docker compose logs airflow-scheduler

# Verify DAG file exists
dir airflow\dags\crypto_pipeline_dag.py

# Check DAG syntax (if Python is available)
python airflow\dags\crypto_pipeline_dag.py

# Restart scheduler
docker compose restart airflow-scheduler

# Wait 30 seconds, refresh Airflow UI
```

### API returns 503
```bash
# Check if model is loaded
curl http://localhost:8000/model/info

# Check API logs
docker-compose logs api
```

### DVC push fails
```bash
# Check MinIO is running
curl http://localhost:9000/minio/health/live

# Reconfigure DVC remote
dvc remote modify minio endpointurl http://localhost:9000
dvc remote modify minio access_key_id minioadmin
dvc remote modify minio secret_access_key minioadmin123
```

---

## 📚 Next Steps

1. **Configure DagHub**
   - Create account at dagshub.com
   - Create new repository
   - Update `.env` with your DagHub credentials

2. **Setup GitHub Actions**
   - Go to repository Settings → Secrets
   - Add all required secrets (see README.md)

3. **Customize Model**
   - Edit `src/models/train.py` for different algorithms
   - Modify `src/data/transform.py` for new features
   - Adjust hyperparameters in Airflow DAG

4. **Scale Up**
   - Increase Airflow workers
   - Add more API replicas
   - Configure external database for Airflow

---

## 🆘 Get Help

- **Documentation**: See `README.md` for detailed docs
- **Logs**: Check `airflow/logs/` and `docker-compose logs`
- **Issues**: Open an issue on GitHub

---

## 🎯 Project Structure

```
mlops-rps-crypto/
├── src/
│   ├── data/          # ETL pipeline
│   ├── models/        # Training code
│   └── api/           # FastAPI service
├── airflow/
│   └── dags/          # Orchestration
├── monitoring/        # Prometheus & Grafana
├── tests/             # Unit tests
├── .github/
│   └── workflows/     # CI/CD pipelines
└── docker-compose.yml # Service orchestration
```

---

**Ready to go! 🚀**
