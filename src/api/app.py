"""
FastAPI Application for Model Serving
Includes Prometheus monitoring and drift detection
"""

import os
import json
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import mlflow.pyfunc
import joblib
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi.responses import Response
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Prometheus Metrics
# ============================================================================

# Request metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Latency metrics
prediction_latency = Histogram(
    'prediction_latency_seconds',
    'Time spent processing prediction',
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

# Model metrics
prediction_value = Gauge(
    'model_prediction_value',
    'Latest prediction value'
)

# Data drift metrics
data_drift_ratio = Gauge(
    'data_drift_ratio',
    'Ratio of out-of-distribution features'
)

feature_ood_count = Counter(
    'feature_ood_total',
    'Count of out-of-distribution feature values',
    ['feature_name']
)

# ============================================================================
# Request/Response Models
# ============================================================================

class PredictionInput(BaseModel):
    """Input schema for prediction"""
    features: List[float] = Field(..., description="List of feature values")
    
    class Config:
        json_schema_extra = {
            "example": {
                "features": [0.05, -0.02, 0.03, 0.01, -0.01, 0.04,
                           1.002, 0.998, 1.001, 0.0001, -0.0002,
                           0.0003, 0.0004, 0.0005, 0.015,
                           0.012, 0.001, 0.003, 0.002, 0.003,
                           0.001, 45.5, 0.707, 0.707, -0.434, 0.901,
                           0, 120.5, 50000, 49800, 49950, 49700, 50100,
                           0.0003, 0.0004, 0.0002]
            }
        }

class PredictionOutput(BaseModel):
    """Output schema for prediction"""
    prediction: float = Field(..., description="Predicted volatility (normalized)")
    prediction_volatility: float = Field(..., description="Predicted actual volatility")
    confidence: float = Field(..., description="Model confidence score (0-1)")
    drift_detected: bool = Field(..., description="Whether data drift was detected")
    drift_ratio: float = Field(..., description="Ratio of OOD features")
    timestamp: str = Field(..., description="Prediction timestamp")
    model_version: str = Field(..., description="Model version used")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    timestamp: str
    model_version: Optional[str] = None

# ============================================================================
# Model Manager
# ============================================================================

class ModelManager:
    """Manages model loading and inference"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.feature_stats = None
        self.model_version = None
        self.drift_threshold = float(os.getenv('DRIFT_THRESHOLD', 0.15))
        
    def load_model(self):
        """Load model, scaler, and metadata"""
        try:
            # Load from MLflow
            model_name = os.getenv('MODEL_NAME', 'crypto-volatility-predictor')
            model_stage = os.getenv('MODEL_STAGE', 'Production')
            
            try:
                # Try loading from MLflow registry
                model_uri = f"models:/{model_name}/{model_stage}"
                self.model = mlflow.pyfunc.load_model(model_uri)
                self.model_version = f"{model_name}:{model_stage}"
                logger.info(f"Loaded model from MLflow: {model_uri}")
            except Exception as e:
                logger.warning(f"Could not load from registry: {e}")
                # Fallback to local model
                model_path = "models"
                if Path(f"{model_path}/model.json").exists():
                    import xgboost as xgb
                    self.model = xgb.XGBRegressor()
                    self.model.load_model(f"{model_path}/model.json")
                    self.model_version = "local"
                    logger.info("Loaded local model")
                else:
                    raise FileNotFoundError("No model found")
            
            # Load scaler
            scaler_path = "models/scaler.joblib"
            if Path(scaler_path).exists():
                self.scaler = joblib.load(scaler_path)
                logger.info("Loaded scaler")
            
            # Load feature names
            feature_path = "models/feature_names.json"
            if Path(feature_path).exists():
                with open(feature_path, 'r') as f:
                    data = json.load(f)
                    self.feature_names = data.get('features', [])
                logger.info(f"Loaded {len(self.feature_names)} feature names")
            
            # Compute feature statistics for drift detection
            self._compute_feature_stats()
            
            logger.info("✓ Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def _compute_feature_stats(self):
        """Compute feature statistics from training data for drift detection"""
        # In production, load these from saved training stats
        # For now, use reasonable defaults based on typical crypto features
        if self.feature_names:
            self.feature_stats = {
                'mean': np.zeros(len(self.feature_names)),
                'std': np.ones(len(self.feature_names)),
                'min': np.ones(len(self.feature_names)) * -10,
                'max': np.ones(len(self.feature_names)) * 10
            }
    
    def detect_drift(self, features: np.ndarray) -> Dict:
        """
        Detect data drift using simple statistical checks
        
        Returns:
            Dict with drift information
        """
        if self.feature_stats is None:
            return {'drift_detected': False, 'drift_ratio': 0.0, 'ood_features': []}
        
        ood_features = []
        features_flat = features.flatten()
        
        # Check each feature for out-of-distribution
        for i, (val, name) in enumerate(zip(features_flat, self.feature_names)):
            # Check if value is extreme (>3 std from mean, or outside min/max)
            mean_val = self.feature_stats['mean'][i] if i < len(self.feature_stats['mean']) else 0
            std_val = self.feature_stats['std'][i] if i < len(self.feature_stats['std']) else 1
            
            z_score = abs((val - mean_val) / (std_val + 1e-10))
            
            if z_score > 3 or np.isnan(val) or np.isinf(val):
                ood_features.append(name)
                feature_ood_count.labels(feature_name=name).inc()
        
        drift_ratio = len(ood_features) / len(features_flat)
        drift_detected = drift_ratio > self.drift_threshold
        
        # Update Prometheus metric
        data_drift_ratio.set(drift_ratio)
        
        return {
            'drift_detected': drift_detected,
            'drift_ratio': drift_ratio,
            'ood_features': ood_features
        }
    
    def predict(self, features: List[float]) -> Dict:
        """
        Make prediction
        
        Args:
            features: List of feature values
            
        Returns:
            Prediction dictionary
        """
        start_time = time.time()
        
        try:
            # Convert to numpy array
            X = np.array(features).reshape(1, -1)
            
            # Validate feature count
            if self.feature_names and len(features) != len(self.feature_names):
                raise ValueError(
                    f"Expected {len(self.feature_names)} features, got {len(features)}"
                )
            
            # Detect drift
            drift_info = self.detect_drift(X)
            
            # Scale features if scaler is available
            if self.scaler:
                X_scaled = self.scaler.transform(X)
            else:
                X_scaled = X
            
            # Make prediction
            if hasattr(self.model, 'predict'):
                prediction = self.model.predict(X_scaled)[0]
            else:
                # MLflow PyFunc model
                prediction = self.model.predict(X_scaled)[0]
            
            # Update metrics
            prediction_value.set(float(prediction))
            
            # Compute confidence (simple heuristic: inverse of drift ratio)
            confidence = max(0.0, min(1.0, 1.0 - drift_info['drift_ratio']))
            
            # Estimate actual volatility (denormalize)
            # Assuming current price is around $50,000 for BTC
            estimated_price = 50000.0  # Should be passed or retrieved
            prediction_volatility = prediction * estimated_price
            
            result = {
                'prediction': float(prediction),
                'prediction_volatility': float(prediction_volatility),
                'confidence': confidence,
                'drift_detected': drift_info['drift_detected'],
                'drift_ratio': drift_info['drift_ratio'],
                'timestamp': datetime.now().isoformat(),
                'model_version': self.model_version or 'unknown'
            }
            
            # Record latency
            latency = time.time() - start_time
            prediction_latency.observe(latency)
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise

# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Crypto Volatility Prediction API",
    description="Real-time cryptocurrency volatility prediction with MLOps",
    version="1.0.0"
)

# Initialize model manager
model_manager = ModelManager()

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    logger.info("Starting up application...")
    success = model_manager.load_model()
    if not success:
        logger.error("Failed to load model on startup!")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests"""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    # Update metrics
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.3f}s"
    )
    
    return response

@app.get("/", response_model=Dict)
async def root():
    """Root endpoint"""
    return {
        "service": "Crypto Volatility Prediction API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "metrics": "/metrics"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if model_manager.model is not None else "unhealthy",
        model_loaded=model_manager.model is not None,
        timestamp=datetime.now().isoformat(),
        model_version=model_manager.model_version
    )

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    """
    Make volatility prediction
    
    Args:
        input_data: Prediction input containing features
        
    Returns:
        Prediction output with volatility forecast
    """
    if model_manager.model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Service unavailable."
        )
    
    try:
        result = model_manager.predict(input_data.features)
        return PredictionOutput(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

@app.get("/model/info")
async def model_info():
    """Get model information"""
    if model_manager.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_version": model_manager.model_version,
        "feature_count": len(model_manager.feature_names) if model_manager.feature_names else 0,
        "feature_names": model_manager.feature_names,
        "drift_threshold": model_manager.drift_threshold
    }

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=False,
        workers=1
    )