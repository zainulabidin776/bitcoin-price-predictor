# Complete Service Configuration Script
# This script helps configure Prometheus, Grafana, and MinIO step by step

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Complete MLOps Service Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to test URL
function Test-Url {
    param($Url, $ServiceName)
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        return $true
    } catch {
        Write-Host "  [FAIL] $ServiceName not accessible at $Url" -ForegroundColor Red
        return $false
    }
}

# Step 1: Verify Services Running
Write-Host "[STEP 1] Verifying Services..." -ForegroundColor Yellow
Write-Host ""

$services = @(
    @{Name="API"; Port=8000; Url="http://localhost:8000/health"},
    @{Name="Prometheus"; Port=9090; Url="http://localhost:9090"},
    @{Name="Grafana"; Port=3000; Url="http://localhost:3000"},
    @{Name="MinIO Console"; Port=9001; Url="http://localhost:9001/minio/health/live"}
)

foreach ($service in $services) {
    if (Test-Url -Url $service.Url -ServiceName $service.Name) {
        Write-Host "  [OK] $($service.Name) is running on port $($service.Port)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $($service.Name) is NOT running" -ForegroundColor Red
        Write-Host "    Start with: docker compose up -d $($service.Name.ToLower())" -ForegroundColor Yellow
    }
}

Write-Host ""

# Step 2: Generate API Traffic
Write-Host "[STEP 2] Generating API Traffic for Metrics..." -ForegroundColor Yellow
Write-Host ""

$apiCalls = 0
for ($i = 1; $i -le 5; $i++) {
    try {
        # Health check
        Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5 | Out-Null
        
        # Prediction request
        $body = @{
            features = @(0.05, -0.02, 0.03, 0.01, -0.01, 0.04, 1.002, 0.998, 1.001, 0.0001, -0.0002, 0.0003, 0.0004, 0.0005, 0.015, 0.012, 0.001, 0.003, 0.002, 0.003, 0.001, 45.5, 0.707, 0.707, -0.434, 0.901, 0, 120.5, 50000, 49800, 49950, 49700, 50100, 0.0003, 0.0004, 0.0002)
        } | ConvertTo-Json
        
        Invoke-WebRequest -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing -TimeoutSec 5 | Out-Null
        $apiCalls++
        Write-Host "  [OK] API call $i successful" -ForegroundColor Green
        Start-Sleep -Seconds 2
    } catch {
        Write-Host "  [WARN] API call $i failed: $_" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "  Generated $apiCalls API calls. Waiting 15 seconds for Prometheus to scrape..." -ForegroundColor Cyan
Start-Sleep -Seconds 15
Write-Host ""

# Step 3: Check Prometheus Targets
Write-Host "[STEP 3] Checking Prometheus Targets..." -ForegroundColor Yellow
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "http://localhost:9090/api/v1/targets" -UseBasicParsing -TimeoutSec 5
    $targets = ($response.Content | ConvertFrom-Json).data.activeTargets
    
    foreach ($target in $targets) {
        if ($target.health -eq "up") {
            $status = "[OK]"
            $color = "Green"
        } else {
            $status = "[FAIL]"
            $color = "Red"
        }
        Write-Host "  $status $($target.job): $($target.scrapeUrl)" -ForegroundColor $color
        Write-Host "    Health: $($target.health)" -ForegroundColor $color
        if ($target.lastError) {
            Write-Host "    Error: $($target.lastError)" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "  ✗ Could not check Prometheus targets" -ForegroundColor Red
}

Write-Host ""

# Step 4: Test Prometheus Queries
Write-Host "[STEP 4] Testing Prometheus Queries..." -ForegroundColor Yellow
Write-Host ""

$queries = @(
    @{Name="Total Requests"; Query='sum(http_requests_total)'},
    @{Name="Prediction Latency"; Query='histogram_quantile(0.95, rate(prediction_latency_seconds_bucket[5m]))'},
    @{Name="Data Drift Ratio"; Query='data_drift_ratio'}
)

foreach ($query in $queries) {
    try {
        $encodedQuery = [System.Web.HttpUtility]::UrlEncode($query.Query)
        $url = "http://localhost:9090/api/v1/query?query=$encodedQuery"
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
        $result = ($response.Content | ConvertFrom-Json).data.result
        
        if ($result.Count -gt 0) {
            Write-Host "  [OK] $($query.Name): Data available" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] $($query.Name): No data yet (make more API calls)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  [FAIL] $($query.Name): Query failed" -ForegroundColor Red
    }
}

Write-Host ""

# Step 5: Instructions
Write-Host "[STEP 5] Configuration Instructions" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GRAFANA SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Open Grafana: http://localhost:3000" -ForegroundColor White
Write-Host "2. Login: admin / admin" -ForegroundColor White
Write-Host "3. Add Prometheus Data Source:" -ForegroundColor White
Write-Host "   - Click ⚙️ (Settings) → Data sources" -ForegroundColor Gray
Write-Host "   - Click 'Add data source'" -ForegroundColor Gray
Write-Host "   - Select 'Prometheus'" -ForegroundColor Gray
Write-Host "   - URL: http://prometheus:9090" -ForegroundColor Gray
Write-Host "   - Click 'Save & test'" -ForegroundColor Gray
Write-Host "   - Should see: [OK] Data source is working" -ForegroundColor Green
Write-Host ""
Write-Host "4. Create Dashboard:" -ForegroundColor White
Write-Host "   - Click + → Create dashboard" -ForegroundColor Gray
Write-Host "   - Add panel → Add visualization" -ForegroundColor Gray
Write-Host "   - Use queries from docs/GRAFANA_SETUP_GUIDE.md" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MINIO SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Open MinIO Console: http://localhost:9001" -ForegroundColor White
Write-Host "2. Login: minioadmin / minioadmin123" -ForegroundColor White
Write-Host "3. Create Bucket:" -ForegroundColor White
Write-Host "   - Click 'Create Bucket'" -ForegroundColor Gray
Write-Host "   - Name: mlops-data" -ForegroundColor Gray
Write-Host "   - Click 'Create Bucket'" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Configure DVC:" -ForegroundColor White
Write-Host "   dvc remote add -d minio s3://mlops-data" -ForegroundColor Gray
Write-Host "   dvc remote modify minio endpointurl http://localhost:9000" -ForegroundColor Gray
Write-Host "   dvc remote modify minio access_key_id minioadmin" -ForegroundColor Gray
Write-Host "   dvc remote modify minio secret_access_key minioadmin123" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test Prometheus:" -ForegroundColor White
Write-Host "  http://localhost:9090" -ForegroundColor Gray
Write-Host "  Try query: sum(http_requests_total)" -ForegroundColor Gray
Write-Host ""
Write-Host "Test Grafana:" -ForegroundColor White
Write-Host "  http://localhost:3000" -ForegroundColor Gray
Write-Host "  Create dashboard with Prometheus queries" -ForegroundColor Gray
Write-Host ""
Write-Host "Test MinIO:" -ForegroundColor White
Write-Host "  http://localhost:9001" -ForegroundColor Gray
Write-Host "  Verify bucket 'mlops-data' exists" -ForegroundColor Gray
Write-Host ""

