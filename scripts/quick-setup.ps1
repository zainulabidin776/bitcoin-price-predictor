# Quick Setup Script - Simplified Version
# This script helps you set up Prometheus, Grafana, and MinIO

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Quick Service Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Generate API traffic
Write-Host "[1] Generating API traffic..." -ForegroundColor Yellow
for ($i = 1; $i -le 3; $i++) {
    try {
        Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5 | Out-Null
        Write-Host "  Health check ${i}: OK" -ForegroundColor Green
    } catch {
        Write-Host "  Health check ${i}: Failed" -ForegroundColor Red
    }
    Start-Sleep -Seconds 1
}

# Prediction call
try {
    $body = '{"features": [0.05, -0.02, 0.03, 0.01, -0.01, 0.04, 1.002, 0.998, 1.001, 0.0001, -0.0002, 0.0003, 0.0004, 0.0005, 0.015, 0.012, 0.001, 0.003, 0.002, 0.003, 0.001, 45.5, 0.707, 0.707, -0.434, 0.901, 0, 120.5, 50000, 49800, 49950, 49700, 50100, 0.0003, 0.0004, 0.0002]}'
    Invoke-WebRequest -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing -TimeoutSec 5 | Out-Null
    Write-Host "  Prediction call: OK" -ForegroundColor Green
} catch {
    Write-Host "  Prediction call: Failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Waiting 15 seconds for Prometheus to scrape..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Instructions" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "GRAFANA:" -ForegroundColor Yellow
Write-Host "  1. Open: http://localhost:3000" -ForegroundColor White
Write-Host "  2. Login: admin / admin" -ForegroundColor White
Write-Host "  3. Settings -> Data sources -> Add Prometheus" -ForegroundColor White
Write-Host "  4. URL: http://prometheus:9090" -ForegroundColor White
Write-Host "  5. Save & test" -ForegroundColor White
Write-Host ""
Write-Host "MINIO:" -ForegroundColor Yellow
Write-Host "  1. Open: http://localhost:9001" -ForegroundColor White
Write-Host "  2. Login: minioadmin / minioadmin123" -ForegroundColor White
Write-Host "  3. Create bucket: mlops-data" -ForegroundColor White
Write-Host ""
Write-Host "PROMETHEUS:" -ForegroundColor Yellow
Write-Host "  1. Open: http://localhost:9090" -ForegroundColor White
Write-Host "  2. Check Status -> Targets" -ForegroundColor White
Write-Host "  3. Try query: sum(http_requests_total)" -ForegroundColor White
Write-Host ""

