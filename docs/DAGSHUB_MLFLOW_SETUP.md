# DagHub MLflow Integration Setup Guide

## Overview

This project uses **DagHub** for MLflow experiment tracking. DagHub provides a free, hosted MLflow server that integrates seamlessly with your GitHub repositories.

## Repository Information

- **Repository Owner**: `zainulabidin776`
- **Repository Name**: `bitcoin-price-predictor`
- **MLflow Tracking URI**: `https://dagshub.com/zainulabidin776/bitcoin-price-predictor.mlflow`

## Configuration

### 1. Environment Variables

Ensure your `.env` file contains:

```bash
# DagHub MLflow Configuration
MLFLOW_TRACKING_URI=https://dagshub.com/zainulabidin776/bitcoin-price-predictor.mlflow
MLFLOW_TRACKING_USERNAME=zainulabidin776
MLFLOW_TRACKING_PASSWORD=your_dagshub_token_here
```

### 2. Package Installation

The `dagshub` package is automatically installed in:
- **Airflow containers**: Via `_PIP_ADDITIONAL_REQUIREMENTS` in `docker-compose.yml`
- **Local environment**: Via `requirements.txt`

```bash
pip install dagshub 'mlflow>=2.0.0,<3.0.0'
```

### 3. Code Integration

The DagHub integration is handled automatically in `src/models/train.py`:

```python
import dagshub

# Automatically initialized when MLFLOW_TRACKING_URI contains 'dagshub.com'
dagshub.init(
    repo_owner='zainulabidin776',
    repo_name='bitcoin-price-predictor',
    mlflow=True
)
```

## How It Works

1. **Automatic Detection**: The `CryptoVolatilityTrainer` class automatically detects if you're using DagHub by checking if `MLFLOW_TRACKING_URI` contains `dagshub.com`

2. **Repository Parsing**: It extracts the repository owner and name from the tracking URI

3. **Initialization**: Calls `dagshub.init()` which:
   - Configures MLflow to use DagHub's tracking server
   - Sets up authentication using your credentials
   - Enables seamless experiment logging

4. **Experiment Tracking**: All MLflow operations work normally:
   - `mlflow.start_run()`
   - `mlflow.log_params()`
   - `mlflow.log_metrics()`
   - `mlflow.log_model()`

## Viewing Experiments

### Via DagHub Web UI

1. Go to: https://dagshub.com/zainulabidin776/bitcoin-price-predictor
2. Click on the **"Experiments"** tab
3. View all logged experiments, metrics, parameters, and artifacts

### Via MLflow UI

1. Click **"Go to MLflow UI"** button in DagHub
2. Or access directly: `https://dagshub.com/zainulabidin776/bitcoin-price-predictor.mlflow`

## What Gets Logged

When training runs, the following are automatically logged to DagHub:

- **Parameters**: Hyperparameters (learning_rate, max_depth, etc.)
- **Metrics**: RMSE, MAE, R², MAPE (train, validation, test)
- **Artifacts**:
  - Trained XGBoost model
  - Feature importance plot
  - Scaler (StandardScaler)
  - Feature names JSON
- **Metadata**: Run name, timestamp, dataset size, feature count

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'dagshub'"

**Solution**: Ensure packages are installed in Airflow container:
```bash
# Rebuild containers to install new packages
docker compose down
docker compose up --build
```

### Issue: "Authentication failed"

**Solution**: 
1. Verify `MLFLOW_TRACKING_USERNAME` and `MLFLOW_TRACKING_PASSWORD` in `.env`
2. Get your DagHub token from: https://dagshub.com/user/settings/tokens

### Issue: "Could not parse DagHub URI"

**Solution**: Ensure `MLFLOW_TRACKING_URI` format is:
```
https://dagshub.com/OWNER/REPO.mlflow
```

### Issue: Experiments not appearing in DagHub

**Solution**:
1. Check Airflow logs: `docker compose logs airflow-scheduler`
2. Verify `.env` file is mounted in Airflow container
3. Check that `dagshub.init()` was called successfully (look for initialization logs)

## Manual Testing

Test DagHub integration locally:

```python
import os
from dotenv import load_dotenv
import dagshub
import mlflow

load_dotenv()

# Initialize DagHub
dagshub.init(
    repo_owner='zainulabidin776',
    repo_name='bitcoin-price-predictor',
    mlflow=True
)

# Test logging
with mlflow.start_run():
    mlflow.log_param("test_param", "test_value")
    mlflow.log_metric("test_metric", 42.0)
    print("✓ Successfully logged to DagHub!")
```

## Best Practices

1. **Use Descriptive Run Names**: Include timestamp and model version
   ```python
   run_name=f"airflow_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
   ```

2. **Log All Hyperparameters**: Even defaults, for reproducibility

3. **Version Your Data**: Use DVC to version datasets and reference in MLflow tags

4. **Monitor Experiments**: Regularly check DagHub UI for model performance trends

5. **Tag Production Models**: Use MLflow model registry to mark production-ready models

## Additional Resources

- [DagHub Documentation](https://dagshub.com/docs)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [DagHub MLflow Guide](https://dagshub.com/docs/feature_guide/mlflow_tracking/)

