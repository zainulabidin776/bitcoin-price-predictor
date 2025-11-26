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

Edit `.env` file with your credentials:

```bash
# Required: CoinCap API Key
COINCAP_API_KEY=your_api_key_here

# Required: DagHub/MLflow (create free account at dagshub.com)
MLFLOW_TRACKING_URI=https://dagshub.com/YOUR_USERNAME/mlops-rps-crypto.mlflow
MLFLOW_TRACKING_USERNAME=your_dagshub_username
MLFLOW_TRACKING_PASSWORD=your_dagshub_token
```

### Step 3: Start Services

```bash
# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

### Step 4: Access Dashboards

| Service | URL | Credentials |
|---------|-----|-------------|
| **Airflow** | http://localhost:8080 | admin / admin |
| **MinIO** | http://localhost:9001 | minioadmin / minioadmin123 |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin / admin |
| **API** | http://localhost:8000 | - |

### Step 5: Run First Pipeline

1. Go to Airflow UI: http://localhost:8080
2. Find DAG: `crypto_volatility_pipeline`
3. Click "Unpause" to enable it
4. Click "Trigger DAG" to run manually

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
# Check logs
docker-compose logs

# Restart specific service
docker-compose restart airflow-webserver

# Complete restart
docker-compose down
docker-compose up -d
```

### Airflow DAG not appearing
```bash
# Check DAG syntax
python airflow/dags/crypto_pipeline_dag.py

# Restart scheduler
docker-compose restart airflow-scheduler
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
