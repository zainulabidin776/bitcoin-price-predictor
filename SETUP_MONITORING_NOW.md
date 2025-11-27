# 🚀 Setup Prometheus, Grafana & MinIO - Step by Step

**Follow these steps exactly. Takes 10-15 minutes total.**

---

## ✅ Pre-Check: Services Running

```powershell
docker compose ps
```

All services should show "Up". If not, run:
```powershell
docker compose up -d
```

---

## PART 1: Generate Metrics Data (2 minutes)

**We need to create some API traffic so Prometheus has data to collect.**

### Option A: Run Script (Easiest)

```powershell
.\scripts\quick-setup.ps1
```

### Option B: Manual Commands

Open PowerShell and run:

```powershell
# Make 10 health check calls
1..10 | ForEach-Object {
    Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    Write-Host "Call $_ done"
    Start-Sleep -Seconds 1
}

# Wait for Prometheus to scrape
Write-Host "Waiting 20 seconds for Prometheus..."
Start-Sleep -Seconds 20
```

**✅ Done! Now Prometheus has data.**

---

## PART 2: Verify Prometheus (3 minutes)

### Step 1: Open Prometheus

**Open in browser:** http://localhost:9090

You should see the Prometheus UI.

### Step 2: Check Targets

1. Click **"Status"** in top menu
2. Click **"Targets"**
3. You should see:
   - ✅ **prometheus** - State: UP
   - ✅ **crypto-prediction-api** - State: UP

**If crypto-prediction-api shows DOWN:**
- Check API is running: `docker compose ps api`
- Check API logs: `docker compose logs api --tail 50`
- Verify API metrics: Open http://localhost:8000/metrics in browser

### Step 3: Test Query

1. Click **"Graph"** tab (top menu)
2. In the query box, type:
   ```
   sum(http_requests_total)
   ```
3. Click **"Execute"** button
4. **Below the graph**, you should see:
   - `{instance="api:8000", job="crypto-prediction-api"} 10` (or similar number)
   - **NOT** "No data points found"

**✅ If you see a number, Prometheus is working!**

**Try more queries:**
```
# Prediction latency
histogram_quantile(0.95, rate(prediction_latency_seconds_bucket[5m]))

# Data drift
data_drift_ratio
```

---

## PART 3: Configure Grafana (5 minutes)

### Step 1: Access Grafana

**Open in browser:** http://localhost:3000

**Login:**
- Username: `admin`
- Password: `admin`

**First time:**
- You'll be asked to change password
- Click **"Skip"** for now (you can change later)

### Step 2: Add Prometheus Data Source

1. **Click ⚙️ (Settings icon)** in left sidebar
2. Click **"Data sources"**
3. Click **"Add data source"** button (top right, blue button)
4. Click **"Prometheus"** (first option)

5. **Configure:**
   - **URL:** Type: `http://prometheus:9090`
     - ⚠️ **CRITICAL:** Use `prometheus` (service name), NOT `localhost`
     - This works because Grafana and Prometheus are in the same Docker network
   
   - **Access:** Select **"Server (default)"** (should be selected)
   
   - **Scrape interval:** Leave default (15s)
   
   - **HTTP Method:** Leave default (POST)

6. **Test Connection:**
   - Scroll down to bottom
   - Click **"Save & test"** button
   - **You should see:** ✅ Green checkmark with "Data source is working"

7. **If you see error:**
   - Check URL is exactly: `http://prometheus:9090`
   - Verify Prometheus is running: `docker compose ps prometheus`
   - Check Prometheus logs: `docker compose logs prometheus --tail 20`

8. **Save:**
   - Click **"Save & test"** again to confirm

**✅ Prometheus data source added!**

### Step 3: Create Dashboard

#### Quick Dashboard (3 minutes)

1. **Create Dashboard:**
   - Click **"+"** (plus icon) in left sidebar
   - Click **"Create dashboard"**
   - Click **"Add visualization"** (or "Add panel")

2. **Add First Panel - Total Requests:**
   - In the query box (at bottom), you'll see "Metrics browser"
   - Click in the query box and type:
     ```
     sum(http_requests_total)
     ```
   - Click **"Run query"** button (top right)
   - **You should see:** A graph or number showing total requests
   - Click **"Apply"** button (top right)
   - Panel is added!

3. **Add Second Panel - Request Rate:**
   - Click **"Add panel"** → **"Add visualization"**
   - Query:
     ```
     rate(http_requests_total[5m])
     ```
   - Click **"Run query"**
   - Should see a line graph
   - Click **"Apply"**

4. **Add Third Panel - Latency (Gauge):**
   - Click **"Add panel"** → **"Add visualization"**
   - Query:
     ```
     histogram_quantile(0.95, rate(prediction_latency_seconds_bucket[5m]))
     ```
   - Click **"Run query"**
   - In right panel, find **"Visualization"** dropdown
   - Change from "Time series" to **"Gauge"**
   - Click **"Apply"**

5. **Add Fourth Panel - Data Drift:**
   - Click **"Add panel"** → **"Add visualization"**
   - Query:
     ```
     data_drift_ratio
     ```
   - Click **"Run query"**
   - Change visualization to **"Gauge"**
   - Set **"Min"** = 0, **"Max"** = 1
   - Click **"Apply"**

6. **Save Dashboard:**
   - Click **"Save dashboard"** icon (💾, top right)
   - **Name:** "MLOps Crypto Monitoring"
   - **Folder:** "General" (default)
   - Click **"Save"**

**✅ Dashboard created!**

**If panels show "No data":**
- Make sure you ran Part 1 (generated API traffic)
- Check time range (top right) - set to "Last 1 hour"
- Verify Prometheus has data (go back to Part 2, Step 3)

---

## PART 4: Configure MinIO (2 minutes)

### Step 1: Access MinIO Console

**Open in browser:** http://localhost:9001

**Login:**
- Username: `minioadmin`
- Password: `minioadmin123`

### Step 2: Create Bucket

1. **Click "Create Bucket"** button
   - Blue button, top right
   - Or click **"Buckets"** in left menu → **"Create Bucket"**

2. **Configure Bucket:**
   - **Bucket Name:** Type `mlops-data`
   - **Region:** Leave default (us-east-1)
   - **Object Locking:** Leave OFF (default)

3. **Create:**
   - Click **"Create Bucket"** button (bottom right)

4. **Verify:**
   - You should see `mlops-data` in the buckets list
   - Click on it - it will be empty (that's OK)

**✅ MinIO bucket created!**

### Step 3: Configure DVC (Optional - for data versioning)

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

**✅ DVC configured!**

---

## ✅ Final Verification

### Checklist:

- [ ] **Prometheus:** http://localhost:9090
  - [ ] Targets show API as "UP"
  - [ ] Query `sum(http_requests_total)` returns data

- [ ] **Grafana:** http://localhost:3000
  - [ ] Prometheus data source shows "Data source is working"
  - [ ] Dashboard created with panels
  - [ ] Panels showing data (not "No data")

- [ ] **MinIO:** http://localhost:9001
  - [ ] Can login
  - [ ] Bucket `mlops-data` exists

---

## 🎯 What You Should See

### Prometheus (http://localhost:9090)
- Graph page with query box
- Targets page showing API as "UP"
- Queries returning numbers (not "No data")

### Grafana (http://localhost:3000)
- Dashboard with 4 panels
- Graphs showing data
- Numbers updating (if you make more API calls)

### MinIO (http://localhost:9001)
- Bucket list showing `mlops-data`
- Can click on bucket (empty is OK)

---

## 🔧 Troubleshooting

### Problem: Prometheus shows "No data"

**Solution:**
1. Make more API calls:
   ```powershell
   1..20 | ForEach-Object {
       Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
       Start-Sleep -Seconds 1
   }
   ```
2. Wait 20 seconds
3. In Prometheus, check time range (top right) - set to "Last 1 hour"
4. Try query again

### Problem: Grafana "Data source is not working"

**Solution:**
1. **Check URL:** Must be `http://prometheus:9090` (NOT localhost)
2. **Check Prometheus:** `docker compose ps prometheus` (should be Up)
3. **Check network:** Both services in same Docker network
4. **Try again:** Delete data source, add again with correct URL

### Problem: Grafana panels show "No data"

**Solution:**
1. **Check Prometheus has data:** Go to http://localhost:9090, try query
2. **Check time range:** Top right of dashboard, set to "Last 1 hour"
3. **Check data source:** Make sure Prometheus is selected in panel
4. **Generate more traffic:** Run Part 1 again

### Problem: API metrics endpoint not working

**Solution:**
1. Check API is running: `docker compose ps api`
2. Check API logs: `docker compose logs api --tail 50`
3. Test endpoint: Open http://localhost:8000/metrics in browser
4. Should see text with `http_requests_total`, `prediction_latency_seconds`, etc.

---

## 📊 Next Steps

Once everything is working:

1. **Add More Panels to Grafana:**
   - Error rate
   - Request breakdown by endpoint
   - System health metrics

2. **Configure Alerts:**
   - Edit panel → Alert tab
   - Set condition (e.g., latency > 0.5)
   - Save alert rule

3. **Complete DVC Integration:**
   - Update Airflow DAG task
   - Test data versioning
   - Push data to MinIO

---

## 🚀 Quick Commands

```powershell
# Generate traffic
.\scripts\quick-setup.ps1

# Check services
docker compose ps

# Check Prometheus targets
Start-Process "http://localhost:9090/api/v1/targets"

# Open Grafana
Start-Process "http://localhost:3000"

# Open MinIO
Start-Process "http://localhost:9001"

# Check API metrics
Start-Process "http://localhost:8000/metrics"
```

---

**You're all set!** 🎉

All three services should now be configured and showing data.

*Last Updated: November 26, 2025*

