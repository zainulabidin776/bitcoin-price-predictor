# 🚀 START HERE - Complete Setup Guide

**Everything you need to configure Prometheus, Grafana, and MinIO in one place.**

---

## 📋 Quick Summary

You have 3 services that need configuration:
1. **Prometheus** - Already collecting metrics ✅ (just needs data)
2. **Grafana** - Needs data source connection ⚠️
3. **MinIO** - Needs bucket creation ⚠️

**Total time: 10-15 minutes**

---

## 🎯 Step-by-Step (Follow in Order)

### STEP 1: Generate API Traffic (2 min)

**Open PowerShell and run:**

```powershell
# Option A: Use script
.\scripts\quick-setup.ps1

# Option B: Manual
1..10 | ForEach-Object {
    Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    Start-Sleep -Seconds 1
}
Start-Sleep -Seconds 20
```

**Why?** Prometheus needs data to scrape. API calls create metrics.

---

### STEP 2: Verify Prometheus (2 min)

1. **Open:** http://localhost:9090
2. **Click:** Status → Targets
3. **Check:** `crypto-prediction-api` shows **UP** (green)
4. **Test Query:**
   - Click "Graph" tab
   - Type: `sum(http_requests_total)`
   - Click "Execute"
   - Should see a number (not "No data")

**✅ If you see data, Prometheus is working!**

---

### STEP 3: Configure Grafana (5 min)

1. **Open:** http://localhost:3000
2. **Login:** admin / admin
3. **Add Data Source:**
   - Click ⚙️ → Data sources
   - Click "Add data source"
   - Select "Prometheus"
   - **URL:** `http://prometheus:9090` ⚠️ (NOT localhost!)
   - Click "Save & test"
   - Should see: ✅ "Data source is working"

4. **Create Dashboard:**
   - Click + → Create dashboard
   - Click "Add visualization"
   - Query: `sum(http_requests_total)`
   - Click "Run query"
   - Click "Apply"
   - Click "Save dashboard"

**✅ Dashboard created!**

---

### STEP 4: Configure MinIO (2 min)

1. **Open:** http://localhost:9001
2. **Login:** minioadmin / minioadmin123
3. **Create Bucket:**
   - Click "Create Bucket"
   - Name: `mlops-data`
   - Click "Create Bucket"

**✅ MinIO ready!**

---

## 📚 Detailed Guides

- **Complete Step-by-Step:** `SETUP_MONITORING_NOW.md`
- **Grafana Details:** `docs/GRAFANA_SETUP_GUIDE.md`
- **MinIO Details:** `docs/MINIO_SETUP_GUIDE.md`
- **Quick Reference:** `docs/QUICK_CONFIGURATION_GUIDE.md`

---

## ✅ Verification

After setup, verify:

| Service | URL | What to Check |
|---------|-----|---------------|
| **Prometheus** | http://localhost:9090 | Query returns data |
| **Grafana** | http://localhost:3000 | Dashboard shows graphs |
| **MinIO** | http://localhost:9001 | Bucket `mlops-data` exists |

---

## 🔧 Common Issues

### "No data" in Prometheus
→ Make more API calls, wait 20 seconds

### Grafana "Data source not working"
→ Check URL is `http://prometheus:9090` (NOT localhost)

### Panels show "No data"
→ Check time range (top right) - set to "Last 1 hour"

---

## 🎉 Success!

Once all steps are complete:
- ✅ Prometheus collecting metrics
- ✅ Grafana visualizing data  
- ✅ MinIO bucket ready for DVC

**You're done!** 🚀

---

*For detailed instructions, see `SETUP_MONITORING_NOW.md`*

