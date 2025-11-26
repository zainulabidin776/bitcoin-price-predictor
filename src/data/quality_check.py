"""
Data Quality Check Module
Implements strict quality gates for data validation
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataQualityChecker:
    """Performs comprehensive data quality checks"""
    
    def __init__(self, null_threshold: float = 0.01, schema_strict: bool = True):
        """
        Initialize quality checker
        
        Args:
            null_threshold: Maximum allowed null percentage (default 1%)
            schema_strict: Whether to enforce strict schema validation
        """
        self.null_threshold = null_threshold
        self.schema_strict = schema_strict
        self.quality_report = {}
        
        # Expected schema for raw crypto data (CryptoCompare format)
        self.expected_schema = {
            'timestamp': 'object',  # datetime string
            'open': 'float64',
            'high': 'float64',
            'low': 'float64',
            'close': 'float64',
            'volume': 'float64',
            'volume_usd': 'float64'
        }
        
        self.required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    
    def check_null_values(self, df: pd.DataFrame) -> Tuple[bool, Dict]:
        """
        Check for null values exceeding threshold
        
        Returns:
            (passed, report_dict)
        """
        null_counts = df.isnull().sum()
        null_percentages = (null_counts / len(df)) * 100
        
        # Check each column
        failed_columns = []
        for col in df.columns:
            if null_percentages[col] > (self.null_threshold * 100):
                failed_columns.append({
                    'column': col,
                    'null_percentage': null_percentages[col],
                    'null_count': null_counts[col]
                })
        
        passed = len(failed_columns) == 0
        
        report = {
            'check': 'null_values',
            'passed': passed,
            'threshold': self.null_threshold * 100,
            'failed_columns': failed_columns,
            'total_nulls': null_counts.sum()
        }
        
        if passed:
            logger.info("✓ Null value check PASSED")
        else:
            logger.error(f"✗ Null value check FAILED: {len(failed_columns)} columns exceed threshold")
        
        return passed, report
    
    def check_schema(self, df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Validate schema matches expected structure"""
        
        # Check required columns exist
        missing_columns = set(self.required_columns) - set(df.columns)
        extra_columns = set(df.columns) - set(self.expected_schema.keys())
        
        # Check data types
        dtype_mismatches = []
        for col, expected_dtype in self.expected_schema.items():
            if col in df.columns:
                actual_dtype = str(df[col].dtype)
                if actual_dtype != expected_dtype:
                    dtype_mismatches.append({
                        'column': col,
                        'expected': expected_dtype,
                        'actual': actual_dtype
                    })
        
        passed = (len(missing_columns) == 0 and 
                 len(dtype_mismatches) == 0 and
                 (not self.schema_strict or len(extra_columns) == 0))
        
        report = {
            'check': 'schema_validation',
            'passed': passed,
            'missing_columns': list(missing_columns),
            'extra_columns': list(extra_columns),
            'dtype_mismatches': dtype_mismatches
        }
        
        if passed:
            logger.info("✓ Schema validation PASSED")
        else:
            logger.error(f"✗ Schema validation FAILED")
        
        return passed, report
    
    def check_data_ranges(self, df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Check if data values are within reasonable ranges"""
        
        range_violations = []
        
        # Check close price is positive
        if 'close' in df.columns:
            negative_prices = df[df['close'] <= 0]
            if len(negative_prices) > 0:
                range_violations.append({
                    'column': 'close',
                    'issue': 'negative_or_zero_values',
                    'count': len(negative_prices)
                })
            
            # Check for unrealistic price values (too high or too low)
            median_price = df['close'].median()
            outlier_threshold = 5.0  # 5x deviation
            
            outliers = df[
                (df['close'] > median_price * outlier_threshold) |
                (df['close'] < median_price / outlier_threshold)
            ]
            
            if len(outliers) > len(df) * 0.05:  # More than 5% outliers
                range_violations.append({
                    'column': 'close',
                    'issue': 'excessive_outliers',
                    'count': len(outliers),
                    'percentage': (len(outliers) / len(df)) * 100
                })
        
        # Check timestamps are valid
        if 'timestamp' in df.columns:
            try:
                pd.to_datetime(df['timestamp'])
            except Exception as e:
                range_violations.append({
                    'column': 'timestamp',
                    'issue': 'invalid_timestamp_format',
                    'count': 1,
                    'error': str(e)
                })
        
        passed = len(range_violations) == 0
        
        report = {
            'check': 'data_ranges',
            'passed': passed,
            'violations': range_violations
        }
        
        if passed:
            logger.info("✓ Data range check PASSED")
        else:
            logger.error(f"✗ Data range check FAILED: {len(range_violations)} violations")
        
        return passed, report
    
    def check_data_freshness(self, df: pd.DataFrame, max_age_hours: int = 48) -> Tuple[bool, Dict]:
        """Check if data is recent enough"""
        
        if 'timestamp' not in df.columns:
            return True, {'check': 'data_freshness', 'passed': True, 'note': 'No timestamp column'}
        
        latest_date = pd.to_datetime(df['timestamp']).max()
        current_time = datetime.now()
        
        age_hours = (current_time - latest_date).total_seconds() / 3600
        
        # More lenient for historical data - allow up to 48 hours
        passed = age_hours <= max_age_hours
        
        report = {
            'check': 'data_freshness',
            'passed': passed,
            'latest_data_time': str(latest_date),
            'current_time': str(current_time),
            'age_hours': age_hours,
            'threshold_hours': max_age_hours
        }
        
        if passed:
            logger.info(f"✓ Data freshness check PASSED (age: {age_hours:.2f}h)")
        else:
            logger.warning(f"✗ Data freshness check FAILED (age: {age_hours:.2f}h > {max_age_hours}h)")
        
        return passed, report
    
    def check_duplicates(self, df: pd.DataFrame) -> Tuple[bool, Dict]:
        """Check for duplicate records"""
        
        duplicate_count = df.duplicated().sum()
        duplicate_percentage = (duplicate_count / len(df)) * 100
        
        # Allow up to 0.5% duplicates
        passed = duplicate_percentage <= 0.5
        
        report = {
            'check': 'duplicates',
            'passed': passed,
            'duplicate_count': int(duplicate_count),
            'duplicate_percentage': duplicate_percentage,
            'threshold_percentage': 0.5
        }
        
        if passed:
            logger.info("✓ Duplicate check PASSED")
        else:
            logger.error(f"✗ Duplicate check FAILED: {duplicate_percentage:.2f}% duplicates")
        
        return passed, report
    
    def check_data_volume(self, df: pd.DataFrame, min_rows: int = 100) -> Tuple[bool, Dict]:
        """Check if sufficient data volume exists"""
        
        row_count = len(df)
        passed = row_count >= min_rows
        
        report = {
            'check': 'data_volume',
            'passed': passed,
            'row_count': row_count,
            'min_required': min_rows
        }
        
        if passed:
            logger.info(f"✓ Data volume check PASSED ({row_count} rows)")
        else:
            logger.error(f"✗ Data volume check FAILED ({row_count} < {min_rows} rows)")
        
        return passed, report
    
    def run_all_checks(self, df: pd.DataFrame) -> Tuple[bool, Dict]:
        """
        Run all quality checks
        
        Returns:
            (all_passed, complete_report)
        """
        logger.info("=" * 60)
        logger.info("STARTING DATA QUALITY CHECKS")
        logger.info("=" * 60)
        
        checks = [
            self.check_data_volume(df),
            self.check_null_values(df),
            self.check_schema(df),
            self.check_data_ranges(df),
            self.check_duplicates(df),
            self.check_data_freshness(df)
        ]
        
        all_passed = all(passed for passed, _ in checks)
        
        complete_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'PASSED' if all_passed else 'FAILED',
            'total_checks': len(checks),
            'passed_checks': sum(1 for passed, _ in checks if passed),
            'failed_checks': sum(1 for passed, _ in checks if not passed),
            'checks': [report for _, report in checks],
            'dataset_info': {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns)
            }
        }
        
        logger.info("=" * 60)
        if all_passed:
            logger.info("✓ ALL QUALITY CHECKS PASSED")
        else:
            logger.error("✗ QUALITY CHECKS FAILED")
        logger.info(f"Passed: {complete_report['passed_checks']}/{complete_report['total_checks']}")
        logger.info("=" * 60)
        
        return all_passed, complete_report
    
    def save_report(self, report: Dict, output_path: Path):
        """Save quality report to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Quality report saved to {output_path}")


def main():
    """Main execution for testing"""
    from pathlib import Path
    
    # Find most recent raw data file
    raw_data_dir = Path('data/raw')
    csv_files = sorted(raw_data_dir.glob('crypto_raw_*.csv'))
    
    if not csv_files:
        logger.error("No raw data files found")
        return False
    
    latest_file = csv_files[-1]
    logger.info(f"Checking quality of: {latest_file}")
    
    # Load data
    df = pd.read_csv(latest_file)
    
    # Run quality checks
    checker = DataQualityChecker(null_threshold=0.01, schema_strict=False)
    passed, report = checker.run_all_checks(df)
    
    # Save report
    report_dir = Path('reports/quality')
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    checker.save_report(report, report_path)
    
    if not passed:
        raise ValueError("Data quality checks failed! Pipeline stopped.")
    
    return passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)