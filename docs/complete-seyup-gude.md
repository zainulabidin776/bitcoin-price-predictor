# 🚀 COMPLETE PROJECT SETUP - STEP BY STEP GUIDE

## 📋 Prerequisites Checklist

- [x] Windows 10/11
- [x] Conda environment: `mlops-crypto` (Python 3.9)
- [x] Docker Desktop installed
- [x] GitHub account: zainulabidin776
- [x] DagHub account connected
- [x] DockerHub account: itsmezayynn

---

## 🎯 PHASE 1: File Setup (10 minutes)

### Step 1: Copy Updated Files

**Option A: Download from Claude (Recommended)**
1. Download these 3 files from Claude's outputs:
   - `quality_check.py`
   - `.env.production` (rename to `.env`)
   - `setup_windows.bat`

2. Copy to your project:
```
C:\Users\zainy\Downloads\Bitcoin-MLOPS\
├── .env                          ← Rename .env.production to .env
├── setup_windows.bat             ← Copy here
└── src\data\
    └── quality_check.py          ← Replace existing file
```

**Option B: Manual Creation**

Create `.env` file manually in project root:

```bash
cd C:\Users\zainy\Downloads\Bitcoin-MLOPS
notepad .env
```

Paste this content (see .env.production file content above)

### Step 2: Verify Files

```bash
# Check files exist
dir .env
dir setup_windows.bat
dir src\data\quality_check.py
dir src\data\extract.py
```

---

## 🎯 PHASE 2: Automated Setup (Option 1 - Recommended)

### Run Setup Script

```bash
cd C:\Users\zainy\Downloads\Bitcoin-MLOPS
conda activate mlops-crypto
setup_windows.bat
```

**This will automatically:**
1. ✅ Create all directories
2. ✅ Verify environment
3. ✅ Install packages
4. ✅ Extract data (721 records)
5. ✅ Run quality checks
6. ✅ Transform features
7. ✅ Train model
8. ✅ Log to MLflow/DagHub

**Expected Duration:** 5-10 minutes

---

## 🎯 PHASE 2: Manual Setup (Option 2 - If Script Fails)

### Step 1: Activate Environment

```bash
conda activate mlops-crypto
```

### Step 2: Create Directories

```bash
mkdir data\raw data\processed reports\quality reports\profiling models outputs logs
```

### Step 3: Verify Installation

```bash
pip list | findstr "mlflow pandas xgboost"
```

Should show:
```
mlflow           2.15.1
pandas           2.0.3
xgboost          2.0.0
```

### Step 4: Test API

```bash
python -c "import requests; r=requests.get('https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD'); print(f'Bitcoin: ${r.json()[\"USD\"]:,.2f}')"
```

Expected: `Bitcoin: $87,323.96`

### Step 5: Run Data Pipeline

```bash
# 1. Extract data
python src\data\extract.py

# 2. Quality check
python src\data\quality_check.py

# 3. Transform features
python src\data\transform.py

# 4. Train model
python src\models\train.py
```

---

## 🎯 PHASE 3: Docker Setup (20 minutes)

### Step 1: Verify Docker

```bash
docker --version
docker compose version
```

If not installed:
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Install and restart computer
3. Start Docker Desktop
4. Wait for Docker Desktop to fully start (whale icon in system tray)

### Step 2: Prepare Environment File

Ensure `.env` file exists in project root with all required variables (see Phase 1).

### Step 3: Start Services

```bash
cd C:\Users\zainy\Downloads\Bitcoin-MLOPS

# Start all services (this will build images and start containers)
docker compose up --build

# Or run in detached mode (background)
docker compose up -d --build
```

**Services starting:**
- PostgreSQL (Airflow database)
- Airflow Init (runs once to initialize database)
- Airflow Webserver (UI)
- Airflow Scheduler (runs DAGs)
- MinIO (S3-compatible storage)
- Prometheus (metrics collection)
- Grafana (dashboards)
- FastAPI (prediction API)

**⏱️ Wait 2-3 minutes for initialization** - Airflow init takes time to:
- Create database tables
- Set up permissions
- Create admin user

### Step 4: Verify Services Are Running

```bash
# Check status of all services
docker compose ps
```

**Expected Output:**
```
NAME                          STATUS
bitcoin-mlops-postgres-1      Up (healthy)
bitcoin-mlops-airflow-init-1  Exited (0)  ← Normal, runs once
bitcoin-mlops-airflow-webserver-1  Up
bitcoin-mlops-airflow-scheduler-1  Up
bitcoin-mlops-minio-1         Up
bitcoin-mlops-prometheus-1    Up
bitcoin-mlops-grafana-1       Up
bitcoin-mlops-api-1           Up
```

**✅ All services should show "Up" status**

### Step 5: Check Service Logs (If Issues)

```bash
# View logs for specific service
docker compose logs airflow-init
docker compose logs airflow-webserver
docker compose logs airflow-scheduler

# View all logs
docker compose logs

# Follow logs in real-time
docker compose logs -f
```

**Key things to check:**
- `airflow-init-1` should show: `exited with code 0` (success)
- `airflow-webserver-1` should show: `Listening at: http://0.0.0.0:8080`
- `airflow-scheduler-1` should show: `Starting the scheduler`

### Step 6: Access UIs

Open browser and test each service:

| Service | URL | Credentials | Status Check |
|---------|-----|-------------|--------------|
| **Airflow** | http://localhost:8081 | admin/admin | Should show DAGs page |
| **Grafana** | http://localhost:3000 | admin/admin | Should show login page |
| **MinIO Console** | http://localhost:9001 | minioadmin/minioadmin123 | Should show buckets |
| **MinIO API** | http://localhost:9000 | - | Health check endpoint |
| **Prometheus** | http://localhost:9090 | No login | Should show Prometheus UI |
| **FastAPI** | http://localhost:8000/docs | No login | Should show Swagger UI |
| **FastAPI Health** | http://localhost:8000/health | - | Should return `{"status":"healthy"}` |

**⚠️ Note:** If port 8080 is already in use, Airflow is configured to use port 8081. Check `docker-compose.yml` for port mappings.

---

## 🎯 PHASE 4: Airflow Configuration (10 minutes)

### Step 1: Access Airflow UI

1. **Open browser**: http://localhost:8081 (or http://localhost:8080 if that port is free)
2. **Login**: 
   - Username: `admin`
   - Password: `admin`
3. **Verify**: You should see the Airflow DAGs page

**If you see "Connection refused" or can't connect:**
- Wait 1-2 more minutes for webserver to fully start
- Check logs: `docker compose logs airflow-webserver`
- Verify container is running: `docker compose ps airflow-webserver`

### Step 2: Verify DAG is Loaded

1. **Look for DAG**: `crypto_pipeline_dag` in the DAGs list
2. **Check status**: Should show as "Paused" (gray toggle switch)
3. **If DAG not visible:**
   ```bash
   # Check scheduler logs for errors
   docker compose logs airflow-scheduler | grep -i error
   
   # Verify DAG file exists
   dir airflow\dags\crypto_pipeline_dag.py
   
   # Restart scheduler
   docker compose restart airflow-scheduler
   ```

### Step 3: Configure Connections (Optional - if DAG needs them)

#### DagHub/MLflow Connection
1. **Admin** → **Connections** → **Add Connection**
2. Fill in:
   ```
   Connection Id: dagshub_mlflow
   Connection Type: HTTP
   Host: dagshub.com
   Schema: https
   Login: zainulabidin776
   Password: 4844315bd4005fdc92de947532a3ed2347d0028e
   ```
3. Click **Save**

#### MinIO Connection (if needed)
1. **Admin** → **Connections** → **Add Connection**
2. Fill in:
   ```
   Connection Id: minio_s3
   Connection Type: S3
   Extra: {"endpoint_url": "http://minio:9000", "aws_access_key_id": "minioadmin", "aws_secret_access_key": "minioadmin123"}
   ```
3. Click **Save**

**Note:** Most connections are configured via environment variables in `.env`, so manual connection setup may not be needed.

### Step 4: Enable and Trigger DAG

1. **Find DAG**: Look for `crypto_pipeline_dag` in the DAGs list
2. **Enable DAG**: Toggle the switch from OFF (gray) to **ON** (blue)
3. **Trigger DAG**: Click the **Play** button (▶️) to run manually
4. **Monitor**: Click on the DAG name to see the graph view

### Step 5: Monitor Execution

1. **Graph View**: Click on DAG name to see task graph
2. **Task Status**: 
   - 🟡 Yellow = Running
   - 🟢 Green = Success
   - 🔴 Red = Failed
3. **View Logs**: Click on any task → **Log** button
4. **Real-time Updates**: Page auto-refreshes every few seconds

**Expected Duration:** ~10-15 minutes for full pipeline (extract → quality → transform → train)

**Common Task Names:**
- `extract_crypto_data` - Fetches data from CryptoCompare API
- `quality_check` - Validates data quality
- `transform_features` - Feature engineering
- `train_model` - Trains XGBoost model
- `log_to_mlflow` - Logs experiment to DagHub

---

## 🎯 PHASE 5: Verification (5 minutes)

### Check Data Files

```bash
dir data\raw
dir data\processed
dir models
dir reports\quality
```

Should see timestamped files in each directory.

### Check DagHub Experiments

1. Go to: https://dagshub.com/zainulabidin776/bitcoin-price-predictor/experiments
2. You should see:
   - Experiment runs with timestamps
   - Metrics: RMSE, MAE, R², MAPE
   - Model artifacts

### Test FastAPI Prediction

```bash
curl http://localhost:8000/predict
```

Or in browser: http://localhost:8000/docs

### Check Grafana Dashboard

1. Go to: http://localhost:3000
2. Login: admin/admin
3. Navigate to Dashboards
4. Open: "Bitcoin Price Prediction Monitoring"

---

## 🎯 PHASE 6: DVC Setup (Optional - 5 minutes)

### Initialize DVC

```bash
cd C:\Users\zainy\Downloads\Bitcoin-MLOPS

# Initialize DVC
dvc init

# Add MinIO as remote
dvc remote add -d minio s3://mlops-data
dvc remote modify minio endpointurl http://localhost:9000
dvc remote modify minio access_key_id minioadmin
dvc remote modify minio secret_access_key minioadmin123

# Track data with DVC
dvc add data/raw/*.csv
dvc add data/processed/*.csv
dvc add models/*.pkl

# Push to MinIO
dvc push
```

### Verify in MinIO

1. Go to: http://localhost:9001
2. Login: minioadmin/minioadmin123
3. Check bucket: `mlops-data`
4. Should see `.dvc` files

---

## 🎯 PHASE 7: GitHub Setup (5 minutes)

### Push to GitHub

```bash
cd C:\Users\zainy\Downloads\Bitcoin-MLOPS

# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit: Complete MLOps Bitcoin prediction pipeline"

# Add remote
git remote add origin https://github.com/zainulabidin776/bitcoin-price-predictor.git

# Push
git push -u origin main
```

---

## 🎯 PHASE 8: CI/CD Setup (Optional - 10 minutes)

### Enable GitHub Actions

1. Go to: https://github.com/zainulabidin776/bitcoin-price-predictor/actions
2. Enable workflows
3. Workflows will run automatically on push

### Add Secrets

Go to: Repository → Settings → Secrets → Actions

Add these secrets:
```
DAGSHUB_TOKEN: 4844315bd4005fdc92de947532a3ed2347d0028e
DOCKER_USERNAME: itsmezayynn
DOCKER_PASSWORD: Complicated@1
```

---

## ✅ COMPLETE VERIFICATION CHECKLIST

### Core Pipeline ✅
- [ ] Data extraction working (721+ records from CryptoCompare)
- [ ] Quality checks passing (6/6 gates)
- [ ] Feature engineering complete (36 features)
- [ ] Model training successful (XGBoost)
- [ ] MLflow logging to DagHub

### Infrastructure ✅
- [ ] Docker Compose running (8 services: postgres, airflow-init, airflow-webserver, airflow-scheduler, minio, prometheus, grafana, api)
- [ ] Airflow accessible (localhost:8081 or 8080)
- [ ] Airflow init completed successfully (exited with code 0)
- [ ] Airflow webserver running (gunicorn listening)
- [ ] Airflow scheduler running (processing DAGs)
- [ ] MinIO accessible (localhost:9001 console, localhost:9000 API)
- [ ] Grafana accessible (localhost:3000)
- [ ] Prometheus accessible (localhost:9090)
- [ ] FastAPI accessible (localhost:8000/docs)

### Monitoring ✅
- [ ] Prometheus collecting metrics
- [ ] Grafana dashboard showing data
- [ ] Model metrics tracked

### Version Control ✅
- [ ] Git repository initialized
- [ ] Pushed to GitHub
- [ ] DVC tracking data/models
- [ ] GitHub Actions running

---

## 🚨 Troubleshooting

### Issue: Docker services won't start

```bash
# Stop all containers
docker compose down

# Remove volumes (WARNING: deletes all data)
docker compose down -v

# Restart Docker Desktop
# Right-click Docker Desktop icon → Restart

# Start fresh
docker compose up --build
```

### Issue: Airflow init container fails

**Symptom:** `airflow-init-1 exited with code 1`

**Solution:**
```bash
# Check init logs
docker compose logs airflow-init

# Common cause: _PIP_ADDITIONAL_REQUIREMENTS failing
# Already fixed: This is commented out in docker-compose.yml
# If you see pip install errors, the fix is already applied
```

### Issue: Airflow webserver port conflict

**Symptom:** `Bind for 127.0.0.1:8080 failed: port is already allocated`

**Solution:**
```bash
# Check what's using port 8080
netstat -ano | findstr :8080

# Option 1: Kill the process using port 8080
# Find PID from netstat output, then:
taskkill /PID <pid> /F

# Option 2: Use port 8081 (already configured in docker-compose.yml)
# Access Airflow at: http://localhost:8081

# Option 3: Change port in docker-compose.yml
# Edit line 67: "8081:8080" → "8082:8080" (or any free port)
```

### Issue: Airflow DAG not appearing

```bash
# Check scheduler logs for errors
docker compose logs airflow-scheduler | findstr /i "error"

# Verify DAG file exists
dir airflow\dags\crypto_pipeline_dag.py

# Check DAG syntax
python airflow\dags\crypto_pipeline_dag.py

# Restart scheduler
docker compose restart airflow-scheduler

# Wait 30 seconds, then refresh Airflow UI
```

### Issue: Port conflicts

```bash
# Check what's using ports
netstat -ano | findstr :8080
netstat -ano | findstr :8081
netstat -ano | findstr :9000
netstat -ano | findstr :9001

# Kill process (replace <pid> with actual PID)
taskkill /PID <pid> /F

# Or change ports in docker-compose.yml
```

### Issue: Services show "Up" but can't access

```bash
# Check if services are actually healthy
docker compose ps

# Check specific service logs
docker compose logs <service-name>

# Restart specific service
docker compose restart <service-name>

# Example: Restart Airflow webserver
docker compose restart airflow-webserver
```

### Issue: Model training fails

```bash
# Check data files exist
dir data\processed

# Check MLflow connection
python -c "import mlflow; mlflow.set_tracking_uri('https://dagshub.com/zainulabidin776/bitcoin-price-predictor.mlflow'); print('✓ MLflow connected')"
```

---

## 📊 Project Structure

```
Bitcoin-MLOPS/
├── .env                          # ✅ Configuration
├── .gitignore                    # Git ignore rules
├── .dvcignore                    # DVC ignore rules
├── docker-compose.yml            # Docker services
├── requirements.txt              # Python dependencies
├── setup_windows.bat             # ✅ Setup script
│
├── data/
│   ├── raw/                      # ✅ Extracted data (721 records)
│   └── processed/                # ✅ Transformed features
│
├── src/
│   ├── data/
│   │   ├── extract.py           # ✅ CryptoCompare extraction
│   │   ├── quality_check.py     # ✅ Quality gates
│   │   └── transform.py         # Feature engineering
│   ├── models/
│   │   └── train.py             # XGBoost training
│   └── api/
│       └── app.py               # FastAPI server
│
├── airflow/
│   └── dags/
│       └── crypto_pipeline_dag.py  # Pipeline orchestration
│
├── models/                       # ✅ Trained models
├── reports/                      # ✅ Quality reports
├── monitoring/                   # Prometheus/Grafana configs
└── tests/                        # Unit tests
```

---

## 🎯 Quick Start Commands

```bash
# Complete automated setup
setup_windows.bat

# Or manual pipeline
conda activate mlops-crypto
python src\data\extract.py
python src\data\quality_check.py
python src\data\transform.py
python src\models\train.py

# Start Docker services
docker-compose up -d

# Check everything
docker-compose ps
```

---

## 📈 Success Metrics

After complete setup, you should have:

- ✅ **Data**: 721 hourly Bitcoin records
- ✅ **Features**: 36 time-series features
- ✅ **Model**: XGBoost with RMSE < 0.05
- ✅ **Services**: 7 Docker containers running
- ✅ **Monitoring**: Real-time dashboards
- ✅ **MLflow**: Experiments logged to DagHub
- ✅ **CI/CD**: Automated testing on GitHub

---

## 🎉 Project Complete!

**Estimated Total Setup Time:** 60-90 minutes

**Components Working:**
1. ✅ Data extraction (CryptoCompare)
2. ✅ Quality validation
3. ✅ Feature engineering
4. ✅ Model training (XGBoost)
5. ✅ MLflow tracking (DagHub)
6. ✅ Containerization (Docker)
7. ✅ Orchestration (Airflow)
8. ✅ Monitoring (Prometheus/Grafana)
9. ✅ API deployment (FastAPI)
10. ✅ CI/CD (GitHub Actions)

**Ready for submission!** 🚀