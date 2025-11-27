# MinIO Setup & Configuration Guide

## Overview

MinIO is an S3-compatible object storage service used in this project for:
- Storing raw and processed data
- DVC remote storage (data versioning)
- Model artifacts backup

---

## What is MinIO?

**MinIO** is a high-performance object storage service that is:
- ✅ **S3-compatible** - Works with any S3-compatible tools (DVC, boto3, etc.)
- ✅ **Lightweight** - Runs in Docker, perfect for development
- ✅ **Production-ready** - Can scale to production workloads

**In this project:**
- MinIO acts as a local S3-compatible storage
- Stores data files for DVC versioning
- Can be replaced with AWS S3, Azure Blob, or other S3-compatible storage in production

---

## Current Setup

MinIO is already configured in `docker-compose.yml`:

```yaml
minio:
  image: minio/minio:latest
  ports:
    - "9000:9000"  # API endpoint
    - "9001:9001"  # Web console
  environment:
    MINIO_ROOT_USER: minioadmin
    MINIO_ROOT_PASSWORD: minioadmin123
  volumes:
    - minio-data:/data
  command: server /data --console-address ":9001"
```

**Access Points:**
- **API Endpoint:** http://localhost:9000
- **Web Console:** http://localhost:9001
- **Credentials:** minioadmin / minioadmin123

---

## Step 1: Access MinIO Console

1. **Open MinIO Console:**
   ```
   http://localhost:9001
   ```

2. **Login:**
   - Username: `minioadmin`
   - Password: `minioadmin123`

3. **You should see:**
   - MinIO dashboard
   - Buckets list (initially empty)

---

## Step 2: Create Bucket for MLOps Data

1. **Create Bucket:**
   - Click **"Create Bucket"** button (top right)
   - **Bucket Name:** `mlops-data`
   - **Region:** Leave default
   - Click **"Create Bucket"**

2. **Verify:**
   - You should see `mlops-data` in the buckets list

---

## Step 3: Configure DVC to Use MinIO

### Option A: Using DVC CLI (Recommended)

1. **Initialize DVC (if not done):**
   ```bash
   dvc init
   ```

2. **Add MinIO as Remote:**
   ```bash
   dvc remote add -d minio s3://mlops-data
   ```

3. **Configure MinIO Endpoint:**
   ```bash
   dvc remote modify minio endpointurl http://localhost:9000
   ```

4. **Configure Credentials:**
   ```bash
   dvc remote modify minio access_key_id minioadmin
   dvc remote modify minio secret_access_key minioadmin123
   ```

5. **Verify Configuration:**
   ```bash
   dvc remote list
   # Should show: minio
   
   dvc remote modify minio --list
   # Should show all settings
   ```

### Option B: Manual Configuration

Edit `.dvc/config` file:

```ini
['remote "minio"']
url = s3://mlops-data
endpointurl = http://localhost:9000
access_key_id = minioadmin
secret_access_key = minioadmin123
```

---

## Step 4: Test DVC with MinIO

1. **Add Data File to DVC:**
   ```bash
   # Example: Add processed data
   dvc add data/processed/crypto_processed_*.csv
   ```

2. **Push to MinIO:**
   ```bash
   dvc push
   ```

3. **Verify in MinIO:**
   - Go to MinIO Console: http://localhost:9001
   - Open `mlops-data` bucket
   - You should see `.dvc` files and data files

---

## Step 5: Configure in Airflow DAG (Optional)

The `version_with_dvc()` task in the DAG can be updated to:

```python
def version_with_dvc(**context):
    """Task 5: Version processed data with DVC"""
    import subprocess
    import os
    
    processed_path = context['ti'].xcom_pull(
        key='processed_data_path', 
        task_ids='transform_data'
    )
    
    if not processed_path:
        raise ValueError("No processed data path found")
    
    # Add to DVC
    subprocess.run(['dvc', 'add', processed_path], check=True)
    
    # Push to MinIO
    subprocess.run(['dvc', 'push'], check=True)
    
    logger.info(f"✓ Data versioned and pushed to MinIO: {processed_path}")
    return True
```

---

## Using MinIO with Python (boto3)

If you need to access MinIO programmatically:

```python
import boto3
from botocore.client import Config

# Create S3 client
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin123',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

# List buckets
buckets = s3_client.list_buckets()
print(buckets)

# Upload file
s3_client.upload_file(
    'local_file.csv',
    'mlops-data',
    'remote_file.csv'
)

# Download file
s3_client.download_file(
    'mlops-data',
    'remote_file.csv',
    'local_file.csv'
)
```

---

## MinIO vs Production S3

### Development (Current Setup)
- ✅ MinIO running in Docker
- ✅ Local storage
- ✅ Free, no cost
- ✅ Perfect for testing

### Production (Future)
- Replace MinIO with:
  - AWS S3
  - Azure Blob Storage
  - Google Cloud Storage
  - Or keep MinIO (it's production-ready!)

**Migration:** Just change the endpoint URL and credentials in DVC config.

---

## Troubleshooting

### Issue: "Access Denied" when pushing to DVC

**Solution:**
- Verify credentials in `.dvc/config`
- Check bucket exists in MinIO
- Verify MinIO is running: `docker compose ps minio`

### Issue: "Connection refused" to MinIO

**Solution:**
- Check MinIO is running: `docker compose ps minio`
- Verify endpoint URL: `http://localhost:9000`
- Check Docker network: Both services should be in same network

### Issue: Bucket not found

**Solution:**
- Create bucket in MinIO Console: http://localhost:9001
- Verify bucket name matches DVC config
- Check bucket permissions (should be public for DVC)

---

## Best Practices

1. **Bucket Organization:**
   - Use separate buckets for different data types:
     - `mlops-data-raw` - Raw data
     - `mlops-data-processed` - Processed data
     - `mlops-models` - Model artifacts

2. **Data Lifecycle:**
   - Set up retention policies
   - Archive old data
   - Clean up unused files

3. **Security:**
   - Change default credentials in production
   - Use IAM policies for access control
   - Enable encryption at rest

---

## Summary

✅ **MinIO is configured and running**  
✅ **Bucket created: `mlops-data`**  
✅ **DVC can use MinIO as remote storage**  
✅ **Ready for data versioning**

**Next Steps:**
- Complete DVC integration in Airflow DAG
- Test data versioning workflow
- Verify .dvc files are tracked in Git

---

*Guide created: November 26, 2025*

