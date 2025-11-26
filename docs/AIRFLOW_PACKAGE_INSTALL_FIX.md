# Airflow Package Installation Fix

## Problem

The `airflow-init` service was failing with exit code 1 during package installation when using `_PIP_ADDITIONAL_REQUIREMENTS` in docker-compose.yml.

## Root Cause

Using `_PIP_ADDITIONAL_REQUIREMENTS` is fragile and can fail due to:
- Missing system dependencies (gcc, g++, build tools)
- Version conflicts
- Network timeouts
- Permission issues
- Long installation times causing timeouts

## Solution

Created a **custom Airflow Dockerfile** (`Dockerfile.airflow`) that pre-installs all required packages during image build. This is the **recommended production approach** by Apache Airflow.

## Files Changed

1. **`Dockerfile.airflow`** (NEW)
   - Extends `apache/airflow:2.7.3-python3.9`
   - Installs system dependencies (gcc, g++, build-essential)
   - Pre-installs all Python packages during build
   - More reliable and faster than runtime installation

2. **`docker-compose.yml`**
   - Removed `_PIP_ADDITIONAL_REQUIREMENTS` (no longer needed)
   - Added `build` section to use custom Dockerfile
   - Changed from `image:` to `build:` for Airflow services

## How to Use

### First Time Setup

```bash
# Rebuild Airflow image with packages pre-installed
docker compose build airflow-webserver airflow-scheduler airflow-init

# Start all services
docker compose up -d
```

### After Code Changes

```bash
# If you add new packages to Dockerfile.airflow, rebuild:
docker compose build airflow-webserver airflow-scheduler airflow-init
docker compose up -d
```

## Installed Packages

The custom image includes:
- `pandas==2.0.3`
- `numpy==1.24.3`
- `scikit-learn==1.3.0`
- `xgboost==2.0.0`
- `mlflow>=2.0.0,<3.0.0`
- `requests==2.31.0`
- `python-dotenv==1.0.0`
- `ydata-profiling==4.5.1`
- `dagshub`

## Benefits

✅ **Reliable**: Packages installed during build, not runtime  
✅ **Faster**: No installation delay on container startup  
✅ **Production-ready**: Follows Airflow best practices  
✅ **Reproducible**: Same packages every time  
✅ **No timeouts**: Build happens once, not on every start  

## Troubleshooting

### Issue: Build fails with "package not found"

**Solution**: Check package name and version in `Dockerfile.airflow`. Some packages may need system dependencies.

### Issue: Image takes long to build

**Solution**: This is normal on first build. Subsequent builds use Docker cache and are faster.

### Issue: Packages still missing after rebuild

**Solution**: 
1. Force rebuild without cache: `docker compose build --no-cache airflow-webserver`
2. Verify packages: `docker compose exec airflow-scheduler pip list | grep pandas`

## Verification

After starting services, verify packages are installed:

```bash
# Check packages in scheduler
docker compose exec airflow-scheduler pip list | findstr "pandas ydata-profiling dagshub"

# Expected output:
# dagshub          X.X.X
# pandas           2.0.3
# ydata-profiling  4.5.1
```

## Next Steps

1. Rebuild Airflow services: `docker compose build airflow-webserver airflow-scheduler airflow-init`
2. Start services: `docker compose up -d`
3. Wait 2-3 minutes for initialization
4. Verify Airflow UI: http://localhost:8081
5. Run your DAG - `transform_data` task should now work!

