"""
Airflow DAG for Crypto Volatility Prediction Pipeline
Orchestrates: Extract → Quality Check → Transform → Train
"""

from datetime import datetime, timedelta
from pathlib import Path
import os

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

# Default arguments
default_args = {
    'owner': 'mlops-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'crypto_volatility_pipeline',
    default_args=default_args,
    description='End-to-end MLOps pipeline for crypto volatility prediction',
    schedule_interval='0 */6 * * *',  # Run every 6 hours
    catchup=False,
    tags=['mlops', 'crypto', 'volatility', 'production'],
)

# ============================================================================
# Task Functions
# ============================================================================

def extract_data(**context):
    """Task 1: Extract data from CoinCap API"""
    import sys
    sys.path.insert(0, '/opt/airflow/src')
    
    from data.extract import CoinCapExtractor
    
    extractor = CoinCapExtractor()
    
    # Validate connection
    if not extractor.validate_api_connection():
        raise ConnectionError("Failed to connect to CoinCap API")
    
    # Extract and save data
    output_path = extractor.extract_and_save()
    
    # Push to XCom for next task
    context['ti'].xcom_push(key='raw_data_path', value=output_path)
    
    return output_path


def quality_check(**context):
    """Task 2: Perform data quality checks"""
    import sys
    sys.path.insert(0, '/opt/airflow/src')
    
    import pandas as pd
    from data.quality_check import DataQualityChecker
    from pathlib import Path
    
    # Get raw data path from previous task
    raw_data_path = context['ti'].xcom_pull(key='raw_data_path', task_ids='extract_data')
    
    if not raw_data_path:
        raise ValueError("No raw data path found from extraction task")
    
    # Load data
    df = pd.read_csv(raw_data_path)
    
    # Run quality checks
    checker = DataQualityChecker(null_threshold=0.01, schema_strict=False)
    passed, report = checker.run_all_checks(df)
    
    # Save report
    report_dir = Path('/opt/airflow/reports/quality')
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    checker.save_report(report, report_path)
    
    # MANDATORY GATE: Fail if quality checks don't pass
    if not passed:
        raise ValueError(
            f"Data quality checks FAILED! "
            f"Passed: {report['passed_checks']}/{report['total_checks']}. "
            f"Pipeline stopped."
        )
    
    # Push path to XCom
    context['ti'].xcom_push(key='validated_data_path', value=raw_data_path)
    context['ti'].xcom_push(key='quality_report_path', value=str(report_path))
    
    return passed


def transform_data(**context):
    """Task 3: Transform data and engineer features"""
    import sys
    sys.path.insert(0, '/opt/airflow/src')
    
    import pandas as pd
    from data.transform import CryptoFeatureEngineer
    from pathlib import Path
    
    # Get validated data path
    raw_data_path = context['ti'].xcom_pull(key='validated_data_path', task_ids='quality_check')
    
    if not raw_data_path:
        raise ValueError("No validated data path found")
    
    # Set output path
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'/opt/airflow/data/processed/crypto_processed_{timestamp}.csv'
    
    # Transform data
    engineer = CryptoFeatureEngineer(prediction_horizon=1)
    processed_path = engineer.transform(raw_data_path, output_file)
    
    # Generate profiling report
    df_processed = pd.read_csv(processed_path)
    report_path = engineer.generate_profiling_report(
        df_processed,
        '/opt/airflow/reports/profiling'
    )
    
    # Push paths to XCom
    context['ti'].xcom_push(key='processed_data_path', value=processed_path)
    context['ti'].xcom_push(key='profiling_report_path', value=report_path)
    
    return processed_path


def train_model(**context):
    """Task 4: Train model with MLflow tracking"""
    import sys
    sys.path.insert(0, '/opt/airflow/src')
    
    from models.train import CryptoVolatilityTrainer
    
    # Get processed data path
    processed_path = context['ti'].xcom_pull(key='processed_data_path', task_ids='transform_data')
    
    if not processed_path:
        raise ValueError("No processed data path found")
    
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
        processed_path,
        params=params,
        run_name=f"airflow_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    # Push results to XCom
    context['ti'].xcom_push(key='run_id', value=results['run_id'])
    context['ti'].xcom_push(key='test_rmse', value=results['metrics']['test_rmse'])
    context['ti'].xcom_push(key='test_r2', value=results['metrics']['test_r2'])
    
    return results['run_id']


def version_with_dvc(**context):
    """Task 5: Version processed data with DVC"""
    processed_path = context['ti'].xcom_pull(key='processed_data_path', task_ids='transform_data')
    
    if not processed_path:
        raise ValueError("No processed data path found")
    
    # This would run DVC commands to version the data
    # For now, just log
    print(f"Would version data file: {processed_path} with DVC")
    
    return True


def log_pipeline_metrics(**context):
    """Task 6: Log final pipeline metrics to MLflow"""
    
    # Gather all metrics from previous tasks
    run_id = context['ti'].xcom_pull(key='run_id', task_ids='train_model')
    test_rmse = context['ti'].xcom_pull(key='test_rmse', task_ids='train_model')
    test_r2 = context['ti'].xcom_pull(key='test_r2', task_ids='train_model')
    quality_report_path = context['ti'].xcom_pull(key='quality_report_path', task_ids='quality_check')
    
    print("=" * 60)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 60)
    print(f"MLflow Run ID: {run_id}")
    print(f"Test RMSE: {test_rmse:.6f}")
    print(f"Test R²: {test_r2:.6f}")
    print(f"Quality Report: {quality_report_path}")
    print("=" * 60)
    
    # Could log additional pipeline-level metrics to MLflow here
    
    return True


# ============================================================================
# Define Tasks
# ============================================================================

# Task 1: Extract data from API
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
    provide_context=True,
)

# Task 2: Quality check (MANDATORY GATE)
quality_check_task = PythonOperator(
    task_id='quality_check',
    python_callable=quality_check,
    dag=dag,
    provide_context=True,
)

# Task 3: Transform and feature engineering
transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
    provide_context=True,
)

# Task 4: Train model
train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
    provide_context=True,
)

# Task 5: Version data with DVC
dvc_task = PythonOperator(
    task_id='version_with_dvc',
    python_callable=version_with_dvc,
    dag=dag,
    provide_context=True,
)

# Task 6: Log pipeline metrics
metrics_task = PythonOperator(
    task_id='log_pipeline_metrics',
    python_callable=log_pipeline_metrics,
    dag=dag,
    provide_context=True,
)

# ============================================================================
# Define Task Dependencies (DAG Structure)
# ============================================================================

# Linear pipeline with quality gate
extract_task >> quality_check_task >> transform_task >> train_task >> dvc_task >> metrics_task

# Alternative: Parallel processing of DVC and metrics after training
# extract_task >> quality_check_task >> transform_task >> train_task >> [dvc_task, metrics_task]