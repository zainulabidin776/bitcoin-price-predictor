#!/usr/bin/env python3
"""
MLflow DagHub Configuration Script
Automatically configures MLflow to work with DagHub for experiment tracking.

This script:
1. Checks if DagHub credentials are configured
2. Initializes DagHub connection
3. Tests MLflow connection
4. Creates/verifies experiment exists
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    print("⚠️  Warning: .env file not found. Using system environment variables.")

def check_dagshub_credentials():
    """Check if DagHub credentials are configured"""
    tracking_uri = os.getenv('MLFLOW_TRACKING_URI', '')
    username = os.getenv('MLFLOW_TRACKING_USERNAME', '')
    password = os.getenv('MLFLOW_TRACKING_PASSWORD', '')
    
    print("="*70)
    print("DAGSHUB MLFLOW CONFIGURATION CHECK")
    print("="*70)
    
    if not tracking_uri:
        print("❌ MLFLOW_TRACKING_URI not set")
        return False, None, None, None
    
    if 'dagshub.com' not in tracking_uri.lower():
        print(f"⚠️  MLFLOW_TRACKING_URI doesn't appear to be DagHub: {tracking_uri}")
        print("   This script is designed for DagHub integration")
        return False, None, None, None
    
    if not username:
        print("❌ MLFLOW_TRACKING_USERNAME not set")
        return False, None, None, None
    
    if not password:
        print("❌ MLFLOW_TRACKING_PASSWORD not set")
        return False, None, None, None
    
    print(f"✓ MLFLOW_TRACKING_URI: {tracking_uri}")
    print(f"✓ MLFLOW_TRACKING_USERNAME: {username}")
    print(f"✓ MLFLOW_TRACKING_PASSWORD: {'*' * len(password)}")
    
    return True, tracking_uri, username, password

def extract_repo_info(tracking_uri):
    """Extract repository owner and name from DagHub URI"""
    try:
        # Format: https://dagshub.com/owner/repo.mlflow
        uri_parts = tracking_uri.replace('.mlflow', '').replace('https://', '').replace('http://', '').split('/')
        if len(uri_parts) >= 3:
            repo_owner = uri_parts[1]
            repo_name = uri_parts[2]
            return repo_owner, repo_name
        else:
            print(f"❌ Could not parse DagHub URI: {tracking_uri}")
            return None, None
    except Exception as e:
        print(f"❌ Error parsing URI: {e}")
        return None, None

def initialize_dagshub(repo_owner, repo_name):
    """Initialize DagHub connection"""
    try:
        import dagshub
        print("\n" + "="*70)
        print("INITIALIZING DAGSHUB CONNECTION")
        print("="*70)
        
        dagshub.init(
            repo_owner=repo_owner,
            repo_name=repo_name,
            mlflow=True
        )
        
        print(f"✓ DagHub initialized: {repo_owner}/{repo_name}")
        return True
    except ImportError:
        print("❌ dagshub package not installed")
        print("   Install with: pip install dagshub")
        return False
    except Exception as e:
        print(f"❌ DagHub initialization failed: {e}")
        return False

def test_mlflow_connection():
    """Test MLflow connection"""
    try:
        import mlflow
        
        print("\n" + "="*70)
        print("TESTING MLFLOW CONNECTION")
        print("="*70)
        
        tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
            print(f"✓ MLflow tracking URI set: {tracking_uri}")
        else:
            print("⚠️  MLFLOW_TRACKING_URI not set, using local tracking")
        
        # Try to get or create experiment
        experiment_name = "crypto-volatility-prediction"
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
                print(f"✓ Created experiment: {experiment_name} (ID: {experiment_id})")
            else:
                print(f"✓ Experiment exists: {experiment_name} (ID: {experiment.experiment_id})")
            
            mlflow.set_experiment(experiment_name)
            print(f"✓ Active experiment set: {experiment_name}")
            
        except Exception as e:
            print(f"⚠️  Could not create/access experiment: {e}")
            print("   This might be normal if using remote tracking")
        
        # Test logging
        print("\n" + "="*70)
        print("TESTING MLFLOW LOGGING")
        print("="*70)
        
        with mlflow.start_run(run_name="configuration_test") as run:
            mlflow.log_param("test_param", "test_value")
            mlflow.log_metric("test_metric", 42.0)
            run_id = run.info.run_id
            print(f"✓ Successfully logged test run: {run_id}")
            print(f"✓ View at: {tracking_uri}/#/experiments/0/runs/{run_id}")
        
        return True
        
    except ImportError:
        print("❌ mlflow package not installed")
        print("   Install with: pip install mlflow")
        return False
    except Exception as e:
        print(f"❌ MLflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main configuration function"""
    print("\n" + "="*70)
    print("MLFLOW DAGSHUB CONFIGURATION SCRIPT")
    print("="*70)
    print()
    
    # Step 1: Check credentials
    success, tracking_uri, username, password = check_dagshub_credentials()
    if not success:
        print("\n❌ Configuration incomplete. Please set the following in .env:")
        print("   MLFLOW_TRACKING_URI=https://dagshub.com/YOUR_USERNAME/YOUR_REPO.mlflow")
        print("   MLFLOW_TRACKING_USERNAME=your_username")
        print("   MLFLOW_TRACKING_PASSWORD=your_token")
        print("\n   Get your token from: https://dagshub.com/user/settings/tokens")
        return 1
    
    # Step 2: Extract repo info
    repo_owner, repo_name = extract_repo_info(tracking_uri)
    if not repo_owner or not repo_name:
        return 1
    
    # Step 3: Initialize DagHub
    if not initialize_dagshub(repo_owner, repo_name):
        return 1
    
    # Step 4: Test MLflow
    if not test_mlflow_connection():
        return 1
    
    # Success
    print("\n" + "="*70)
    print("✅ CONFIGURATION COMPLETE!")
    print("="*70)
    print(f"\n✓ DagHub repository: {repo_owner}/{repo_name}")
    print(f"✓ MLflow tracking: {tracking_uri}")
    print(f"✓ Experiment: crypto-volatility-prediction")
    print("\nYour MLflow experiments will now be logged to DagHub!")
    print(f"View them at: {tracking_uri}")
    print()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

