# MLOps RPS Project - Work Division & Responsibilities

**Project:** Real-Time Predictive System for Cryptocurrency Volatility  
**Team Members:** 
- Zain ul Abidin
- Sanan Azfar  
- Ahmed Javed

**Instructor:** Sir Pir Sami Ullah  
**Deadline:** November 30, 2025

---

## Team Member Responsibilities

### 👤 Zain ul Abidin

**Primary Focus:** Data Pipeline & Orchestration

#### Responsibilities:
1. **Data Extraction & Quality**
   - ✅ Implemented CryptoCompare API integration (`src/data/extract.py`)
   - ✅ Built data quality checker with mandatory gates (`src/data/quality_check.py`)
   - ✅ Fixed column name compatibility issues (timestamp/date, close/priceUsd)

2. **Airflow Orchestration**
   - ✅ Designed and implemented main DAG (`airflow/dags/crypto_pipeline_dag.py`)
   - ✅ Configured task dependencies and XCom communication
   - ✅ Set up Airflow Docker environment with custom packages

3. **Infrastructure Setup**
   - ✅ Docker Compose configuration for all services
   - ✅ Airflow custom Dockerfile with package dependencies
   - ✅ Environment variable management

4. **Documentation**
   - ✅ Setup guides and troubleshooting documentation
   - ✅ API integration documentation

**Key Deliverables:**
- `src/data/extract.py` (273 lines)
- `src/data/quality_check.py` (150+ lines)
- `airflow/dags/crypto_pipeline_dag.py` (283 lines)
- `Dockerfile.airflow` (30 lines)
- `docker-compose.yml` (217 lines)

**Time Investment:** ~40 hours

---

### 👤 Sanan Azfar

**Primary Focus:** Model Development & MLflow Integration

#### Responsibilities:
1. **Feature Engineering**
   - ✅ Implemented comprehensive feature engineering (`src/data/transform.py`)
   - ✅ Created 36 features (price, volatility, momentum, temporal)
   - ✅ Target variable creation for volatility prediction

2. **Model Training**
   - ✅ XGBoost model implementation (`src/models/train.py`)
   - ✅ Train/validation/test split with time-series awareness
   - ✅ Hyperparameter configuration

3. **MLflow & DagHub Integration**
   - ✅ MLflow experiment tracking setup
   - ✅ DagHub automatic initialization
   - ✅ Model artifact logging (model, scaler, features)
   - ✅ Metrics logging (RMSE, MAE, R², MAPE)

4. **Model Configuration Script**
   - ✅ Created `scripts/configure_mlflow_dagshub.py`
   - ✅ Automated DagHub setup and testing

**Key Deliverables:**
- `src/data/transform.py` (344 lines)
- `src/models/train.py` (452 lines)
- `scripts/configure_mlflow_dagshub.py` (200+ lines)
- MLflow experiment tracking configuration

**Time Investment:** ~35 hours

---

### 👤 Ahmed Javed

**Primary Focus:** API Development, Monitoring & CI/CD

#### Responsibilities:
1. **FastAPI Application**
   - ✅ REST API implementation (`src/api/app.py`)
   - ✅ Model serving endpoint (`/predict`)
   - ✅ Health check endpoint (`/health`)
   - ✅ Drift detection implementation

2. **Prometheus Integration**
   - ✅ Metrics collection (latency, requests, drift)
   - ✅ Prometheus client integration
   - ✅ Metrics endpoint (`/metrics`)

3. **CI/CD Pipelines**
   - ✅ GitHub Actions workflows (dev, test, master)
   - ✅ CML integration for model comparison
   - ✅ Docker image build and deployment
   - ✅ Automated testing in CI

4. **Docker & Deployment**
   - ✅ API Dockerfile
   - ✅ Production deployment configuration
   - ✅ Health check implementation

**Key Deliverables:**
- `src/api/app.py` (415 lines)
- `Dockerfile` (41 lines)
- `.github/workflows/dev-ci.yml`
- `.github/workflows/test-ci.yml`
- `.github/workflows/prod-cd.yml`
- `monitoring/prometheus.yml`

**Time Investment:** ~38 hours

---

## Shared Responsibilities

### All Team Members

1. **Code Review**
   - Review each other's pull requests
   - Ensure code quality standards
   - Verify requirements compliance

2. **Testing**
   - Test pipeline end-to-end
   - Verify all services work together
   - Test error scenarios

3. **Documentation**
   - Contribute to README
   - Update documentation as needed
   - Create user guides

4. **Troubleshooting**
   - Debug issues together
   - Share knowledge and solutions
   - Support each other

---

## Remaining Tasks & Assignment

### High Priority Tasks

#### 1. Grafana Dashboard Configuration (Ahmed Javed)
**Estimated Time:** 2-3 hours

**Tasks:**
- [ ] Connect Prometheus as data source in Grafana
- [ ] Create monitoring dashboard with:
  - API request rate
  - Prediction latency
  - Data drift ratio
  - Error rates
- [ ] Configure alert rules:
  - Latency > 500ms
  - Data drift ratio > 0.15
- [ ] Test alerts

**Resources:**
- Grafana UI: http://localhost:3000
- Prometheus: http://localhost:9090
- See: `docs/GRAFANA_SETUP_GUIDE.md`

---

#### 2. DVC Integration Completion (Zain ul Abidin)
**Estimated Time:** 1-2 hours

**Tasks:**
- [ ] Complete `version_with_dvc()` task in DAG
- [ ] Test DVC push to MinIO
- [ ] Verify .dvc files are tracked in Git
- [ ] Document DVC workflow

**Resources:**
- MinIO Console: http://localhost:9001
- See: `docs/DVC_SETUP_GUIDE.md`

---

#### 3. DagHub DVC Remote (Sanan Azfar)
**Estimated Time:** 30 minutes

**Tasks:**
- [ ] Configure DVC to use DagHub as remote storage
- [ ] Test data versioning with DagHub
- [ ] Update documentation

**Resources:**
- DagHub: https://dagshub.com/zainulabidin776/bitcoin-price-predictor
- See: DagHub DVC documentation

---

### Medium Priority Tasks

#### 4. GitHub Branch Protection (Ahmed Javed)
**Estimated Time:** 15 minutes

**Tasks:**
- [ ] Configure branch protection rules
- [ ] Require PR approvals for test and master branches
- [ ] Verify CI/CD still works

---

#### 5. Final Documentation Review (All)
**Estimated Time:** 1 hour

**Tasks:**
- [ ] Review all documentation
- [ ] Ensure consistency
- [ ] Add any missing information
- [ ] Create final submission document

---

## Work Distribution Summary

| Team Member | Primary Focus | Lines of Code | Time Invested | Remaining Tasks |
|------------|--------------|---------------|---------------|-----------------|
| **Zain ul Abidin** | Data Pipeline | ~1,200 | ~40 hours | DVC integration (2h) |
| **Sanan Azfar** | Model & MLflow | ~1,000 | ~35 hours | DagHub DVC (30m) |
| **Ahmed Javed** | API & CI/CD | ~1,500 | ~38 hours | Grafana (3h), Branch protection (15m) |

**Total Code:** ~3,700 lines  
**Total Time:** ~113 hours  
**Remaining:** ~6 hours

---

## Collaboration Tools

1. **GitHub Repository**
   - Code repository
   - Issue tracking
   - Pull request reviews

2. **DagHub**
   - MLflow experiments
   - Model registry
   - Data versioning (DVC)

3. **Docker Compose**
   - Local development environment
   - Service orchestration

4. **Communication**
   - Regular sync meetings
   - Code review sessions
   - Documentation updates

---

## Quality Standards

### Code Quality
- ✅ Type hints throughout
- ✅ Error handling
- ✅ Logging
- ✅ Documentation strings

### Testing
- ✅ Unit tests for critical components
- ✅ Integration tests in CI
- ✅ End-to-end pipeline testing

### Documentation
- ✅ README with setup instructions
- ✅ Code comments
- ✅ Architecture diagrams
- ✅ Troubleshooting guides

---

## Timeline

| Date | Milestone | Owner |
|------|-----------|-------|
| Nov 26 | Current Status | All |
| Nov 27 | Grafana Setup | Ahmed |
| Nov 28 | DVC Integration | Zain |
| Nov 29 | DagHub DVC | Sanan |
| Nov 29 | Final Review | All |
| Nov 30 | Submission | All |

---

## Success Metrics

✅ **Code Quality:** All code reviewed and approved  
✅ **Functionality:** All requirements met  
✅ **Documentation:** Comprehensive and clear  
✅ **Testing:** All tests passing  
✅ **Deployment:** Production-ready

---

*Last Updated: November 26, 2025*

