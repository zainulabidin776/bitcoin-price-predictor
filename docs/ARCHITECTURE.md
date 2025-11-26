# MLOps RPS Architecture Diagram

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     MLOps Real-Time Predictive System                          ║
║                   Cryptocurrency Volatility Prediction                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│  DATA INGESTION LAYER                                                        │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │ CryptoCompare│  ◄─── Live cryptocurrency market data
    │     API     │       (BTC price, volume, market data)
    │  (Real-time)│
    └──────┬──────┘
           │
           │ Every 6 hours (scheduled)
           ▼
    ┌──────────────┐
    │   Airflow    │ ◄─── Orchestration & Scheduling
    │     DAG      │      - Extract data
    └──────┬───────┘      - Quality check (MANDATORY GATE)
           │              - Transform & feature engineering
           │              - Train model
           ▼              - Version with DVC
    ┌──────────────────┐
    │  Quality Check   │ ◄─── FAIL PIPELINE IF BAD DATA
    │   (Mandatory)    │      - Null checks (<1%)
    └──────┬───────────┘      - Schema validation
           │                  - Range checks
           │ ✓ PASS           - Freshness checks
           ▼
┌──────────────────┐
│ Feature Engineer │ ◄─── 36 Time-Series Features
│  Transform.py    │      - Price features (returns, MA, MACD)
└──────┬───────────┘      - Volatility features (std, CV)
       │                  - Momentum (ROC, RSI)
       │                  - Temporal (cyclical encoding)
       ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│  DATA STORAGE & VERSIONING                                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐           ┌──────────────┐
    │    MinIO     │◄──────────│     DVC      │
    │ (S3 Storage) │           │ (Versioning) │
    └──────────────┘           └──────────────┘
         │                            │
         │ Raw & Processed Data       │ .dvc metadata
         │                            │
         └────────────┬───────────────┘
                      │
                      │ Data versioned & tracked
                      ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│  MODEL TRAINING & EXPERIMENT TRACKING                                        │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   XGBoost    │ ◄─── Model Training
    │   Training   │      - Time-series split
    └──────┬───────┘      - Feature scaling
           │              - Hyperparameter tuning
           │
           │ Log everything
           ▼
    ┌──────────────┐           ┌──────────────┐
    │   MLflow     │◄──────────│   DagHub     │
    │  Tracking    │           │  (Central)   │
    └──────┬───────┘           └──────────────┘
           │                          │
           │ - Experiments            │ Unified:
           │ - Metrics (RMSE, R²)     │ - Code (Git)
           │ - Hyperparameters        │ - Data (DVC)
           │ - Models                 │ - Models (MLflow)
           │ - Artifacts              │
           │
           │ Best model
           ▼
    ┌──────────────┐
    │    Model     │
    │   Registry   │
    └──────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  CI/CD PIPELINE (GitHub Actions)                                             │
└─────────────────────────────────────────────────────────────────────────────┘

    feature/* ──┐
                │ PR
                ▼
    ┌──────────────┐
    │  dev branch  │ ◄─── CI: Linting + Unit Tests
    └──────┬───────┘      - Black (formatting)
           │              - Flake8 (linting)
           │ PR           - MyPy (type checking)
           ▼              - pytest (unit tests)
    ┌──────────────┐
    │ test branch  │ ◄─── CI: Full Pipeline + CML
    └──────┬───────┘      - Train new model
           │              - Compare with baseline
           │ PR           - ⚠️ BLOCK if worse
           ▼              - Post report in PR
    ┌──────────────┐
    │master branch │ ◄─── CD: Build & Deploy
    └──────┬───────┘      - Build Docker image
           │              - Test container
           │              - Push to registry
           │              - Create release
           ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│  MODEL SERVING (Production)                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │    Docker    │
    │  Container   │
    │ ┌──────────┐ │
    │ │ FastAPI  │ │ ◄─── REST API
    │ │   App    │ │      - /predict endpoint
    │ │          │ │      - /health endpoint
    │ │ + Model  │ │      - /metrics endpoint
    │ └──────────┘ │      - Drift detection
    └──────┬───────┘      - Prometheus metrics
           │
           │ Expose metrics
           ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│  MONITORING & OBSERVABILITY                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐           ┌──────────────┐
    │  Prometheus  │◄──────────│   Grafana    │
    │  (Metrics)   │  Query    │ (Dashboard)  │
    └──────┬───────┘           └──────────────┘
           │                          │
           │ Scrape every 10s         │ Visualize
           │                          │
           │ Metrics:                 │ Dashboards:
           │ - http_requests_total    │ - Request rate
           │ - prediction_latency     │ - Latency (P95)
           │ - data_drift_ratio       │ - Drift detection
           │ - model_predictions      │ - Status codes
           │ - feature_ood_total      │ - OOD features
           │                          │
           │                          │ Alerts:
           │                          │ - Latency > 500ms
           │                          │ - Drift > 0.15
           │                          │
           └──────────────────────────┘


╔═══════════════════════════════════════════════════════════════════════════════╗
║  KEY FEATURES                                                                  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  ✅ Real-time data ingestion from CryptoCompare API                           ║
║  ✅ Mandatory quality gates (fails pipeline if bad data)                      ║
║  ✅ Comprehensive feature engineering (36 features)                           ║
║  ✅ Experiment tracking with MLflow & DagHub                                  ║
║  ✅ Data versioning with DVC                                                  ║
║  ✅ CI/CD with GitHub Actions                                                 ║
║  ✅ Automated model comparison with CML                                       ║
║  ✅ Docker containerization                                                   ║
║  ✅ Real-time monitoring with Prometheus & Grafana                            ║
║  ✅ Data drift detection                                                      ║
║  ✅ Automated alerting                                                        ║
║  ✅ Production-ready deployment                                               ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║  TECH STACK                                                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  Orchestration:    Apache Airflow                                             ║
║  ML Framework:     XGBoost, scikit-learn                                      ║
║  Tracking:         MLflow, DagHub                                             ║
║  Versioning:       DVC, Git                                                   ║
║  Storage:          MinIO (S3-compatible)                                      ║
║  API:              FastAPI, uvicorn                                           ║
║  Containerization: Docker, Docker Compose                                     ║
║  CI/CD:            GitHub Actions, CML                                        ║
║  Monitoring:       Prometheus, Grafana                                        ║
║  Testing:          pytest, pytest-cov                                         ║
║  Code Quality:     Black, Flake8, MyPy                                        ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```
