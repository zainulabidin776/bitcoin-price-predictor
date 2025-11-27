# Quick Configuration Guide - Prometheus, Grafana, MinIO

**Follow these steps in order. Each step takes 2-5 minutes.**

---

## ⚡ Quick Start (5 minutes)

### Step 1: Generate API Traffic

**Open PowerShell and run:**

```powershell
# Run the quick setup script
.\scripts\quick-setup.ps1
```

**OR manually:**

```powershell
# Make API calls
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# Wait 15 seconds
Start-Sleep -Seconds 15
```

**Why?** Prometheus needs data to scrape. Making API calls creates metrics.

---

### Step 2: Verify Prometheus (2 minutes)

1. **Open browser:** http://localhost:9090

2. **Check Targets:**
   - Click **"Status"** → **"Targets"** (top menu)
   - Look for **"crypto-prediction-api"**
   - Should show: **UP** (green)

3. **Test Query:**
   - Click **"Graph"** tab
   - In query box, type: `sum(http_requests_total)`
   - Click **"Execute"**
   - Should show a number (not "No data")

**✅ If you see data, Prometheus is working!**

---

### Step 3: Configure Grafana (3 minutes)

1. **Open Grafana:** http://localhost:3000
   - Login: `admin` / `admin`
   - Click **"Skip"** if asked to change password

2. **Add Prometheus Data Source:**
   - Click **⚙️ (Settings)** → **"Data sources"** (left sidebar)
   - Click **"Add data source"** (top right)
   - Click **"Prometheus"**

3. **Configure:**
   - **URL:** `http://prometheus:9090`
     - ⚠️ **IMPORTANT:** Use `prometheus` NOT `localhost`
   - **Access:** "Server (default)"
   - Scroll down → Click **"Save & test"**
   - Should see: ✅ **"Data source is working"**

4. **Create Simple Dashboard:**
   - Click **"+"** (left sidebar) → **"Create dashboard"**
   - Click **"Add visualization"**
   - In query box, paste:
     ```
     sum(http_requests_total)
     ```
   - Click **"Run query"** (top right)
   - You should see a graph!
   - Click **"Apply"** (top right)
   - Click **"Save dashboard"** (💾 icon)
   - Name: "MLOps Monitoring"
   - Click **"Save"**

**✅ Dashboard created!**

---

### Step 4: Configure MinIO (2 minutes)

1. **Open MinIO Console:** http://localhost:9001
   - Login: `minioadmin` / `minioadmin123`

2. **Create Bucket:**
   - Click **"Create Bucket"** (blue button, top right)
   - **Bucket Name:** `mlops-data`
   - Click **"Create Bucket"**

3. **Verify:**
   - You should see `mlops-data` in the list
   - Click on it (will be empty, that's OK)

**✅ MinIO ready!**

---

## 🎯 Verification Checklist

After completing all steps, verify:

### Prometheus
- [ ] http://localhost:9090 opens
- [ ] Targets show API as "UP"
- [ ] Query `sum(http_requests_total)` returns data

### Grafana
- [ ] http://localhost:3000 opens
- [ ] Prometheus data source shows "Data source is working"
- [ ] Dashboard shows graph with data

### MinIO
- [ ] http://localhost:9001 opens
- [ ] Bucket `mlops-data` exists

---

## 🔧 Troubleshooting

### "No data" in Prometheus

**Fix:**
1. Make more API calls:
   ```powershell
   1..10 | ForEach-Object {
       Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
       Start-Sleep -Seconds 1
   }
   ```
2. Wait 15-20 seconds
3. Check time range (top right) - set to "Last 1 hour"

### Grafana "Data source is not working"

**Fix:**
1. Verify URL is `http://prometheus:9090` (NOT localhost)
2. Check Prometheus is running: `docker compose ps prometheus`
3. Try: `http://prometheus:9090` in browser (won't work, but tests network)

### API metrics not showing

**Fix:**
1. Check API is running: `docker compose ps api`
2. Test metrics endpoint: http://localhost:8000/metrics
3. Should see: `http_requests_total`, `prediction_latency_seconds`, etc.

---

## 📊 Next Steps

Once everything is working:

1. **Add More Grafana Panels:**
   - See `docs/GRAFANA_SETUP_GUIDE.md` for panel configurations
   - Add latency, drift, error rate panels

2. **Configure Alerts:**
   - Edit panel → Alert tab
   - Set thresholds (latency > 500ms, drift > 0.15)

3. **Complete DVC Setup:**
   - See `docs/MINIO_SETUP_GUIDE.md`
   - Configure DVC to use MinIO

---

## 🚀 Quick Commands Reference

```powershell
# Check services
docker compose ps

# Generate API traffic
.\scripts\quick-setup.ps1

# Check Prometheus targets
Start-Process "http://localhost:9090/api/v1/targets"

# Check API metrics
Start-Process "http://localhost:8000/metrics"

# Open Grafana
Start-Process "http://localhost:3000"

# Open MinIO
Start-Process "http://localhost:9001"
```

---

**That's it! You should now have:**
- ✅ Prometheus collecting metrics
- ✅ Grafana visualizing data
- ✅ MinIO bucket ready

*Guide created: November 26, 2025*

