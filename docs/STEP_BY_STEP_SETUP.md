# Step-by-Step Setup Guide: Prometheus, Grafana, and MinIO

**Complete configuration guide for all monitoring and storage services.**

---

## Prerequisites

✅ All Docker services running:
```powershell
docker compose ps
```

You should see all services in "Up" state:
- api-1
- prometheus-1
- grafana-1
- minio-1
- airflow-webserver-1
- airflow-scheduler-1
- postgres-1

---

## Part 1: Generate API Traffic (Create Metrics)

**First, we need to generate some API calls so Prometheus has data to scrape.**

### Option A: Using PowerShell Script (Easiest)

```powershell
# Run the setup script
.\scripts\configure-all-services.ps1
```

### Option B: Manual API Calls

Open PowerShell and run:

```powershell
# Make 5 health check calls
1..5 | ForEach-Object {
    Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    Start-Sleep -Seconds 2
}

# Make 5 prediction calls
$body = @{
    features = @(0.05, -0.02, 0.03, 0.01, -0.01, 0.04, 1.002, 0.998, 1.001, 0.0001, -0.0002, 0.0003, 0.0004, 0.0005, 0.015, 0.012, 0.001, 0.003, 0.002, 0.003, 0.001, 45.5, 0.707, 0.707, -0.434, 0.901, 0, 120.5, 50000, 49800, 49950, 49700, 50100, 0.0003, 0.0004, 0.0002)
} | ConvertTo-Json

1..5 | ForEach-Object {
    Invoke-WebRequest -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    Start-Sleep -Seconds 2
}
```

**Wait 15-20 seconds** for Prometheus to scrape the metrics.

---

## Part 2: Verify Prometheus is Working

### Step 1: Check Prometheus is Accessible

Open in browser: **http://localhost:9090**

You should see the Prometheus UI.

### Step 2: Check Targets

1. Click **"Status"** → **"Targets"** in the top menu
2. You should see:
   - ✅ **prometheus** (UP) - Prometheus monitoring itself
   - ✅ **crypto-prediction-api** (UP) - Your API service

If **crypto-prediction-api** shows as DOWN:
- Check API is running: `docker compose ps api`
- Check API logs: `docker compose logs api`
- Verify API metrics: http://localhost:8000/metrics

### Step 3: Test Queries

In Prometheus UI, try these queries:

1. **Total Requests:**
   ```
   sum(http_requests_total)
   ```
   Click "Execute" - Should show a number

2. **Prediction Latency:**
   ```
   histogram_quantile(0.95, rate(prediction_latency_seconds_bucket[5m]))
   ```
   Should show latency in seconds

3. **Data Drift:**
   ```
   data_drift_ratio
   ```
   Should show a value between 0 and 1

**If queries return "No data":**
- Make more API calls (run Part 1 again)
- Wait 15-20 seconds
- Check time range (top right) - set to "Last 1 hour"

---

## Part 3: Configure Grafana

### Step 1: Access Grafana

Open in browser: **http://localhost:3000**

**Login:**
- Username: `admin`
- Password: `admin`

**First Login:**
- You'll be asked to change password
- You can click **"Skip"** for now

### Step 2: Add Prometheus Data Source

1. **Click the ⚙️ (gear icon)** in the left sidebar
2. Click **"Data sources"**
3. Click **"Add data source"** button (top right)
4. Select **"Prometheus"**

5. **Configure:**
   - **URL:** `http://prometheus:9090`
     - ⚠️ **IMPORTANT:** Use `prometheus` (service name), NOT `localhost`
     - This works because Grafana and Prometheus are in the same Docker network
   
   - **Access:** Select **"Server (default)"**
   
   - Leave other settings as default

6. **Test Connection:**
   - Scroll down
   - Click **"Save & test"**
   - You should see: ✅ **"Data source is working"**

7. **Save:**
   - Click **"Save & test"** again

### Step 3: Create Dashboard

#### Option A: Quick Dashboard (5 minutes)

1. **Create Dashboard:**
   - Click **"+"** in left sidebar
   - Click **"Create dashboard"**
   - Click **"Add visualization"**

2. **Add First Panel - Request Rate:**
   - In the query box, paste:
     ```
     rate(http_requests_total[5m])
     ```
   - Click **"Run query"** (top right)
   - You should see a graph
   - Click **"Apply"** (top right)
   - Panel is added!

3. **Add Second Panel - Latency:**
   - Click **"Add panel"** → **"Add visualization"**
   - Query:
     ```
     histogram_quantile(0.95, rate(prediction_latency_seconds_bucket[5m]))
     ```
   - Click **"Run query"**
   - Click **"Apply"**

4. **Add Third Panel - Data Drift (Gauge):**
   - Click **"Add panel"** → **"Add visualization"**
   - Query:
     ```
     data_drift_ratio
     ```
   - In right panel, change **"Visualization"** to **"Gauge"**
   - Set **"Min"** = 0, **"Max"** = 1
   - Click **"Apply"**

5. **Save Dashboard:**
   - Click **"Save dashboard"** (💾 icon, top right)
   - Name: "MLOps Monitoring"
   - Click **"Save"**

#### Option B: Import Pre-built Dashboard

1. Click **"+"** → **"Import dashboard"**
2. Copy JSON from `scripts/setup-grafana-dashboard.json`
3. Paste into import box
4. Select Prometheus as data source
5. Click **"Import"**

### Step 4: Configure Alerts (Optional)

1. **Edit a Panel:**
   - Click panel title → **"Edit"**

2. **Add Alert:**
   - Go to **"Alert"** tab
   - Click **"Create alert rule from this panel"**
   - Configure condition (e.g., latency > 0.5)
   - Save

---

## Part 4: Configure MinIO

### Step 1: Access MinIO Console

Open in browser: **http://localhost:9001**

**Login:**
- Username: `minioadmin`
- Password: `minioadmin123`

### Step 2: Create Bucket

1. **Click "Create Bucket"** button (top right, blue button)
2. **Bucket Name:** `mlops-data`
3. **Region:** Leave default
4. **Click "Create Bucket"**

### Step 3: Verify Bucket

- You should see `mlops-data` in the buckets list
- Click on it to see contents (will be empty initially)

### Step 4: Configure DVC (Optional - for data versioning)

Open PowerShell in project directory:

```powershell
# Initialize DVC (if not done)
dvc init

# Add MinIO as remote
dvc remote add -d minio s3://mlops-data

# Configure MinIO endpoint
dvc remote modify minio endpointurl http://localhost:9000

# Configure credentials
dvc remote modify minio access_key_id minioadmin
dvc remote modify minio secret_access_key minioadmin123

# Verify
dvc remote list
```

---

## Part 5: Verification Checklist

### ✅ Prometheus
- [ ] Accessible at http://localhost:9090
- [ ] Targets show API as "UP"
- [ ] Queries return data (not "No data")

### ✅ Grafana
- [ ] Accessible at http://localhost:3000
- [ ] Prometheus data source connected
- [ ] Dashboard created with panels
- [ ] Panels showing data (not "No data")

### ✅ MinIO
- [ ] Accessible at http://localhost:9001
- [ ] Bucket `mlops-data` created
- [ ] Can login successfully

### ✅ API Metrics
- [ ] http://localhost:8000/metrics shows metrics
- [ ] Metrics include: http_requests_total, prediction_latency_seconds, data_drift_ratio

---

## Troubleshooting

### Problem: Prometheus shows "No data"

**Solution:**
1. Make API calls (see Part 1)
2. Wait 15-20 seconds
3. Check time range in Prometheus (top right) - set to "Last 1 hour"
4. Verify API metrics endpoint: http://localhost:8000/metrics

### Problem: Grafana shows "Data source is not working"

**Solution:**
1. Verify URL is `http://prometheus:9090` (NOT localhost)
2. Check Prometheus is running: `docker compose ps prometheus`
3. Check Prometheus logs: `docker compose logs prometheus`
4. Verify both services are in same network: `docker network ls`

### Problem: Grafana dashboard shows "No data"

**Solution:**
1. Verify Prometheus has data (check Part 2)
2. Check data source is selected correctly in panel
3. Verify query syntax is correct
4. Check time range (top right of dashboard)

### Problem: MinIO bucket creation fails

**Solution:**
1. Verify MinIO is running: `docker compose ps minio`
2. Check MinIO logs: `docker compose logs minio`
3. Try refreshing the page
4. Check browser console for errors

---

## Quick Test Commands

### Test API Metrics
```powershell
# Check metrics endpoint
Invoke-WebRequest -Uri "http://localhost:8000/metrics" -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Test Prometheus
```powershell
# Check targets
Invoke-WebRequest -Uri "http://localhost:9090/api/v1/targets" -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

### Generate Traffic
```powershell
# Run setup script
.\scripts\configure-all-services.ps1
```

---

## Summary

✅ **Prometheus:** Collecting metrics from API  
✅ **Grafana:** Connected to Prometheus, dashboard created  
✅ **MinIO:** Bucket created, ready for DVC  

**Next Steps:**
- Monitor dashboard regularly
- Adjust alert thresholds
- Complete DVC integration
- Test end-to-end pipeline

---

*Guide created: November 26, 2025*

