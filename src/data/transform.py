"""
Data Transformation and Feature Engineering Module
Creates features for cryptocurrency volatility prediction
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List
import logging
from datetime import datetime
from ydata_profiling import ProfileReport
import warnings

warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CryptoFeatureEngineer:
    """Transform raw crypto data into ML-ready features"""
    
    def __init__(self, prediction_horizon: int = 1):
        """
        Initialize feature engineer
        
        Args:
            prediction_horizon: Hours ahead to predict (default: 1)
        """
        self.prediction_horizon = prediction_horizon
        self.feature_names = []
        
    def load_raw_data(self, file_path: str) -> pd.DataFrame:
        """Load and prepare raw data"""
        df = pd.read_csv(file_path)
        
        # Ensure datetime
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        # Ensure numeric
        df['priceUsd'] = pd.to_numeric(df['priceUsd'], errors='coerce')
        
        logger.info(f"Loaded {len(df)} raw records")
        return df
    
    def create_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create price-based features"""
        logger.info("Creating price features...")
        
        # Price returns (percentage changes)
        df['price_return_5m'] = df['priceUsd'].pct_change(1)
        df['price_return_15m'] = df['priceUsd'].pct_change(3)
        df['price_return_30m'] = df['priceUsd'].pct_change(6)
        df['price_return_1h'] = df['priceUsd'].pct_change(12)
        df['price_return_4h'] = df['priceUsd'].pct_change(48)
        df['price_return_24h'] = df['priceUsd'].pct_change(288)
        
        # Moving averages
        df['ma_5'] = df['priceUsd'].rolling(window=5, min_periods=1).mean()
        df['ma_12'] = df['priceUsd'].rolling(window=12, min_periods=1).mean()
        df['ma_48'] = df['priceUsd'].rolling(window=48, min_periods=1).mean()
        df['ma_144'] = df['priceUsd'].rolling(window=144, min_periods=1).mean()
        
        # Price relative to moving averages
        df['price_to_ma5'] = df['priceUsd'] / df['ma_5']
        df['price_to_ma12'] = df['priceUsd'] / df['ma_12']
        df['price_to_ma48'] = df['priceUsd'] / df['ma_48']
        
        # Exponential moving averages
        df['ema_12'] = df['priceUsd'].ewm(span=12, adjust=False).mean()
        df['ema_48'] = df['priceUsd'].ewm(span=48, adjust=False).mean()
        
        # MACD-like features
        df['macd'] = df['ema_12'] - df['ema_48']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        return df
    
    def create_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create volatility-based features"""
        logger.info("Creating volatility features...")
        
        # Rolling standard deviation (volatility)
        df['volatility_5m'] = df['priceUsd'].rolling(window=5, min_periods=2).std()
        df['volatility_30m'] = df['priceUsd'].rolling(window=30, min_periods=5).std()
        df['volatility_1h'] = df['priceUsd'].rolling(window=12, min_periods=5).std()
        df['volatility_4h'] = df['priceUsd'].rolling(window=48, min_periods=10).std()
        
        # Normalized volatility (coefficient of variation)
        df['cv_1h'] = df['volatility_1h'] / df['ma_12']
        df['cv_4h'] = df['volatility_4h'] / df['ma_48']
        
        # High-Low range
        df['high_5m'] = df['priceUsd'].rolling(window=5).max()
        df['low_5m'] = df['priceUsd'].rolling(window=5).min()
        df['hl_range_5m'] = (df['high_5m'] - df['low_5m']) / df['low_5m']
        
        df['high_1h'] = df['priceUsd'].rolling(window=12).max()
        df['low_1h'] = df['priceUsd'].rolling(window=12).min()
        df['hl_range_1h'] = (df['high_1h'] - df['low_1h']) / df['low_1h']
        
        return df
    
    def create_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create momentum indicators"""
        logger.info("Creating momentum features...")
        
        # Rate of change
        df['roc_12'] = ((df['priceUsd'] - df['priceUsd'].shift(12)) / 
                        df['priceUsd'].shift(12))
        df['roc_48'] = ((df['priceUsd'] - df['priceUsd'].shift(48)) / 
                        df['priceUsd'].shift(48))
        
        # RSI-like momentum
        delta = df['priceUsd'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Price acceleration (second derivative)
        df['price_accel'] = df['price_return_5m'].diff()
        
        return df
    
    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features"""
        logger.info("Creating temporal features...")
        
        # Extract time components
        df['hour'] = df['date'].dt.hour
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Cyclical encoding for hour (24-hour cycle)
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        # Cyclical encoding for day of week (7-day cycle)
        df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # Time since start (in hours)
        df['hours_elapsed'] = (df['date'] - df['date'].min()).dt.total_seconds() / 3600
        
        return df
    
    def create_lag_features(self, df: pd.DataFrame, lags: List[int] = [1, 2, 3, 6, 12]) -> pd.DataFrame:
        """Create lagged price features"""
        logger.info("Creating lag features...")
        
        for lag in lags:
            df[f'price_lag_{lag}'] = df['priceUsd'].shift(lag)
            df[f'volatility_lag_{lag}'] = df['volatility_1h'].shift(lag)
        
        return df
    
    def create_target_variable(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create target variable: future volatility"""
        logger.info(f"Creating target variable (volatility {self.prediction_horizon}h ahead)...")
        
        # Calculate future volatility
        # For 1-hour prediction with 5-min intervals, shift 12 periods
        shift_periods = self.prediction_horizon * 12
        
        df['target_volatility'] = df['volatility_1h'].shift(-shift_periods)
        
        # Also create normalized target
        df['target_volatility_norm'] = df['target_volatility'] / df['priceUsd']
        
        return df
    
    def clean_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and finalize features"""
        logger.info("Cleaning features...")
        
        # Replace inf with nan
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Drop rows with missing target
        df = df.dropna(subset=['target_volatility'])
        
        # Forward fill remaining NaN values (for initial periods)
        df = df.fillna(method='ffill')
        
        # Drop remaining NaN rows
        df = df.dropna()
        
        logger.info(f"Final dataset size: {len(df)} records")
        return df
    
    def select_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Select final feature set"""
        
        # Define feature columns
        feature_cols = [
            # Price features
            'price_return_5m', 'price_return_15m', 'price_return_30m',
            'price_return_1h', 'price_return_4h', 'price_return_24h',
            'price_to_ma5', 'price_to_ma12', 'price_to_ma48',
            'macd', 'macd_signal',
            
            # Volatility features
            'volatility_5m', 'volatility_30m', 'volatility_1h', 'volatility_4h',
            'cv_1h', 'cv_4h',
            'hl_range_5m', 'hl_range_1h',
            
            # Momentum features
            'roc_12', 'roc_48', 'rsi', 'price_accel',
            
            # Temporal features
            'hour_sin', 'hour_cos', 'dow_sin', 'dow_cos',
            'is_weekend', 'hours_elapsed',
            
            # Lag features
            'price_lag_1', 'price_lag_2', 'price_lag_3', 'price_lag_6', 'price_lag_12',
            'volatility_lag_1', 'volatility_lag_2', 'volatility_lag_3'
        ]
        
        # Verify all features exist
        available_features = [col for col in feature_cols if col in df.columns]
        missing_features = set(feature_cols) - set(available_features)
        
        if missing_features:
            logger.warning(f"Missing features: {missing_features}")
        
        logger.info(f"Selected {len(available_features)} features")
        self.feature_names = available_features
        
        return df, available_features
    
    def transform(self, input_file: str, output_file: str) -> str:
        """
        Main transformation pipeline
        
        Args:
            input_file: Path to raw CSV file
            output_file: Path to save processed CSV
            
        Returns:
            Path to processed file
        """
        logger.info("=" * 60)
        logger.info("STARTING DATA TRANSFORMATION")
        logger.info("=" * 60)
        
        # Load data
        df = self.load_raw_data(input_file)
        
        # Apply feature engineering
        df = self.create_price_features(df)
        df = self.create_volatility_features(df)
        df = self.create_momentum_features(df)
        df = self.create_temporal_features(df)
        df = self.create_lag_features(df)
        df = self.create_target_variable(df)
        df = self.clean_features(df)
        
        # Select final features
        df, feature_names = self.select_features(df)
        
        # Prepare final dataset
        final_cols = feature_names + ['target_volatility', 'target_volatility_norm', 'date']
        df_final = df[final_cols].copy()
        
        # Save processed data
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_final.to_csv(output_path, index=False)
        
        logger.info(f"Processed data saved to: {output_path}")
        logger.info(f"Shape: {df_final.shape}")
        logger.info(f"Features: {len(feature_names)}")
        
        logger.info("=" * 60)
        logger.info("✓ TRANSFORMATION COMPLETED")
        logger.info("=" * 60)
        
        return str(output_path)
    
    def generate_profiling_report(self, df: pd.DataFrame, output_dir: str):
        """Generate pandas profiling report"""
        logger.info("Generating data profiling report...")
        
        try:
            profile = ProfileReport(
                df,
                title="Crypto Volatility Dataset Profile",
                explorative=True,
                minimal=False
            )
            
            report_path = Path(output_dir) / f"data_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            profile.to_file(report_path)
            logger.info(f"✓ Profiling report saved to: {report_path}")
            
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Failed to generate profiling report: {e}")
            return None


def main():
    """Main execution function"""
    from pathlib import Path
    
    # Find latest raw data file
    raw_data_dir = Path('data/raw')
    csv_files = sorted(raw_data_dir.glob('crypto_raw_*.csv'))
    
    if not csv_files:
        logger.error("No raw data files found!")
        return None
    
    latest_file = csv_files[-1]
    logger.info(f"Processing file: {latest_file}")
    
    # Set output path
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'data/processed/crypto_processed_{timestamp}.csv'
    
    # Transform data
    engineer = CryptoFeatureEngineer(prediction_horizon=1)
    processed_path = engineer.transform(str(latest_file), output_file)
    
    # Generate profiling report
    df_processed = pd.read_csv(processed_path)
    engineer.generate_profiling_report(df_processed, 'reports/profiling')
    
    print(f"\n✓ Transformation completed successfully!")
    print(f"✓ Processed file: {processed_path}")
    print(f"✓ Dataset shape: {df_processed.shape}")
    
    return processed_path


if __name__ == "__main__":
    main()