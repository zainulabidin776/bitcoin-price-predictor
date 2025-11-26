# ✅ Docker Compose Setup - Verified Working Steps

## 🎯 Quick Summary

**Status:** ✅ All services running successfully  
**Date Verified:** November 26, 2025  
**Platform:** Windows 10/11 with Docker Desktop

---

## 📋 Prerequisites Checklist

- [x] Docker Desktop installed and running
- [x] `.env` file created with all required variables
- [x] Project directory: `C:\Users\zainy\Downloads\Bitcoin-MLOPS`
- [x] At least 8GB RAM available
- [x] Ports 8081, 9000, 9001, 3000, 9090, 8000 available

---

## 🚀 Step-by-Step Setup (Verified Working)

### Step 1: Navigate to Project Directory

```bash
cd C:\Users\zainy\Downloads\Bitcoin-MLOPS
```

### Step 2: Verify .env File Exists

```bash
dir .env
```

**Required variables in `.env`:**
- CryptoCompare API config (no key needed)
- MLflow/DagHub credentials
- MinIO configuration
- Airflow configuration
- API server configuration

### Step 3: Start All Services

```bash
docker compose up --build
```

**What happens:**
1. Docker builds the API image (if needed)
2. Pulls required images (PostgreSQL, Airflow, MinIO, etc.)
3. Creates network: `bitcoin-mlops_mlops-network`
4. Creates volumes for persistent data
5. Starts all 8 services

**Expected output:**
```
[+] Building X.Xs (X/X) FINISHED
[+] Running 8/8
 ✔ Container bitcoin-mlops-postgres-1           Created
 ✔ Container bitcoin-mlops-airflow-init-1       Created
 ✔ Container bitcoin-mlops-airflow-webserver-1  Created
 ✔ Container bitcoin-mlops-airflow-scheduler-1  Created
 ✔ Container bitcoin-mlops-minio-1              Created
 ✔ Container bitcoin-mlops-prometheus-1         Created
 ✔ Container bitcoin-mlops-grafana-1            Created
 ✔ Container bitcoin-mlops-api-1                Created
```

### Step 4: Wait for Initialization (2-3 minutes)

**Key things happening:**
- PostgreSQL starts and becomes healthy
- Airflow init runs database migrations
- Airflow init creates admin user
- Airflow init exits with code 0 (success)
- Airflow webserver starts gunicorn
- Airflow scheduler starts processing DAGs
- All other services start

**Watch for these log messages:**

✅ **PostgreSQL:**
```
database system is ready to accept connections
```

✅ **Airflow Init:**
```
Database migrating done!
User "admin" created with role "Admin"
airflow-init-1 exited with code 0
```

✅ **Airflow Webserver:**
```
[INFO] Listening at: http://0.0.0.0:8080 (27)
[INFO] Booting worker with pid: 75
```

✅ **Airflow Scheduler:**
```
Starting the scheduler
Processing each file at most -1 times
```

✅ **API:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 5: Verify Services Are Running

```bash
docker compose ps
```

**Expected Status:**
```
NAME                              STATUS
bitcoin-mlops-postgres-1          Up (healthy)
bitcoin-mlops-airflow-init-1      Exited (0)  ← Normal!
bitcoin-mlops-airflow-webserver-1 Up
bitcoin-mlops-airflow-scheduler-1 Up
bitcoin-mlops-minio-1             Up
bitcoin-mlops-prometheus-1        Up
bitcoin-mlops-grafana-1           Up
bitcoin-mlops-api-1               Up
```

**✅ All services should show "Up" status**

### Step 6: Access Services

Open your browser and test each service:

| Service | URL | Credentials | Expected Result |
|---------|-----|-------------|-----------------|
| **Airflow** | http://localhost:8081 | admin/admin | DAGs page loads |
| **Grafana** | http://localhost:3000 | admin/admin | Login page |
| **MinIO** | http://localhost:9001 | minioadmin/minioadmin123 | Buckets page |
| **Prometheus** | http://localhost:9090 | - | Prometheus UI |
| **FastAPI** | http://localhost:8000/docs | - | Swagger UI |
| **FastAPI Health** | http://localhost:8000/health | - | `{"status":"healthy"}` |

---

## 🔍 Verification Checklist

### ✅ Infrastructure
- [ ] All 8 containers running
- [ ] Airflow init completed (exited with code 0)
- [ ] Airflow webserver accessible
- [ ] Airflow scheduler running
- [ ] PostgreSQL healthy
- [ ] MinIO accessible
- [ ] Prometheus collecting metrics
- [ ] Grafana accessible
- [ ] FastAPI responding

### ✅ Airflow
- [ ] Can login to Airflow UI
- [ ] DAG `crypto_pipeline_dag` visible
- [ ] DAG can be enabled (toggle switch)
- [ ] DAG can be triggered manually
- [ ] Tasks execute successfully

### ✅ API
- [ ] Health endpoint returns 200
- [ ] Swagger docs accessible
- [ ] Metrics endpoint working

---

## 🐛 Troubleshooting

### Issue: Port 8080 Already in Use

**Symptom:**
```
Error: Bind for 127.0.0.1:8080 failed: port is already allocated
```

**Solution:**
- Already configured: Airflow uses port 8081
- Access at: http://localhost:8081
- Or change port in `docker-compose.yml` line 67

### Issue: Airflow Init Fails

**Symptom:**
```
airflow-init-1 exited with code 1
```

**Check logs:**
```bash
docker compose logs airflow-init
```

**Common causes:**
- ✅ **FIXED:** `_PIP_ADDITIONAL_REQUIREMENTS` causing pip install failures
  - **Solution:** Already commented out in `docker-compose.yml` line 15-23
- Database connection issues
  - **Solution:** Wait for PostgreSQL to be healthy first

### Issue: Services Won't Start

**Solution:**
```bash
# Stop everything
docker compose down

# Remove volumes (WARNING: deletes data)
docker compose down -v

# Restart Docker Desktop
# Then start fresh
docker compose up --build
```

### Issue: Can't Access Services

**Check:**
1. Wait 2-3 minutes for full initialization
2. Check service logs: `docker compose logs <service-name>`
3. Verify container is running: `docker compose ps`
4. Check if port is correct (8081 for Airflow)

---

## 📊 Service Details

### PostgreSQL
- **Port:** 5432 (internal)
- **Database:** airflow
- **User:** airflow
- **Password:** airflow
- **Volume:** `postgres-db-volume`

### Airflow
- **Webserver Port:** 8081 (host) → 8080 (container)
- **Scheduler:** Internal
- **Init:** Runs once, then exits
- **Credentials:** admin/admin
- **Volumes:** DAGs, logs, plugins, data, models

### MinIO
- **Console Port:** 9001
- **API Port:** 9000
- **Credentials:** minioadmin/minioadmin123
- **Bucket:** mlops-data (create via UI)

### Prometheus
- **Port:** 9090
- **Config:** `monitoring/prometheus.yml`
- **Data:** `prometheus-data` volume

### Grafana
- **Port:** 3000
- **Credentials:** admin/admin
- **Data:** `grafana-data` volume

### FastAPI
- **Port:** 8000
- **Workers:** 4
- **Health:** http://localhost:8000/health
- **Docs:** http://localhost:8000/docs

---

## 🎯 Next Steps

1. **Access Airflow UI:** http://localhost:8081
2. **Enable DAG:** Toggle `crypto_pipeline_dag` to ON
3. **Trigger DAG:** Click play button
4. **Monitor:** Watch task execution in real-time
5. **Check Results:** View data in `data/` and `models/` directories

---

## ✅ Success Indicators

You'll know everything is working when:

1. ✅ All 8 containers show "Up" status
2. ✅ Airflow init shows "exited with code 0"
3. ✅ Can login to Airflow UI
4. ✅ DAG is visible and can be enabled
5. ✅ Can trigger DAG and tasks execute
6. ✅ All other services are accessible
7. ✅ No errors in logs

---

## 📝 Key Fixes Applied

1. **✅ Fixed Airflow Init Failure**
   - Commented out `_PIP_ADDITIONAL_REQUIREMENTS` in `docker-compose.yml`
   - This was causing pip install failures during init
   - Packages should be installed in a custom image for production

2. **✅ Fixed Port Conflict**
   - Changed Airflow webserver port to 8081 (from 8080)
   - Prevents conflicts with other services using port 8080

3. **✅ Verified All Services**
   - All 8 services start successfully
   - Health checks passing
   - Services accessible via browser

---

## 🎉 You're All Set!

Everything is configured and working. Follow the steps above to start your MLOps pipeline!

**Quick Start Command:**
```bash
cd C:\Users\zainy\Downloads\Bitcoin-MLOPS
docker compose up --build
```

Then access: http://localhost:8081 (Airflow)

---

**Last Updated:** November 26, 2025  
**Status:** ✅ Verified Working

