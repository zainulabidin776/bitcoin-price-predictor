"""
Data Extraction Module for CoinCap Pro API
Fetches real-time cryptocurrency data for volatility prediction

API Documentation: https://pro.coincap.io/api-docs
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv
import logging
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class CoinCapExtractor:
    """Extract cryptocurrency data from CoinCap Pro API"""
    
    def __init__(self):
        self.api_key = os.getenv('COINCAP_API_KEY')
        self.base_url = os.getenv('COINCAP_BASE_URL', 'https://api.coincap.io/v2')
        self.asset = os.getenv('CRYPTO_ASSET', 'bitcoin')
        
        # According to CoinCap Pro docs, use Bearer token
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip'
        }
        
        self.raw_data_dir = Path('data/raw')
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Track API usage
        self.requests_made = 0
        self.rate_limit = int(os.getenv('COINCAP_RATE_LIMIT', 4000))
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make API request with rate limiting and error handling
        
        Args:
            endpoint: API endpoint (e.g., 'assets/bitcoin')
            params: Query parameters
            
        Returns:
            Response data dictionary
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            # Check rate limit
            if self.requests_made >= self.rate_limit:
                logger.warning(f"Approaching rate limit ({self.requests_made}/{self.rate_limit})")
            
            # Make request
            response = requests.get(
                url, 
                headers=self.headers, 
                params=params,
                timeout=30
            )
            
            self.requests_made += 1
            
            # Check response status
            response.raise_for_status()
            
            # Parse JSON
            data = response.json()
            
            # Log success
            logger.info(f"✓ API request successful: {endpoint}")
            
            return data
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            logger.error(f"Response: {response.text if 'response' in locals() else 'No response'}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise
    
    def fetch_current_price(self) -> Dict:
        """
        Fetch current price and market data
        
        Endpoint: GET /v2/assets/{id}
        Documentation: https://docs.coincap.io/#89deffa0-ab03-4e0a-8d92-637a857d2c91
        """
        try:
            endpoint = f"assets/{self.asset}"
            data = self._make_request(endpoint)
            
            if 'data' in data:
                logger.info(f"Current {self.asset} price: ${float(data['data']['priceUsd']):.2f}")
                return data['data']
            else:
                raise ValueError("No data in response")
                
        except Exception as e:
            logger.error(f"Failed to fetch current price: {e}")
            raise
    
    def fetch_historical_data(self, interval: str = 'm5', days: int = 30) -> pd.DataFrame:
        """
        Fetch historical price data
        
        Endpoint: GET /v2/assets/{id}/history
        Documentation: https://docs.coincap.io/#61e708a8-8876-4fb2-a418-86f12f308978
        
        Args:
            interval: Time interval - Options:
                - m1, m5, m15, m30 (minutes)
                - h1, h2, h6, h12 (hours)  
                - d1 (day)
            days: Number of days of historical data
        
        Returns:
            DataFrame with historical OHLCV data
        """
        try:
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # Convert to milliseconds (CoinCap uses millisecond timestamps)
            start_ms = int(start_time.timestamp() * 1000)
            end_ms = int(end_time.timestamp() * 1000)
            
            # Build endpoint and parameters
            endpoint = f"assets/{self.asset}/history"
            params = {
                'interval': interval,
                'start': start_ms,
                'end': end_ms
            }
            
            logger.info(f"Fetching {days} days of {interval} data for {self.asset}...")
            
            # Make request
            data = self._make_request(endpoint, params)
            
            if 'data' not in data or not data['data']:
                raise ValueError("No historical data returned from API")
            
            # Convert to DataFrame
            df = pd.DataFrame(data['data'])
            
            # Parse and format data
            df['date'] = pd.to_datetime(df['time'], unit='ms')
            df['priceUsd'] = pd.to_numeric(df['priceUsd'], errors='coerce')
            
            # Sort by date
            df = df.sort_values('date').reset_index(drop=True)
            
            logger.info(f"✓ Successfully fetched {len(df)} historical records")
            logger.info(f"  Date range: {df['date'].min()} to {df['date'].max()}")
            logger.info(f"  Price range: ${df['priceUsd'].min():.2f} - ${df['priceUsd'].max():.2f}")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")
            raise
    
    def fetch_market_data(self) -> Dict:
        """
        Fetch market statistics and rankings
        
        Endpoint: GET /v2/assets
        """
        try:
            endpoint = "assets"
            params = {'limit': 100}
            
            data = self._make_request(endpoint, params)
            
            # Find our asset in the list
            if 'data' in data:
                asset_data = next(
                    (item for item in data['data'] if item['id'] == self.asset),
                    None
                )
                
                if asset_data is None:
                    raise ValueError(f"Asset {self.asset} not found in market data")
                
                logger.info(f"✓ Market data - Rank: #{asset_data.get('rank', 'N/A')}, "
                          f"Market Cap: ${float(asset_data.get('marketCapUsd', 0)):,.0f}")
                
                return asset_data
            else:
                raise ValueError("No data in market response")
                
        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            raise
    
    def fetch_rates(self) -> pd.DataFrame:
        """
        Fetch exchange rates (optional - for additional features)
        
        Endpoint: GET /v2/rates
        """
        try:
            endpoint = "rates"
            data = self._make_request(endpoint)
            
            if 'data' in data:
                rates_df = pd.DataFrame(data['data'])
                logger.info(f"✓ Fetched {len(rates_df)} exchange rates")
                return rates_df
            else:
                logger.warning("No rates data available")
                return pd.DataFrame()
                
        except Exception as e:
            logger.warning(f"Could not fetch rates (non-critical): {e}")
            return pd.DataFrame()
    
    def get_api_usage_stats(self) -> Dict:
        """Get API usage statistics"""
        return {
            'requests_made': self.requests_made,
            'rate_limit': self.rate_limit,
            'remaining': self.rate_limit - self.requests_made,
            'usage_percentage': (self.requests_made / self.rate_limit) * 100
        }
    
    def extract_and_save(self) -> str:
        """
        Main extraction method - fetches all data and saves to disk
        
        Returns:
            Path to saved raw data file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            logger.info("=" * 70)
            logger.info("STARTING DATA EXTRACTION FROM COINCAP PRO API")
            logger.info("=" * 70)
            
            # Fetch all data sources
            logger.info("\n[1/3] Fetching current price...")
            current_price = self.fetch_current_price()
            
            logger.info("\n[2/3] Fetching historical data...")
            historical_data = self.fetch_historical_data(interval='m5', days=30)
            
            logger.info("\n[3/3] Fetching market data...")
            market_data = self.fetch_market_data()
            
            # Combine into single dataset
            extraction_metadata = {
                'timestamp': timestamp,
                'extraction_time': datetime.now().isoformat(),
                'asset': self.asset,
                'api_base_url': self.base_url,
                'current_price': current_price,
                'market_data': market_data,
                'records_count': len(historical_data),
                'date_range': {
                    'start': str(historical_data['date'].min()),
                    'end': str(historical_data['date'].max())
                },
                'api_usage': self.get_api_usage_stats()
            }
            
            # Save historical data as CSV
            csv_filename = f"crypto_raw_{timestamp}.csv"
            csv_path = self.raw_data_dir / csv_filename
            historical_data.to_csv(csv_path, index=False)
            logger.info(f"\n✓ Saved historical data to {csv_path}")
            
            # Save metadata as JSON
            json_filename = f"extraction_metadata_{timestamp}.json"
            json_path = self.raw_data_dir / json_filename
            with open(json_path, 'w') as f:
                json.dump(extraction_metadata, f, indent=2, default=str)
            logger.info(f"✓ Saved metadata to {json_path}")
            
            # Print summary
            logger.info("\n" + "=" * 70)
            logger.info("✓ DATA EXTRACTION COMPLETED SUCCESSFULLY")
            logger.info("=" * 70)
            logger.info(f"Records extracted: {len(historical_data)}")
            logger.info(f"Date range: {historical_data['date'].min()} to {historical_data['date'].max()}")
            logger.info(f"Current price: ${float(current_price['priceUsd']):.2f}")
            logger.info(f"API requests made: {self.requests_made}/{self.rate_limit}")
            logger.info("=" * 70)
            
            return str(csv_path)
            
        except Exception as e:
            logger.error(f"\n✗ Extraction failed: {e}")
            logger.error(f"API requests made: {self.requests_made}")
            raise
    
    def validate_api_connection(self) -> bool:
        """Validate API connection and credentials"""
        try:
            logger.info("Validating CoinCap Pro API connection...")
            
            # Test request to assets endpoint
            endpoint = f"assets/{self.asset}"
            data = self._make_request(endpoint)
            
            if 'data' in data:
                logger.info("✓ API connection validated successfully")
                logger.info(f"  Asset: {data['data'].get('name', self.asset)}")
                logger.info(f"  Symbol: {data['data'].get('symbol', 'N/A')}")
                logger.info(f"  Price: ${float(data['data'].get('priceUsd', 0)):.2f}")
                logger.info(f"  API Key: ...{self.api_key[-8:]}")  # Show last 8 chars
                return True
            else:
                logger.error("✗ API validation failed - No data in response")
                return False
                
        except Exception as e:
            logger.error(f"✗ API validation failed: {e}")
            logger.error(f"  Please check your API key in .env file")
            logger.error(f"  API Key used: ...{self.api_key[-8:] if self.api_key else 'NOT SET'}")
            return False


def main():
    """Main execution function"""
    try:
        extractor = CoinCapExtractor()
        
        # Validate connection
        logger.info("\n" + "=" * 70)
        logger.info("COINCAP PRO API - DATA EXTRACTION")
        logger.info("=" * 70)
        
        if not extractor.validate_api_connection():
            raise ConnectionError("Failed to connect to CoinCap Pro API")
        
        # Extract data
        output_path = extractor.extract_and_save()
        
        print("\n" + "=" * 70)
        print("✓ DATA EXTRACTION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"✓ Output file: {output_path}")
        print(f"✓ API requests used: {extractor.requests_made}/{extractor.rate_limit}")
        print("=" * 70)
        
        return output_path
        
    except Exception as e:
        logger.error(f"\n✗ Extraction process failed: {e}")
        raise


if __name__ == "__main__":
    main()