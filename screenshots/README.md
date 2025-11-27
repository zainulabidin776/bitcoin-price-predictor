# Screenshots Directory

This directory contains screenshots for the project documentation.

## Required Screenshots

Please add the following screenshots to this directory:

### Infrastructure (3 screenshots)
1. `docker-services.png` - Docker Compose services status
2. `airflow-dag.png` - Airflow DAG showing all tasks completed
3. `service-dependencies.png` - Service dependency graph

### Data Pipeline (3 screenshots)
4. `data-extraction.png` - Data extraction logs/output
5. `quality-check.png` - Quality check results showing all gates passed
6. `feature-engineering.png` - Feature engineering output (36 features)

### Model Training (3 screenshots)
7. `mlflow-experiments.png` - MLflow experiments in DagHub
8. `model-metrics.png` - Model performance metrics (RMSE, MAE, R²)
9. `dagshub-hub.png` - DagHub showing integrated components

### CI/CD (2 screenshots)
10. `github-actions.png` - GitHub Actions workflow execution
11. `cml-comparison.png` - CML model comparison report in PR

### API (3 screenshots)
12. `fastapi-docs.png` - FastAPI Swagger documentation
13. `api-health.png` - API health check response
14. `prediction-endpoint.png` - Prediction endpoint with drift detection

### Monitoring (5 screenshots)
15. `prometheus-targets.png` - Prometheus targets showing API as UP
16. `prometheus-queries.png` - Prometheus query results
17. `grafana-dashboard.png` - Grafana monitoring dashboard
18. `grafana-datasource.png` - Grafana Prometheus data source config
19. `grafana-alerts.png` - Grafana alert rules

### Storage (2 screenshots)
20. `minio-console.png` - MinIO console with mlops-data bucket
21. `dvc-versioning.png` - DVC data versioning status

### Architecture (1 screenshot)
22. `system-overview.png` - Complete system architecture diagram

## Screenshot Guidelines

- **Format:** PNG or JPG
- **Resolution:** Minimum 1920x1080 (Full HD)
- **Naming:** Use exact names listed above
- **Content:** Clear, readable, showing relevant information
- **Annotations:** Optional - can add arrows/boxes to highlight key areas

## How to Take Screenshots

### Docker Services
```powershell
# Run this command, then screenshot
docker compose ps
```

### Airflow DAG
1. Open: http://localhost:8081
2. Find DAG: `crypto_volatility_pipeline`
3. Click on DAG
4. Screenshot the graph view

### Prometheus
1. Open: http://localhost:9090
2. Status → Targets (for targets screenshot)
3. Graph tab with query (for queries screenshot)

### Grafana
1. Open: http://localhost:3000
2. Settings → Data sources (for datasource screenshot)
3. Dashboard view (for dashboard screenshot)
4. Alerting → Alert rules (for alerts screenshot)

### MinIO
1. Open: http://localhost:9001
2. Login and show bucket list
3. Screenshot bucket contents

### FastAPI
1. Open: http://localhost:8000/docs
2. Screenshot Swagger UI
3. Test endpoints and screenshot responses

---

*Add your screenshots here and they will be automatically included in the LaTeX report.*

