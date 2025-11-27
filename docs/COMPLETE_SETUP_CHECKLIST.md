# Complete Setup Checklist - Final Steps to 100% Compliance

**Project:** MLOps RPS - Cryptocurrency Volatility Prediction  
**Team:** Zain ul Abidin, Sanan Azfar, Ahmed Javed  
**Status:** 83% Complete → Target: 100%

---

## Current Status Summary

✅ **What's Working:**
- All Docker services running
- Airflow DAG executing successfully
- Data extraction, quality checks, transformation working
- Model training with MLflow tracking
- FastAPI API serving predictions
- Prometheus collecting metrics
- CI/CD pipelines functional

⚠️ **What Needs Configuration:**
- Grafana dashboard setup
- DVC integration completion
- DagHub DVC remote configuration

---

## Priority 1: Grafana Configuration (Ahmed Javed - 2-3 hours)

### Step 1: Access Grafana
- [ ] Open http://localhost:3000
- [ ] Login: admin/admin
- [ ] Change password (optional)

### Step 2: Add Prometheus Data Source
- [ ] Go to Settings → Data sources
- [ ] Add Prometheus
- [ ] URL: `http://prometheus:9090`
- [ ] Click "Save & test"
- [ ] Verify: ✅ "Data source is working"

### Step 3: Create Dashboard
- [ ] Create new dashboard
- [ ] Add panels:
  - [ ] API Request Rate
  - [ ] Prediction Latency (95th percentile)
  - [ ] Data Drift Ratio (Gauge)
  - [ ] Total Requests (Stat)
  - [ ] Error Rate
- [ ] Save dashboard

### Step 4: Configure Alerts
- [ ] Create alert: Latency > 500ms
- [ ] Create alert: Data Drift > 0.15
- [ ] Test alerts

**Reference:** See `docs/GRAFANA_SETUP_GUIDE.md` for detailed instructions

---

## Priority 2: DVC Integration (Zain ul Abidin - 1-2 hours)

### Step 1: Verify MinIO Setup
- [ ] Access MinIO: http://localhost:9001
- [ ] Login: minioadmin/minioadmin123
- [ ] Create bucket: `mlops-data`
- [ ] Verify bucket exists

### Step 2: Configure DVC
```bash
# Initialize DVC (if not done)
dvc init

# Add MinIO as remote
dvc remote add -d minio s3://mlops-data
dvc remote modify minio endpointurl http://localhost:9000
dvc remote modify minio access_key_id minioadmin
dvc remote modify minio secret_access_key minioadmin123
```

- [ ] Run above commands
- [ ] Verify: `dvc remote list` shows "minio"

### Step 3: Complete DAG Task
- [ ] Update `version_with_dvc()` in `airflow/dags/crypto_pipeline_dag.py`
- [ ] Add DVC commands:
  ```python
  subprocess.run(['dvc', 'add', processed_path], check=True)
  subprocess.run(['dvc', 'push'], check=True)
  ```
- [ ] Test task execution

### Step 4: Test DVC Workflow
- [ ] Run DAG manually
- [ ] Verify DVC task completes
- [ ] Check MinIO bucket for .dvc files
- [ ] Verify .dvc files in Git

**Reference:** See `docs/MINIO_SETUP_GUIDE.md` for detailed instructions

---

## Priority 3: DagHub DVC Remote (Sanan Azfar - 30 minutes)

### Step 1: Configure DagHub DVC
```bash
# Add DagHub as DVC remote
dvc remote add dagshub https://dagshub.com/zainulabidin776/bitcoin-price-predictor.dvc
dvc remote modify dagshub url https://dagshub.com/zainulabidin776/bitcoin-price-predictor.dvc
```

- [ ] Run configuration commands
- [ ] Test: `dvc push -r dagshub`

### Step 2: Verify in DagHub
- [ ] Go to DagHub repository
- [ ] Check "Datasets" tab
- [ ] Verify data files appear

---

## Priority 4: Final Verification (All - 1 hour)

### Infrastructure Check
- [ ] All Docker services running: `docker compose ps`
- [ ] Airflow accessible: http://localhost:8081
- [ ] MinIO accessible: http://localhost:9001
- [ ] Prometheus accessible: http://localhost:9090
- [ ] Grafana accessible: http://localhost:3000
- [ ] API accessible: http://localhost:8000/docs

### Pipeline Check
- [ ] Run full DAG in Airflow
- [ ] Verify all tasks complete successfully
- [ ] Check MLflow experiments in DagHub
- [ ] Verify data in MinIO
- [ ] Test API predictions

### Monitoring Check
- [ ] Grafana dashboard showing metrics
- [ ] Prometheus scraping API metrics
- [ ] Alerts configured and tested
- [ ] Dashboard panels updating

### CI/CD Check
- [ ] GitHub Actions workflows enabled
- [ ] Test PR workflow
- [ ] Verify CML reports in PRs
- [ ] Check Docker image builds

---

## Documentation Checklist

- [ ] Review `docs/PROJECT_REQUIREMENTS_ANALYSIS.md`
- [ ] Review `docs/WORK_DIVISION.md`
- [ ] Review `docs/GRAFANA_SETUP_GUIDE.md`
- [ ] Review `docs/MINIO_SETUP_GUIDE.md`
- [ ] Compile LaTeX report: `docs/PROJECT_REPORT.tex`
- [ ] Update README with final status

---

## Submission Checklist

### Code
- [ ] All code committed to GitHub
- [ ] .dvc files committed
- [ ] No sensitive data in repository
- [ ] README updated

### Documentation
- [ ] LaTeX report compiled to PDF
- [ ] All documentation files reviewed
- [ ] Architecture diagrams included
- [ ] Work division documented

### Demonstration
- [ ] Pipeline runs end-to-end
- [ ] All services accessible
- [ ] Monitoring dashboards working
- [ ] API serving predictions

---

## Quick Reference: Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Airflow | http://localhost:8081 | admin/admin |
| MinIO Console | http://localhost:9001 | minioadmin/minioadmin123 |
| MinIO API | http://localhost:9000 | minioadmin/minioadmin123 |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |
| FastAPI | http://localhost:8000/docs | - |
| DagHub | https://dagshub.com/zainulabidin776/bitcoin-price-predictor | Your credentials |

---

## Estimated Time to Completion

| Task | Owner | Time |
|------|-------|------|
| Grafana Setup | Ahmed | 2-3 hours |
| DVC Integration | Zain | 1-2 hours |
| DagHub DVC | Sanan | 30 minutes |
| Final Review | All | 1 hour |
| **Total** | | **4-6 hours** |

---

## Support Resources

1. **Grafana Setup:** `docs/GRAFANA_SETUP_GUIDE.md`
2. **MinIO Setup:** `docs/MINIO_SETUP_GUIDE.md`
3. **DVC Setup:** `docs/DVC_SETUP_GUIDE.md` (if exists)
4. **Troubleshooting:** `README.md` → Troubleshooting section
5. **Requirements Analysis:** `docs/PROJECT_REQUIREMENTS_ANALYSIS.md`

---

## Final Notes

✅ **You're 83% complete!** The hard work is done. The remaining tasks are primarily configuration and setup, which are straightforward.

🎯 **Focus Areas:**
1. Grafana dashboard (most visible for demonstration)
2. DVC integration (completes Phase I requirements)
3. Final testing and documentation

🚀 **You're almost there!** These final steps will bring you to 100% compliance with all project requirements.

---

*Last Updated: November 26, 2025*

