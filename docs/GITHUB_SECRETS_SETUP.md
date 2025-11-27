# GitHub Secrets Setup Guide
## Required Secrets for CI/CD Workflows

**Important:** GitHub Secrets are configured in the repository settings, NOT in the `.env` file. The `.env` file is for local Docker Compose services.

---

## 🔐 Required Secrets for Production CD Pipeline

### 1. MLflow/DagHub Secrets (Optional but Recommended)

These are already in your `.env` file for local use. You need to add them to GitHub Secrets for the workflow:

#### `MLFLOW_TRACKING_URI`
- **Value:** `https://dagshub.com/zainulabidin776/bitcoin-price-predictor.mlflow`
- **Purpose:** MLflow tracking server URI
- **Required for:** Fetching production model version
- **Status:** ✅ You have this in `.env`

#### `MLFLOW_TRACKING_USERNAME`
- **Value:** `zainulabidin776`
- **Purpose:** DagHub username
- **Required for:** MLflow authentication
- **Status:** ✅ You have this in `.env`

#### `MLFLOW_TRACKING_PASSWORD`
- **Value:** `4844315bd4005fdc92de947532a3ed2347d0028e`
- **Purpose:** DagHub token/password
- **Required for:** MLflow authentication
- **Status:** ✅ You have this in `.env`

---

### 2. Docker Hub Secrets (Optional but Recommended)

These are **NOT** in your `.env` file. You need to add them to GitHub Secrets:

#### `DOCKER_USERNAME`
- **Value:** Your Docker Hub username (e.g., `itsmezayynn`)
- **Purpose:** Docker Hub authentication
- **Required for:** Pushing Docker images to Docker Hub
- **Status:** ❌ **MISSING** - Need to add to GitHub Secrets

#### `DOCKER_PASSWORD`
- **Value:** Your Docker Hub password or access token
- **Purpose:** Docker Hub authentication
- **Required for:** Pushing Docker images to Docker Hub
- **Status:** ❌ **MISSING** - Need to add to GitHub Secrets

**Note:** The workflow will work without these, but it won't push images to Docker Hub.

---

## 📋 How to Add Secrets to GitHub

### Step 1: Go to Repository Settings

1. Open your GitHub repository: `https://github.com/zainulabidin776/bitcoin-price-predictor`
2. Click **Settings** (top right)
3. In the left sidebar, click **Secrets and variables** → **Actions**

### Step 2: Add Each Secret

Click **New repository secret** and add:

#### Secret 1: MLFLOW_TRACKING_URI
- **Name:** `MLFLOW_TRACKING_URI`
- **Value:** `https://dagshub.com/zainulabidin776/bitcoin-price-predictor.mlflow`
- Click **Add secret**

#### Secret 2: MLFLOW_TRACKING_USERNAME
- **Name:** `MLFLOW_TRACKING_USERNAME`
- **Value:** `zainulabidin776`
- Click **Add secret**

#### Secret 3: MLFLOW_TRACKING_PASSWORD
- **Name:** `MLFLOW_TRACKING_PASSWORD`
- **Value:** `4844315bd4005fdc92de947532a3ed2347d0028e`
- Click **Add secret**

#### Secret 4: DOCKER_USERNAME
- **Name:** `DOCKER_USERNAME`
- **Value:** Your Docker Hub username (e.g., `itsmezayynn`)
- Click **Add secret**

#### Secret 5: DOCKER_PASSWORD
- **Name:** `DOCKER_PASSWORD`
- **Value:** Your Docker Hub password or access token
- Click **Add secret**

---

## ✅ Verification Checklist

After adding secrets, verify:

- [ ] `MLFLOW_TRACKING_URI` is set
- [ ] `MLFLOW_TRACKING_USERNAME` is set
- [ ] `MLFLOW_TRACKING_PASSWORD` is set
- [ ] `DOCKER_USERNAME` is set (optional)
- [ ] `DOCKER_PASSWORD` is set (optional)

---

## 🚀 What Happens With/Without Secrets

### With All Secrets Configured:
- ✅ Fetches production model from MLflow
- ✅ Builds Docker image
- ✅ Tests Docker image
- ✅ **Pushes to Docker Hub**
- ✅ Creates GitHub release
- ✅ Full deployment pipeline

### Without Docker Hub Secrets:
- ✅ Fetches production model from MLflow
- ✅ Builds Docker image locally
- ✅ Tests Docker image
- ⚠️ **Skips Docker Hub push** (shows warning)
- ⚠️ **Skips GitHub release** (requires Docker Hub)
- ✅ Deployment summary still works

### Without MLflow Secrets:
- ⚠️ Uses default "latest" model version
- ✅ Builds Docker image
- ✅ Tests Docker image
- ✅ Pushes to Docker Hub (if credentials set)
- ✅ Creates GitHub release (if Docker Hub set)

---

## 🔒 Security Notes

1. **Never commit secrets to Git:**
   - Secrets are encrypted in GitHub
   - Only visible to repository admins
   - Not accessible in workflow logs

2. **Use Access Tokens:**
   - For Docker Hub, prefer access tokens over passwords
   - More secure and revocable
   - Create at: https://hub.docker.com/settings/security

3. **Rotate Secrets Regularly:**
   - Update passwords/tokens periodically
   - Revoke old tokens when updating

---

## 📝 Quick Reference

### Your Current .env (Local Development):
```bash
# MLflow - ✅ Present
MLFLOW_TRACKING_URI=https://dagshub.com/zainulabidin776/bitcoin-price-predictor.mlflow
MLFLOW_TRACKING_USERNAME=zainulabidin776
MLFLOW_TRACKING_PASSWORD=4844315bd4005fdc92de947532a3ed2347d0028e

# Docker Hub - ❌ Missing (not needed for local, but needed for CI/CD)
# DOCKER_USERNAME=your-username
# DOCKER_PASSWORD=your-password
```

### GitHub Secrets Needed:
1. ✅ `MLFLOW_TRACKING_URI` - Copy from .env
2. ✅ `MLFLOW_TRACKING_USERNAME` - Copy from .env
3. ✅ `MLFLOW_TRACKING_PASSWORD` - Copy from .env
4. ❌ `DOCKER_USERNAME` - **Need to add** (your Docker Hub username)
5. ❌ `DOCKER_PASSWORD` - **Need to add** (your Docker Hub password/token)

---

## 🎯 Next Steps

1. **Add MLflow Secrets:**
   - Copy values from your `.env` file
   - Add to GitHub Secrets

2. **Add Docker Hub Secrets:**
   - Get your Docker Hub username
   - Create access token or use password
   - Add to GitHub Secrets

3. **Test Workflow:**
   - Push to `master` branch
   - Check Actions tab
   - Verify workflow runs successfully

---

*Last Updated: November 26, 2025*

