# MLOps Monitoring Setup Script
# This script helps configure Prometheus, Grafana, and MinIO

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MLOps Monitoring Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Services
Write-Host "[1/6] Checking Docker services..." -ForegroundColor Yellow
$services = docker compose ps --format json | ConvertFrom-Json
$running = $services | Where-Object { $_.State -eq "running" }

Write-Host "Running services:" -ForegroundColor Green
$running | ForEach-Object { Write-Host "  ✓ $($_.Service)" -ForegroundColor Green }

# Step 2: Check API Metrics
Write-Host ""
Write-Host "[2/6] Checking API metrics endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/metrics" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ API metrics endpoint is accessible" -ForegroundColor Green
        $metrics = $response.Content
        if ($metrics -match "http_requests_total") {
            Write-Host "  ✓ Metrics are being exposed" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ Metrics endpoint exists but no metrics found" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  ✗ API metrics endpoint not accessible: $_" -ForegroundColor Red
    Write-Host "  Make sure API service is running: docker compose ps api" -ForegroundColor Yellow
}

# Step 3: Check Prometheus
Write-Host ""
Write-Host "[3/6] Checking Prometheus..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9090/api/v1/targets" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ Prometheus is accessible" -ForegroundColor Green
        $targets = ($response.Content | ConvertFrom-Json).data.activeTargets
        Write-Host "  Prometheus targets:" -ForegroundColor Cyan
        foreach ($target in $targets) {
            $status = if ($target.health -eq "up") { "✓" } else { "✗" }
            $color = if ($target.health -eq "up") { "Green" } else { "Red" }
            Write-Host "    $status $($target.job): $($target.scrapeUrl) - $($target.health)" -ForegroundColor $color
        }
    }
} catch {
    Write-Host "  ✗ Prometheus not accessible: $_" -ForegroundColor Red
}

# Step 4: Generate API Traffic
Write-Host ""
Write-Host "[4/6] Generating API traffic for metrics..." -ForegroundColor Yellow
try {
    # Health check
    Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5 | Out-Null
    Write-Host "  ✓ Health check successful" -ForegroundColor Green
    
    # Prediction request
    $body = @{
        features = @(0.05, -0.02, 0.03, 0.01, -0.01, 0.04, 1.002, 0.998, 1.001, 0.0001, -0.0002, 0.0003, 0.0004, 0.0005, 0.015, 0.012, 0.001, 0.003, 0.002, 0.003, 0.001, 45.5, 0.707, 0.707, -0.434, 0.901, 0, 120.5, 50000, 49800, 49950, 49700, 50100, 0.0003, 0.0004, 0.0002)
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ✓ Prediction request successful" -ForegroundColor Green
    Write-Host "  Wait 10-15 seconds for Prometheus to scrape metrics..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
} catch {
    Write-Host "  ⚠ Could not generate traffic: $_" -ForegroundColor Yellow
    Write-Host "  This is okay, you can test manually later" -ForegroundColor Yellow
}

# Step 5: MinIO Setup Instructions
Write-Host ""
Write-Host "[5/6] MinIO Setup Instructions" -ForegroundColor Yellow
Write-Host "  1. Open MinIO Console: http://localhost:9001" -ForegroundColor Cyan
Write-Host "  2. Login: minioadmin / minioadmin123" -ForegroundColor Cyan
Write-Host "  3. Create bucket: mlops-data" -ForegroundColor Cyan
Write-Host "  4. Bucket is ready for DVC data versioning" -ForegroundColor Cyan

# Step 6: Grafana Setup Instructions
Write-Host ""
Write-Host "[6/6] Grafana Setup Instructions" -ForegroundColor Yellow
Write-Host "  1. Open Grafana: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  2. Login: admin / admin" -ForegroundColor Cyan
Write-Host "  3. Add Prometheus data source:" -ForegroundColor Cyan
Write-Host "     - URL: http://prometheus:9090" -ForegroundColor White
Write-Host "     - Click 'Save & test'" -ForegroundColor White
Write-Host "  4. Create dashboard (see docs/GRAFANA_SETUP_GUIDE.md)" -ForegroundColor Cyan

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Check Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Configure Grafana (see docs/GRAFANA_SETUP_GUIDE.md)" -ForegroundColor White
Write-Host "  2. Set up MinIO bucket (see docs/MINIO_SETUP_GUIDE.md)" -ForegroundColor White
Write-Host "  3. Test Prometheus queries: http://localhost:9090" -ForegroundColor White
Write-Host ""

