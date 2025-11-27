# Grafana Setup & Configuration Guide

## Overview

Grafana is a visualization and monitoring tool that connects to Prometheus to create dashboards and alerts for your MLOps pipeline. This guide will help you configure Grafana for the cryptocurrency volatility prediction system.

---

## Prerequisites

✅ Docker Compose services running  
✅ Prometheus accessible at http://localhost:9090  
✅ FastAPI service running and exposing metrics at http://localhost:8000/metrics

---

## Step 1: Access Grafana

1. **Open Grafana UI:**
   ```
   http://localhost:3000
   ```

2. **Login:**
   - Username: `admin`
   - Password: `admin` (default, change on first login)

3. **First Login:**
   - You'll be prompted to change the password
   - You can skip this for now (click "Skip")

---

## Step 2: Add Prometheus Data Source

1. **Navigate to Data Sources:**
   - Click the **⚙️ (gear icon)** in the left sidebar
   - Select **"Data sources"**

2. **Add Data Source:**
   - Click **"Add data source"**
   - Select **"Prometheus"**

3. **Configure Prometheus:**
   - **URL:** `http://prometheus:9090`
     - ⚠️ **Important:** Use `prometheus` (service name) not `localhost`
     - This works because both services are in the same Docker network
   
   - **Access:** Select **"Server (default)"**
   
   - **Scrape interval:** `15s` (optional, matches Prometheus config)

4. **Test Connection:**
   - Click **"Save & test"** at the bottom
   - You should see: ✅ **"Data source is working"**

5. **Save:**
   - Click **"Save & test"** again to confirm

---

## Step 3: Create Monitoring Dashboard

### Option A: Import Pre-built Dashboard (Recommended)

1. **Create Dashboard:**
   - Click **"+"** in left sidebar
   - Select **"Import dashboard"**

2. **Import JSON:**
   - Copy the dashboard JSON from `docs/grafana-dashboard.json` (we'll create this)
   - Paste into the import box
   - Click **"Load"**

3. **Select Data Source:**
   - Choose **"Prometheus"** as data source
   - Click **"Import"**

### Option B: Create Dashboard Manually

1. **Create New Dashboard:**
   - Click **"+"** in left sidebar
   - Select **"Create dashboard"**
   - Click **"Add visualization"**

2. **Add Panels:**

#### Panel 1: API Request Rate

- **Query:**
  ```promql
  rate(http_requests_total[5m])
  ```
- **Title:** "API Request Rate"
- **Unit:** "requests/sec"
- **Visualization:** Time series

#### Panel 2: Prediction Latency

- **Query:**
  ```promql
  histogram_quantile(0.95, rate(prediction_latency_seconds_bucket[5m]))
  ```
- **Title:** "95th Percentile Prediction Latency"
- **Unit:** "seconds"
- **Visualization:** Time series
- **Thresholds:**
  - Green: < 0.1s
  - Yellow: 0.1s - 0.5s
  - Red: > 0.5s

#### Panel 3: Data Drift Ratio

- **Query:**
  ```promql
  data_drift_ratio
  ```
- **Title:** "Data Drift Ratio"
- **Unit:** "percent (0-1)"
- **Visualization:** Gauge
- **Thresholds:**
  - Green: < 0.1
  - Yellow: 0.1 - 0.15
  - Red: > 0.15

#### Panel 4: Total Requests

- **Query:**
  ```promql
  sum(http_requests_total)
  ```
- **Title:** "Total API Requests"
- **Unit:** "short"
- **Visualization:** Stat

#### Panel 5: Latest Prediction Value

- **Query:**
  ```promql
  model_prediction_value
  ```
- **Title:** "Latest Prediction"
- **Unit:** "short"
- **Visualization:** Stat

#### Panel 6: Error Rate

- **Query:**
  ```promql
  rate(http_requests_total{status=~"5.."}[5m])
  ```
- **Title:** "Error Rate (5xx)"
- **Unit:** "percent (0-1)"
- **Visualization:** Time series

3. **Save Dashboard:**
   - Click **"Save dashboard"** (💾 icon)
   - Name: "MLOps Crypto Prediction Monitoring"
   - Folder: "General"

---

## Step 4: Configure Alerts

### Alert 1: High Latency

1. **Edit Panel:**
   - Go to "Prediction Latency" panel
   - Click panel title → **"Edit"**

2. **Add Alert:**
   - Go to **"Alert"** tab
   - Click **"Create alert rule from this panel"**

3. **Configure Alert:**
   - **Name:** "High Prediction Latency"
   - **Condition:**
     ```promql
     histogram_quantile(0.95, rate(prediction_latency_seconds_bucket[5m])) > 0.5
     ```
   - **Evaluate every:** `1m`
   - **For:** `2m` (alert if condition true for 2 minutes)

4. **Add Notification:**
   - Click **"Add notification channel"**
   - For now, you can use **"Test"** to see alerts in Grafana
   - (Optional: Configure Slack/webhook later)

5. **Save:**
   - Click **"Save rule"**

### Alert 2: Data Drift Detected

1. **Edit Panel:**
   - Go to "Data Drift Ratio" panel
   - Click panel title → **"Edit"**

2. **Add Alert:**
   - Go to **"Alert"** tab
   - Click **"Create alert rule from this panel"**

3. **Configure Alert:**
   - **Name:** "Data Drift Detected"
   - **Condition:**
     ```promql
     data_drift_ratio > 0.15
     ```
   - **Evaluate every:** `1m`
   - **For:** `1m`

4. **Save:**
   - Click **"Save rule"**

---

## Step 5: Test the Setup

### Test Metrics Collection

1. **Generate Some Traffic:**
   ```bash
   # Make some API calls
   curl http://localhost:8000/health
   curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"features": [0.05, -0.02, 0.03, 0.01, -0.01, 0.04, 1.002, 0.998, 1.001, 0.0001, -0.0002, 0.0003, 0.0004, 0.0005, 0.015, 0.012, 0.001, 0.003, 0.002, 0.003, 0.001, 45.5, 0.707, 0.707, -0.434, 0.901, 0, 120.5, 50000, 49800, 49950, 49700, 50100, 0.0003, 0.0004, 0.0002]}'
   ```

2. **Check Dashboard:**
   - Refresh Grafana dashboard
   - You should see metrics updating

3. **Verify Prometheus:**
   - Go to http://localhost:9090
   - Click **"Graph"** tab
   - Try query: `http_requests_total`
   - You should see data

---

## Step 6: Verify Alerts

1. **View Alerts:**
   - In Grafana, click **"Alerting"** (bell icon) in left sidebar
   - Click **"Alert rules"**
   - You should see your configured alerts

2. **Test Alert:**
   - Alerts will fire when conditions are met
   - Check alert state (Pending/Firing)

---

## Troubleshooting

### Issue: "Data source is not working"

**Solution:**
- Verify Prometheus is running: `docker compose ps prometheus`
- Check Prometheus URL: Use `http://prometheus:9090` (not localhost)
- Verify network: Both services should be in `mlops-network`

### Issue: No metrics showing

**Solution:**
- Check Prometheus targets: http://localhost:9090/targets
- Verify API metrics endpoint: http://localhost:8000/metrics
- Check Prometheus logs: `docker compose logs prometheus`

### Issue: Dashboard not updating

**Solution:**
- Check time range (top right of dashboard)
- Verify data source is selected correctly
- Refresh dashboard (F5)

---

## Advanced Configuration

### Add Slack Notifications (Optional)

1. **Create Slack Webhook:**
   - Go to https://api.slack.com/apps
   - Create new app → Incoming Webhooks
   - Copy webhook URL

2. **Add Notification Channel in Grafana:**
   - Settings → Alerting → Notification channels
   - Add new channel → "Slack"
   - Paste webhook URL
   - Test and save

3. **Add to Alert Rules:**
   - Edit alert rule
   - Add notification channel
   - Save

---

## Dashboard JSON Export

To share or backup your dashboard:

1. **Export Dashboard:**
   - Open dashboard
   - Click **"Dashboard settings"** (⚙️ icon)
   - Go to **"JSON Model"** tab
   - Copy JSON
   - Save to `monitoring/grafana/dashboards/mlops-monitoring.json`

---

## Summary

✅ **Completed:**
- Prometheus data source connected
- Monitoring dashboard created
- Alerts configured
- Metrics visualization working

**Next Steps:**
- Monitor dashboard regularly
- Adjust alert thresholds as needed
- Add more panels if required
- Configure external notifications (optional)

---

*Guide created: November 26, 2025*

