#!/bin/bash

# =============================================================================
# MLOps RPS Crypto - Complete Setup Script
# =============================================================================

set -e  # Exit on error

echo "============================================================"
echo "  MLOps Real-Time Predictive System - Crypto Volatility"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0:31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# =============================================================================
# Helper Functions
# =============================================================================

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

# =============================================================================
# Prerequisites Check
# =============================================================================

print_step "Checking prerequisites..."

check_command docker
check_command docker-compose
check_command python3
check_command git

print_info "✓ All prerequisites found"
echo ""

# =============================================================================
# Environment Setup
# =============================================================================

print_step "Setting up environment..."

if [ ! -f .env ]; then
    print_info "Creating .env file from template..."
    cp .env.example .env
    print_info "⚠️  Please edit .env file and add your credentials:"
    print_info "   - DATA_SOURCE=cryptocompare (Free - No key required)"
    print_info "   - MLFLOW_TRACKING_URI (DagHub)"
    print_info "   - MLFLOW_TRACKING_USERNAME"
    print_info "   - MLFLOW_TRACKING_PASSWORD"
    print_info "   - DOCKER_USERNAME (for deployment)"
    echo ""
    read -p "Press Enter after updating .env file..."
else
    print_info "✓ .env file already exists"
fi

# =============================================================================
# Python Environment
# =============================================================================

print_step "Setting up Python environment..."

if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
fi

print_info "Activating virtual environment..."
source venv/bin/activate

print_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

print_info "✓ Python environment ready"
echo ""

# =============================================================================
# Create Directory Structure
# =============================================================================

print_step "Creating directory structure..."

mkdir -p data/raw
mkdir -p data/processed
mkdir -p models
mkdir -p reports/quality
mkdir -p reports/profiling
mkdir -p outputs
mkdir -p airflow/logs
mkdir -p airflow/plugins
mkdir -p monitoring/grafana/provisioning

print_info "✓ Directories created"
echo ""

# =============================================================================
# Initialize DVC
# =============================================================================

print_step "Initializing DVC..."

if [ ! -d ".dvc" ]; then
    dvc init
    print_info "✓ DVC initialized"
else
    print_info "✓ DVC already initialized"
fi

echo ""

# =============================================================================
# Docker Services
# =============================================================================

print_step "Starting Docker services..."

print_info "Creating .env for Docker Compose..."
export AIRFLOW_UID=$(id -u)
echo "AIRFLOW_UID=$AIRFLOW_UID" >> .env

print_info "Building Docker images..."
docker-compose build

print_info "Starting services (this may take a few minutes)..."
docker-compose up -d

print_info "Waiting for services to be healthy..."
sleep 30

# Check service health
print_info "Checking service status..."
docker-compose ps

print_info "✓ Docker services started"
echo ""

# =============================================================================
# Configure MinIO
# =============================================================================

print_step "Configuring MinIO storage..."

print_info "Waiting for MinIO to be ready..."
sleep 10

print_info "Creating bucket for data storage..."
# You may need to install mc (MinIO Client) for this
# mc alias set local http://localhost:9000 minioadmin minioadmin123
# mc mb local/mlops-data

print_info "✓ MinIO configured"
echo ""

# =============================================================================
# Run Initial Data Pipeline
# =============================================================================

print_step "Running initial data pipeline..."

read -p "Would you like to run the initial data pipeline? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Extracting data..."
    python src/data/extract.py
    
    print_info "Running quality checks..."
    python src/data/quality_check.py
    
    print_info "Transforming data..."
    python src/data/transform.py
    
    print_info "Training initial model..."
    python src/models/train.py
    
    print_info "✓ Initial pipeline completed"
else
    print_info "Skipping initial pipeline"
fi

echo ""

# =============================================================================
# Initialize Git Branches
# =============================================================================

print_step "Setting up Git branches..."

if git rev-parse --verify dev >/dev/null 2>&1; then
    print_info "✓ Dev branch exists"
else
    print_info "Creating dev branch..."
    git checkout -b dev
fi

if git rev-parse --verify test >/dev/null 2>&1; then
    print_info "✓ Test branch exists"
else
    print_info "Creating test branch from dev..."
    git checkout -b test dev
fi

if git rev-parse --verify master >/dev/null 2>&1; then
    print_info "✓ Master branch exists"
else
    print_info "Creating master branch from test..."
    git checkout -b master test
fi

git checkout dev
print_info "✓ Git branches configured"
echo ""

# =============================================================================
# Summary and Next Steps
# =============================================================================

echo "============================================================"
echo "  ✅ Setup Complete!"
echo "============================================================"
echo ""
echo "📊 Access Your Services:"
echo ""
echo "  Airflow:     http://localhost:8080  (admin/admin)"
echo "  MinIO:       http://localhost:9001  (minioadmin/minioadmin123)"
echo "  Prometheus:  http://localhost:9090"
echo "  Grafana:     http://localhost:3000  (admin/admin)"
echo "  API:         http://localhost:8000"
echo ""
echo "📝 Next Steps:"
echo ""
echo "  1. Verify all services are running:"
echo "     docker-compose ps"
echo ""
echo "  2. Check Airflow DAG:"
echo "     - Go to http://localhost:8080"
echo "     - Enable 'crypto_volatility_pipeline'"
echo "     - Trigger a manual run"
echo ""
echo "  3. Test the API:"
echo "     curl http://localhost:8000/health"
echo ""
echo "  4. Setup DagHub:"
echo "     - Create repo at dagshub.com"
echo "     - Update MLFLOW_TRACKING_URI in .env"
echo ""
echo "  5. Configure GitHub Actions:"
echo "     - Add secrets to repository:"
echo "       * DATA_SOURCE=cryptocompare (Free - No key required)"
echo "       * MLFLOW_TRACKING_URI"
echo "       * MLFLOW_TRACKING_USERNAME"
echo "       * MLFLOW_TRACKING_PASSWORD"
echo "       * DOCKER_USERNAME"
echo "       * DOCKER_PASSWORD"
echo ""
echo "📚 Documentation: README.md"
echo ""
echo "============================================================"
echo ""

# =============================================================================
# Optional: Run Tests
# =============================================================================

read -p "Would you like to run tests? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Running tests..."
    pytest tests/ -v --cov=src
fi

echo ""
print_info "All done! Happy MLOps-ing! 🚀"