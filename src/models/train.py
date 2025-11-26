"""
Model Training Module with MLflow Integration
Trains XGBoost model for cryptocurrency volatility prediction
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Any
import logging
from datetime import datetime
import json

import mlflow
import mlflow.sklearn
import mlflow.xgboost
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CryptoVolatilityTrainer:
    """Train and evaluate volatility prediction model"""
    
    def __init__(self, experiment_name: str = "crypto-volatility-prediction"):
        """
        Initialize trainer
        
        Args:
            experiment_name: MLflow experiment name
        """
        self.experiment_name = experiment_name
        self.model = None
        self.scaler = None
        self.feature_names = None
        
        # Setup MLflow
        self.setup_mlflow()
        
    def setup_mlflow(self):
        """Configure MLflow tracking"""
        tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
        
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
            logger.info(f"MLflow tracking URI: {tracking_uri}")
        else:
            logger.warning("MLflow tracking URI not set, using local tracking")
        
        # Set or create experiment
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(self.experiment_name)
                logger.info(f"Created new experiment: {self.experiment_name}")
            else:
                experiment_id = experiment.experiment_id
                logger.info(f"Using existing experiment: {self.experiment_name}")
            
            mlflow.set_experiment(self.experiment_name)
            
        except Exception as e:
            logger.error(f"MLflow setup error: {e}")
            logger.info("Continuing with local MLflow tracking")
    
    def load_processed_data(self, file_path: str) -> pd.DataFrame:
        """Load processed dataset"""
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} processed records")
        logger.info(f"Columns: {df.columns.tolist()}")
        return df
    
    def prepare_train_test_split(
        self, 
        df: pd.DataFrame, 
        test_size: float = 0.2,
        val_size: float = 0.2
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Split data into train/validation/test sets
        Uses time-series aware splitting
        """
        # Separate features and target
        feature_cols = [col for col in df.columns 
                       if col not in ['target_volatility', 'target_volatility_norm', 'date']]
        
        self.feature_names = feature_cols
        
        X = df[feature_cols].values
        y = df['target_volatility_norm'].values  # Use normalized target
        
        # Time-series split: train -> validation -> test
        n = len(X)
        train_end = int(n * (1 - test_size - val_size))
        val_end = int(n * (1 - test_size))
        
        X_train = X[:train_end]
        y_train = y[:train_end]
        
        X_val = X[train_end:val_end]
        y_val = y[train_end:val_end]
        
        X_test = X[val_end:]
        y_test = y[val_end:]
        
        logger.info(f"Train set: {X_train.shape}")
        logger.info(f"Validation set: {X_val.shape}")
        logger.info(f"Test set: {X_test.shape}")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def scale_features(
        self, 
        X_train: np.ndarray, 
        X_val: np.ndarray, 
        X_test: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, StandardScaler]:
        """Scale features using StandardScaler"""
        scaler = StandardScaler()
        
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        X_test_scaled = scaler.transform(X_test)
        
        self.scaler = scaler
        
        logger.info("Features scaled using StandardScaler")
        return X_train_scaled, X_val_scaled, X_test_scaled, scaler
    
    def train_xgboost(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        params: Dict[str, Any] = None
    ) -> xgb.XGBRegressor:
        """
        Train XGBoost model
        
        Args:
            X_train: Training features
            y_train: Training target
            X_val: Validation features
            y_val: Validation target
            params: Model hyperparameters
        """
        if params is None:
            params = {
                'objective': 'reg:squarederror',
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 200,
                'min_child_weight': 3,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'gamma': 0.1,
                'reg_alpha': 0.1,
                'reg_lambda': 1.0,
                'random_state': 42,
                'n_jobs': -1
            }
        
        logger.info("Training XGBoost model...")
        logger.info(f"Parameters: {params}")
        
        model = xgb.XGBRegressor(**params)
        
        # Train with early stopping
        model.fit(
            X_train, 
            y_train,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=20,
            verbose=False
        )
        
        logger.info(f"✓ Model training completed")
        logger.info(f"Best iteration: {model.best_iteration}")
        
        self.model = model
        return model
    
    def evaluate_model(
        self,
        model: xgb.XGBRegressor,
        X: np.ndarray,
        y: np.ndarray,
        dataset_name: str = "test"
    ) -> Dict[str, float]:
        """Evaluate model performance"""
        
        y_pred = model.predict(X)
        
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        mae = mean_absolute_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        # Additional metrics
        mape = np.mean(np.abs((y - y_pred) / (y + 1e-10))) * 100
        
        metrics = {
            f'{dataset_name}_rmse': rmse,
            f'{dataset_name}_mae': mae,
            f'{dataset_name}_r2': r2,
            f'{dataset_name}_mape': mape
        }
        
        logger.info(f"\n{dataset_name.upper()} SET METRICS:")
        logger.info(f"  RMSE: {rmse:.6f}")
        logger.info(f"  MAE: {mae:.6f}")
        logger.info(f"  R²: {r2:.6f}")
        logger.info(f"  MAPE: {mape:.2f}%")
        
        return metrics
    
    def get_feature_importance(self, model: xgb.XGBRegressor) -> pd.DataFrame:
        """Get feature importance DataFrame"""
        importance_dict = {
            'feature': self.feature_names,
            'importance': model.feature_importances_
        }
        
        importance_df = pd.DataFrame(importance_dict)
        importance_df = importance_df.sort_values('importance', ascending=False)
        
        return importance_df
    
    def train_and_log(
        self,
        data_path: str,
        params: Dict[str, Any] = None,
        run_name: str = None
    ) -> Dict[str, Any]:
        """
        Complete training pipeline with MLflow logging
        
        Returns:
            Dictionary with model path and metrics
        """
        logger.info("=" * 60)
        logger.info("STARTING MODEL TRAINING")
        logger.info("=" * 60)
        
        # Start MLflow run
        with mlflow.start_run(run_name=run_name) as run:
            
            # Log parameters
            if params:
                mlflow.log_params(params)
            
            # Load data
            df = self.load_processed_data(data_path)
            
            # Log dataset info
            mlflow.log_param("dataset_size", len(df))
            mlflow.log_param("n_features", len(df.columns) - 3)  # Excluding target and date
            
            # Prepare data splits
            X_train, X_val, X_test, y_train, y_val, y_test = \
                self.prepare_train_test_split(df)
            
            mlflow.log_param("train_size", len(X_train))
            mlflow.log_param("val_size", len(X_val))
            mlflow.log_param("test_size", len(X_test))
            
            # Scale features
            X_train_scaled, X_val_scaled, X_test_scaled, scaler = \
                self.scale_features(X_train, X_val, X_test)
            
            # Train model
            model = self.train_xgboost(
                X_train_scaled, y_train,
                X_val_scaled, y_val,
                params=params
            )
            
            # Evaluate on all sets
            train_metrics = self.evaluate_model(model, X_train_scaled, y_train, "train")
            val_metrics = self.evaluate_model(model, X_val_scaled, y_val, "validation")
            test_metrics = self.evaluate_model(model, X_test_scaled, y_test, "test")
            
            # Combine all metrics
            all_metrics = {**train_metrics, **val_metrics, **test_metrics}
            
            # Log metrics to MLflow
            mlflow.log_metrics(all_metrics)
            
            # Log feature importance
            importance_df = self.get_feature_importance(model)
            importance_path = "outputs/feature_importance.csv"
            os.makedirs("outputs", exist_ok=True)
            importance_df.to_csv(importance_path, index=False)
            mlflow.log_artifact(importance_path)
            
            logger.info("\nTop 10 Important Features:")
            print(importance_df.head(10))
            
            # Save model artifacts
            model_dir = "models"
            os.makedirs(model_dir, exist_ok=True)
            
            # Log model with MLflow
            mlflow.xgboost.log_model(
                model,
                "model",
                registered_model_name=os.getenv('MODEL_NAME', 'crypto-volatility-predictor')
            )
            
            # Also save scaler
            import joblib
            scaler_path = f"{model_dir}/scaler.joblib"
            joblib.dump(scaler, scaler_path)
            mlflow.log_artifact(scaler_path)
            
            # Save feature names
            feature_names_path = f"{model_dir}/feature_names.json"
            with open(feature_names_path, 'w') as f:
                json.dump({'features': self.feature_names}, f)
            mlflow.log_artifact(feature_names_path)
            
            # Log run info
            run_id = run.info.run_id
            
            logger.info("\n" + "=" * 60)
            logger.info("✓ TRAINING COMPLETED SUCCESSFULLY")
            logger.info(f"Run ID: {run_id}")
            logger.info(f"Test RMSE: {test_metrics['test_rmse']:.6f}")
            logger.info(f"Test R²: {test_metrics['test_r2']:.6f}")
            logger.info("=" * 60)
            
            return {
                'run_id': run_id,
                'metrics': all_metrics,
                'model_uri': f"runs:/{run_id}/model"
            }


def main():
    """Main execution function"""
    from pathlib import Path
    
    # Find latest processed data file
    processed_dir = Path('data/processed')
    csv_files = sorted(processed_dir.glob('crypto_processed_*.csv'))
    
    if not csv_files:
        logger.error("No processed data files found!")
        return None
    
    latest_file = csv_files[-1]
    logger.info(f"Training with file: {latest_file}")
    
    # Define hyperparameters
    params = {
        'objective': 'reg:squarederror',
        'max_depth': 7,
        'learning_rate': 0.05,
        'n_estimators': 300,
        'min_child_weight': 3,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'gamma': 0.1,
        'reg_alpha': 0.1,
        'reg_lambda': 1.0,
        'random_state': 42,
        'n_jobs': -1
    }
    
    # Train model
    trainer = CryptoVolatilityTrainer()
    results = trainer.train_and_log(
        str(latest_file),
        params=params,
        run_name=f"xgboost_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    print(f"\n✓ Model training completed!")
    print(f"✓ Run ID: {results['run_id']}")
    print(f"✓ Test RMSE: {results['metrics']['test_rmse']:.6f}")
    print(f"✓ Test R²: {results['metrics']['test_r2']:.6f}")
    
    return results


if __name__ == "__main__":
    main()