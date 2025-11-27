# GitHub Actions CI/CD Setup Guide

This guide explains how to configure GitHub Actions workflows for the MLOps project.

---

## 📋 Required Secrets

To enable CI/CD pipelines, you need to configure the following secrets in your GitHub repository:

### How to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret below

### Required Secrets

#### 1. MLflow/DagHub Secrets (Optional but Recommended)

```
MLFLOW_TRACKING_URI
```
- **Value:** `https://dagshub.com/zainulabidin776/bitcoin-price-predictor.mlflow`
- **Purpose:** MLflow tracking server URI
- **Required for:** Model fetching in production CD pipeline

```
MLFLOW_TRACKING_USERNAME
```
- **Value:** `zainulabidin776`
- **Purpose:** DagHub username
- **Required for:** MLflow authentication

```
MLFLOW_TRACKING_PASSWORD
```
- **Value:** Your DagHub token/password
- **Purpose:** DagHub authentication
- **Required for:** MLflow authentication

#### 2. Docker Hub Secrets (Optional but Recommended)

```
DOCKER_USERNAME
```
- **Value:** Your Docker Hub username (e.g., `itsmezayynn`)
- **Purpose:** Docker image registry
- **Required for:** Pushing Docker images

```
DOCKER_PASSWORD
```
- **Value:** Your Docker Hub password or access token
- **Purpose:** Docker Hub authentication
- **Required for:** Pushing Docker images

---

## 🔄 Workflow Overview

### 1. Development CI (`dev-ci.yml`)

**Triggers:**
- Pull requests to `dev` branch
- Pushes to `dev` branch

**Jobs:**
- **Code Quality:** Flake8 linting, Bandit security scan, Safety dependency check
- **Unit Tests:** Run pytest tests (if available)
- **Summary:** Report overall status

**Secrets Required:** None (works without secrets)

---

### 2. Test Branch CI (`test-ci.yml`)

**Triggers:**
- Pull requests to `test` branch

**Jobs:**
- **Model Training:** Full pipeline execution (extract → train)
- **Model Comparison:** Compare new model with baseline using CML
- **PR Comment:** Post comparison report in PR

**Secrets Required:**
- `MLFLOW_TRACKING_URI`
- `MLFLOW_TRACKING_USERNAME`
- `MLFLOW_TRACKING_PASSWORD`

**Note:** If secrets are not set, the workflow will still run but MLflow tracking will be skipped.

---

### 3. Production CD (`prod-cd.yml`)

**Triggers:**
- Pushes to `master` branch
- Pull requests to `master` branch

**Jobs:**
- **Build and Deploy:**
  - Fetch model from MLflow
  - Build Docker image
  - Test Docker image
  - Push to Docker Hub (if credentials set)
  - Create GitHub release
- **Notification:** Send deployment status

**Secrets Required:**
- `MLFLOW_TRACKING_URI` (optional)
- `MLFLOW_TRACKING_USERNAME` (optional)
- `MLFLOW_TRACKING_PASSWORD` (optional)
- `DOCKER_USERNAME` (optional)
- `DOCKER_PASSWORD` (optional)

**Note:** The workflow is designed to work even without secrets. It will:
- Build Docker images locally (not push)
- Use default model version if MLflow is not configured
- Skip Docker Hub push if credentials are missing

---

## ✅ Workflow Status

### Current Status

All workflows have been updated to:
- ✅ Handle missing secrets gracefully
- ✅ Use `continue-on-error` for optional steps
- ✅ Provide clear warnings when secrets are missing
- ✅ Not fail the entire workflow if optional steps fail

### What Changed

1. **Error Handling:**
   - Added `continue-on-error: true` for optional steps
   - Added conditional checks for secrets
   - Improved error messages

2. **Notification Job:**
   - Changed from `exit 1` to warnings
   - No longer fails the workflow unnecessarily

3. **Docker Build:**
   - Works without Docker Hub credentials
   - Builds image locally if credentials not set

4. **MLflow Integration:**
   - Gracefully handles missing MLflow credentials
   - Uses default version if model fetch fails

---

## 🚀 Testing Workflows

### Test Development CI

```bash
# Create a feature branch
git checkout -b feature/test-ci

# Make a small change
echo "# Test" >> README.md

# Commit and push
git add README.md
git commit -m "Test: CI pipeline"
git push origin feature/test-ci

# Create PR to dev branch
```

### Test Production CD

```bash
# Merge to master (or create PR)
git checkout master
git merge dev
git push origin master
```

---

## 🔍 Troubleshooting

### Workflow Fails with "Secret not found"

**Solution:** The workflows are now designed to work without secrets. If you see warnings, that's expected. The workflow will continue.

### Docker Build Fails

**Check:**
1. Is `Dockerfile` present in root directory?
2. Are all dependencies in `requirements.txt`?
3. Check the build logs for specific errors

### MLflow Model Fetch Fails

**Solution:** This is expected if:
- MLflow secrets are not set
- No production model exists yet

The workflow will use "latest" as default version.

### Notification Job Fails

**Solution:** This has been fixed. The notification job now only warns, it doesn't fail the workflow.

---

## 📊 Workflow Status Indicators

- ✅ **Green:** All checks passed
- ⚠️ **Yellow:** Some optional checks had warnings (workflow still passes)
- ❌ **Red:** Required checks failed (workflow fails)

---

## 🎯 Next Steps

1. **Add Secrets (Optional):**
   - Go to repository Settings → Secrets
   - Add MLflow and Docker Hub credentials
   - Workflows will use them automatically

2. **Test Workflows:**
   - Create a test PR to `dev` branch
   - Check Actions tab for results

3. **Monitor:**
   - Check Actions tab regularly
   - Review any warnings or errors
   - Update secrets as needed

---

## 📝 Notes

- All workflows are designed to be **fault-tolerant**
- Missing secrets will generate warnings but won't fail workflows
- You can add secrets later and workflows will automatically use them
- The notification job is informational only and won't fail the workflow

---

*Last Updated: November 26, 2025*

