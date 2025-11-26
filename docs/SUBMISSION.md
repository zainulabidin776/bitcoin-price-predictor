# MLOps RPS Project - Submission Documentation

## 📋 Project Completion Checklist

### Phase I: Problem Definition and Data Ingestion ✅

- [x] **Problem Selected**: Cryptocurrency Volatility Prediction
  - Domain: Financial
  - API: CryptoCompare API (Free, No key required, 100K calls/month)
  - Task: Predict BTC volatility 1 hour ahead
  - File: `src/data/extract.py`

- [x] **Apache Airflow DAG Implementation**
  - File: `airflow/dags/crypto_pipeline_dag.py`
  - Schedule: Every 6 hours
  - Extraction: Python operator connects to CryptoCompare API
  - Raw data saved with timestamp in `data/raw/`

- [x] **Mandatory Quality Gate**
  - File: `src/data/quality_check.py`
  - Checks: Null values (<1%), schema validation, data ranges, freshness, duplicates
  - **Pipeline fails if quality checks fail**
  - Reports saved to `reports/quality/`

- [x] **Data Transformation**
  - File: `src/data/transform.py`
  - Features: 36 engineered features (price, volatility, momentum, temporal)
  - Lag features for time-series
  - Clean and normalized data

- [x] **Documentation Artifact**
  - Pandas Profiling reports generated
  - Logged to MLflow as artifacts
  - Saved in `reports/profiling/`

- [x] **Data Versioning with DVC**
  - DVC initialized
  - Configured for MinIO (S3-compatible) storage
  - `.dvc` files tracked in Git
  - Data pushed to remote storage

### Phase II: Experimentation and Model Management ✅

- [x] **MLflow Integration**
  - File: `src/models/train.py`
  - All experiments tracked with MLflow
  - Hyperparameters logged
  - Metrics logged: RMSE, MAE, R², MAPE
  - Model artifacts saved

- [x] **DagHub as Central Hub**
  - Configuration in `.env`
  - Links Code (Git), Data (DVC), and Models (MLflow)
  - Centralized experiment tracking
  - Model registry for production models

- [x] **Model Selection**
  - Algorithm: XGBoost Regressor
  - Target: Normalized volatility (1h ahead)
  - Train/Val/Test split with time-series awareness
  - Feature importance tracked

### Phase III: Continuous Integration & Deployment ✅

- [x] **Git Workflow**
  - Strict branching: `dev` → `test` → `master`
  - File: `.github/workflows/dev-ci.yml`
  - File: `.github/workflows/test-ci.yml`
  - File: `.github/workflows/prod-cd.yml`

- [x] **GitHub Actions CI/CD**

  **Dev Branch** (`dev-ci.yml`):
  - Code formatting (Black)
  - Import sorting (isort)
  - Linting (Flake8)
  - Type checking (MyPy)
  - Unit tests (pytest)
  - Security scanning (Bandit, Safety)

  **Test Branch** (`test-ci.yml`):
  - Full pipeline execution
  - Model training
  - **CML Model Comparison**: Automated report in PR
  - Comparison with production baseline
  - **Merge blocked if model worse**

  **Master Branch** (`prod-cd.yml`):
  - Docker image build
  - Container testing
  - Push to Docker registry
  - Automated versioning
  - GitHub release creation

- [x] **Mandatory PR Approvals**
  - Enforced through GitHub branch protection
  - At least 1 reviewer required

- [x] **Dockerization**
  - File: `Dockerfile`
  - FastAPI service containerized
  - Health checks implemented
  - Multi-stage build for optimization

- [x] **Container Registry**
  - Docker Hub integration
  - Automated tagging (version + commit SHA)
  - Latest tag maintained
  - Deployment manifest generated

### Phase IV: Monitoring and Observability ✅

- [x] **Prometheus Integration**
  - File: `monitoring/prometheus.yml`
  - File: `src/api/app.py` (metrics embedded)
  - Metrics collected:
    - `http_requests_total`: API request count
    - `prediction_latency_seconds`: Inference time
    - `data_drift_ratio`: OOD feature ratio
    - `model_prediction_value`: Prediction values
    - `feature_ood_total`: Per-feature drift

- [x] **Grafana Dashboards**
  - File: `monitoring/grafana/dashboards/model-monitoring.json`
  - Visualizations:
    - API request rate
    - Prediction latency (P95)
    - Data drift ratio
    - Model predictions
    - HTTP status distribution
    - OOD features

- [x] **Alerting**
  - Latency alert: >500ms
  - Drift alert: ratio >0.15
  - Configured in Grafana
  - Can integrate with Slack/email

---

## 🏗️ Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ CryptoCompare│────▶│   Airflow    │────▶│   MinIO     │
│    API      │     │     DAG      │     │  (DVC)      │
└─────────────┘     └──────────────┘     └─────────────┘
                           │                      │
                           ▼                      ▼
                    ┌──────────────┐       ┌─────────────┐
                    │    MLflow    │◀──────│   DagHub    │
                    │  (Tracking)  │       │   (Remote)  │
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

## 📊 Tool Integration Summary

| Category | Tools | Implementation | Purpose |
|----------|-------|----------------|---------|
| **Orchestration** | Apache Airflow | `airflow/dags/crypto_pipeline_dag.py` | Schedule & automate ETL → Training |
| **Data Versioning** | DVC | `.dvc/`, `data/*.dvc` | Version datasets with MinIO storage |
| **Experiment Tracking** | MLflow | `src/models/train.py` | Track experiments, log metrics/models |
| **Central Hub** | DagHub | `.env` config | Unify Git, DVC, MLflow |
| **CI/CD** | GitHub Actions | `.github/workflows/*.yml` | Automated testing & deployment |
| **Model Comparison** | CML | `.github/workflows/test-ci.yml` | Automated model comparison in PRs |
| **Containerization** | Docker | `Dockerfile`, `docker-compose.yml` | Package & deploy API |
| **Monitoring** | Prometheus | `monitoring/prometheus.yml` | Collect service/model metrics |
| **Visualization** | Grafana | `monitoring/grafana/` | Real-time dashboards & alerts |

---

## 🎯 Key Features Implemented

### 1. **Production-Ready Pipeline**
- Fully automated ETL
- Quality gates prevent bad data
- Time-series aware feature engineering
- Robust error handling

### 2. **CI/CD Best Practices**
- Automated code quality checks
- Comprehensive test coverage
- Model performance validation
- Automated deployment

### 3. **Model Governance**
- Experiment tracking
- Model versioning
- Performance comparison
- Approval gates

### 4. **Real-Time Monitoring**
- Service health metrics
- Model performance tracking
- Data drift detection
- Automated alerting

### 5. **Reproducibility**
- Data versioning (DVC)
- Environment management (Docker)
- Experiment tracking (MLflow)
- Complete documentation

---

## 📈 Model Performance

### Baseline Metrics
- **RMSE**: < 0.05 (on normalized volatility)
- **MAE**: < 0.03
- **R²**: > 0.75
- **Inference Time**: < 100ms

### Feature Engineering
- **36 features** total
- Price-based: Returns, moving averages, MACD
- Volatility: Rolling std, coefficient of variation
- Momentum: ROC, RSI, acceleration
- Temporal: Cyclical encoding, lag features

---

## 🚀 Deployment Instructions

### Quick Deploy

```bash
# 1. Clone repository
git clone <repo-url>
cd mlops-rps-crypto

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Run setup
chmod +x setup.sh
./setup.sh

# 4. Access services
# Airflow: http://localhost:8081 (or 8080 if port is free)
# API: http://localhost:8000
# Grafana: http://localhost:3000
```

### Production Deploy

```bash
# Pull latest image
docker pull <dockerhub-username>/crypto-predictor:latest

# Run container
docker run -d -p 8000:8000 \
  -e MLFLOW_TRACKING_URI=<uri> \
  -e MODEL_STAGE=Production \
  <dockerhub-username>/crypto-predictor:latest

# Verify
curl http://localhost:8000/health
```

---

## 📚 Documentation

- **README.md**: Complete project documentation
- **QUICKSTART.md**: 5-minute setup guide
- **This file**: Submission documentation
- **Code comments**: Extensive inline documentation
- **Type hints**: Throughout codebase

---

## ✅ Verification

To verify the project meets all requirements:

1. **Data Pipeline**
   ```bash
   # Check Airflow DAG
   python airflow/dags/crypto_pipeline_dag.py  # Should run without errors
   
   # Run quality checks
   python src/data/quality_check.py  # Should pass or fail appropriately
   ```

2. **Model Training**
   ```bash
   # Train model
   python src/models/train.py  # Should log to MLflow
   ```

3. **API Service**
   ```bash
   # Test API
   curl http://localhost:8000/health  # Should return 200
   curl http://localhost:8000/metrics  # Should return Prometheus metrics
   ```

4. **CI/CD**
   - Push to dev → Triggers dev-ci.yml
   - PR to test → Triggers test-ci.yml with CML
   - Merge to master → Triggers prod-cd.yml

5. **Monitoring**
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000
   - Check dashboards and alerts

---

## 🎓 Learning Outcomes Demonstrated

1. ✅ **Data Engineering**: ETL pipeline with quality checks
2. ✅ **Feature Engineering**: Time-series feature creation
3. ✅ **ML Experimentation**: Systematic tracking with MLflow
4. ✅ **Model Deployment**: Containerized REST API
5. ✅ **CI/CD**: Automated testing and deployment
6. ✅ **Monitoring**: Real-time metrics and alerting
7. ✅ **Version Control**: Git + DVC + MLflow
8. ✅ **Orchestration**: Airflow DAG management
9. ✅ **Production Readiness**: Error handling, logging, documentation

---

## 🏆 Project Highlights

- **Zero-dependency API**: CryptoCompare API requires no authentication (free tier)
- **Automated Quality Gates**: Pipeline fails fast on data issues
- **Model Governance**: CML ensures only better models are deployed
- **Complete Monitoring**: From data drift to API latency
- **Production-Ready**: Docker, health checks, error handling
- **Well-Documented**: README, QUICKSTART, inline comments
- **Test Coverage**: Unit tests for critical components
- **Scalable**: Can easily add more models or features

---

## 📞 Support

For questions or issues:
1. Check documentation in `README.md` and `QUICKSTART.md`
2. Review logs: `docker-compose logs <service>`
3. Check Airflow logs: `airflow/logs/`
4. Open GitHub issue

---

**Project Status**: ✅ COMPLETE AND READY FOR SUBMISSION

**Submitted by**: [Your Team Name]  
**Date**: [Submission Date]  
**Project**: MLOps Real-Time Predictive System - Crypto Volatility Prediction
