"""
Data Extraction Module for Bitcoin Price Prediction
Uses CryptoCompare FREE API - No key required, reliable historical data
"""

import os
import sys
import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import logging
from dotenv import load_dotenv
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CryptoCompareExtractor:
    """
    Uses CryptoCompare FREE API for historical Bitcoin data
    No API key required for basic endpoints
    https://min-api.cryptocompare.com
    """
    
    def __init__(self):
        """Initialize CryptoCompare API client"""
        self.base_url = "https://min-api.cryptocompare.com/data"
        self.asset = "BTC"
        self.currency = "USD"
        self.requests_made = 0
        
        logger.info("="*70)
        logger.info("CRYPTOCOMPARE FREE API - DATA EXTRACTION")
        logger.info("="*70)
        logger.info("✓ Using CryptoCompare API (no key required)")
        logger.info("✓ Free tier: 100,000 calls/month")
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        headers = {
            'Accept': 'application/json'
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                self.requests_made += 1
                
                if response.status_code == 429:
                    wait_time = 10
                    logger.warning(f"Rate limited, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP Error (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return None
                
            except Exception as e:
                logger.error(f"Request error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return None
        
        return None
    
    def fetch_current_price(self) -> Optional[Dict]:
        """Fetch current Bitcoin price"""
        logger.info(f"Fetching current price for {self.asset}...")
        
        url = f"{self.base_url}/price"
        params = {
            'fsym': self.asset,
            'tsyms': self.currency
        }
        
        response = self._make_request(url, params)
        
        if response and response.status_code == 200:
            data = response.json()
            price = data.get(self.currency, 0)
            
            logger.info(f"✓ Current price: ${price:,.2f}")
            
            return {'price_usd': price, 'symbol': self.asset}
        
        return None
    
    def fetch_historical_data(self, days: int = 30) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data from CryptoCompare
        Free API provides hourly data for any time period
        """
        logger.info(f"Fetching {days} days of historical data...")
        
        # CryptoCompare histohour endpoint - free, no key needed
        url = f"{self.base_url}/v2/histohour"
        
        # Calculate limit (hours)
        limit = days * 24
        
        params = {
            'fsym': self.asset,
            'tsym': self.currency,
            'limit': min(limit, 2000),  # Max 2000 per request
            'toTs': int(datetime.now().timestamp())
        }
        
        logger.info(f"Request: {url}")
        logger.info(f"Fetching {limit} hours of data...")
        
        response = self._make_request(url, params)
        
        if response and response.status_code == 200:
            data = response.json()
            
            if data.get('Response') == 'Error':
                logger.error(f"API Error: {data.get('Message')}")
                return None
            
            # Extract OHLCV data
            candles = data.get('Data', {}).get('Data', [])
            
            if not candles:
                logger.warning("No historical data returned")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(candles)
            
            # Rename columns
            df = df.rename(columns={
                'time': 'timestamp',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volumefrom': 'volume',
                'volumeto': 'volume_usd'
            })
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            
            # Select relevant columns
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'volume_usd']]
            
            # Sort by timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            logger.info(f"✓ Successfully fetched {len(df)} historical records")
            logger.info(f"✓ Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
            logger.info(f"✓ Price range: ${df['close'].min():,.2f} - ${df['close'].max():,.2f}")
            
            return df
        
        logger.error("Failed to fetch historical data")
        return None
    
    def extract_and_save(self, output_dir: str = 'data/raw') -> Optional[str]:
        """Extract data and save to CSV"""
        logger.info("="*70)
        logger.info("STARTING DATA EXTRACTION")
        logger.info("="*70)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Fetch current price
        current_data = self.fetch_current_price()
        if not current_data:
            logger.warning("Could not fetch current price, continuing anyway...")
        
        # Fetch historical data (hourly for 30 days = 720 records)
        historical_df = self.fetch_historical_data(days=30)
        
        if historical_df is None or historical_df.empty:
            logger.error("Failed to fetch historical data")
            return None
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = output_path / f'crypto_raw_{timestamp}.csv'
        
        # Save to CSV
        historical_df.to_csv(csv_filename, index=False)
        logger.info(f"✓ Saved historical data to {csv_filename}")
        
        # Save metadata
        metadata = {
            'extraction_timestamp': timestamp,
            'asset': self.asset,
            'currency': self.currency,
            'records_fetched': len(historical_df),
            'date_range': {
                'start': str(historical_df['timestamp'].min()),
                'end': str(historical_df['timestamp'].max())
            },
            'current_price': current_data,
            'api_requests': self.requests_made,
            'data_source': 'CryptoCompare Free API',
            'data_quality': 'Real OHLCV values from CryptoCompare'
        }
        
        metadata_filename = output_path / f'extraction_metadata_{timestamp}.json'
        with open(metadata_filename, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"✓ Saved metadata to {metadata_filename}")
        
        # Print summary
        logger.info("="*70)
        logger.info("DATA EXTRACTION SUMMARY")
        logger.info("="*70)
        logger.info(f"Records fetched: {len(historical_df)}")
        logger.info(f"Date range: {historical_df['timestamp'].min()} to {historical_df['timestamp'].max()}")
        logger.info(f"Price range: ${historical_df['close'].min():,.2f} - ${historical_df['close'].max():,.2f}")
        logger.info(f"API requests made: {self.requests_made}")
        logger.info(f"Output file: {csv_filename}")
        logger.info("="*70)
        logger.info("✓ DATA EXTRACTION COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        
        return str(csv_filename)


def main():
    """Main execution function"""
    try:
        # Use CryptoCompare (free, no key needed, has historical data)
        extractor = CryptoCompareExtractor()
        
        # Extract and save data
        output_file = extractor.extract_and_save()
        
        if output_file:
            logger.info(f"Success! Data saved to: {output_file}")
            return 0
        else:
            logger.error("Data extraction failed")
            return 1
            
    except Exception as e:
        logger.error(f"Fatal error during extraction: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())