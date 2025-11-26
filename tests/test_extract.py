"""
Unit tests for data extraction module
Tests CryptoCompare API extractor (free, no key required)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from pathlib import Path
import os
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data.extract import CryptoCompareExtractor


class TestCryptoCompareExtractor:
    """Test cases for CryptoCompareExtractor"""
    
    @pytest.fixture
    def extractor(self):
        """Create extractor instance"""
        return CryptoCompareExtractor()
    
    @pytest.fixture
    def mock_price_response(self):
        """Mock current price API response"""
        return {
            'USD': 87696.36
        }
    
    @pytest.fixture
    def mock_historical_response(self):
        """Mock historical data response from CryptoCompare"""
        return {
            'Response': 'Success',
            'Type': 100,
            'Data': {
                'Data': [
                    {
                        'time': 1699900000,
                        'open': 50000.00,
                        'high': 50100.00,
                        'low': 49900.00,
                        'close': 50050.00,
                        'volumefrom': 100.5,
                        'volumeto': 5025125.00
                    },
                    {
                        'time': 1699903600,
                        'open': 50050.00,
                        'high': 50150.00,
                        'low': 50000.00,
                        'close': 50100.00,
                        'volumefrom': 105.2,
                        'volumeto': 5270520.00
                    }
                ]
            }
        }
    
    def test_initialization(self, extractor):
        """Test extractor initialization"""
        assert extractor.base_url == "https://min-api.cryptocompare.com/data"
        assert extractor.asset == "BTC"
        assert extractor.currency == "USD"
        assert extractor.requests_made == 0
        # CryptoCompare doesn't need API key
        assert hasattr(extractor, 'base_url')
    
    @patch('requests.get')
    def test_fetch_current_price_success(self, mock_get, extractor, mock_price_response):
        """Test successful current price fetch"""
        mock_response = Mock()
        mock_response.json.return_value = mock_price_response
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = extractor.fetch_current_price()
        
        assert result is not None
        assert 'price_usd' in result
        assert 'symbol' in result
        assert result['price_usd'] == 87696.36
        assert result['symbol'] == 'BTC'
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_fetch_current_price_failure(self, mock_get, extractor):
        """Test failed current price fetch"""
        mock_get.side_effect = Exception("API Error")
        
        result = extractor.fetch_current_price()
        
        assert result is None
    
    @patch('requests.get')
    def test_fetch_historical_data_success(self, mock_get, extractor, mock_historical_response):
        """Test successful historical data fetch"""
        mock_response = Mock()
        mock_response.json.return_value = mock_historical_response
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = extractor.fetch_historical_data(days=1)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'timestamp' in result.columns
        assert 'open' in result.columns
        assert 'high' in result.columns
        assert 'low' in result.columns
        assert 'close' in result.columns
        assert 'volume' in result.columns
        assert 'volume_usd' in result.columns
    
    @patch('requests.get')
    def test_fetch_historical_data_failure(self, mock_get, extractor):
        """Test failed historical data fetch"""
        mock_response = Mock()
        mock_response.json.return_value = {'Response': 'Error', 'Message': 'API Error'}
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = extractor.fetch_historical_data(days=1)
        
        assert result is None
    
    @patch.object(CryptoCompareExtractor, 'fetch_current_price')
    @patch.object(CryptoCompareExtractor, 'fetch_historical_data')
    def test_extract_and_save(
        self,
        mock_historical,
        mock_current,
        extractor,
        mock_price_response,
        mock_historical_response
    ):
        """Test complete extract and save process"""
        # Setup mocks
        mock_current.return_value = {'price_usd': 87696.36, 'symbol': 'BTC'}
        
        # Create DataFrame from mock data
        df = pd.DataFrame(mock_historical_response['Data']['Data'])
        df['timestamp'] = pd.to_datetime(df['time'], unit='s')
        df = df.rename(columns={
            'volumefrom': 'volume',
            'volumeto': 'volume_usd'
        })
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'volume_usd']]
        mock_historical.return_value = df
        
        # Create temp directory for output
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            # Execute
            output_path = extractor.extract_and_save(output_dir=tmpdir)
            
            # Verify
            assert output_path is not None
            assert Path(output_path).exists()
            assert Path(output_path).suffix == '.csv'
            
            # Verify CSV content
            saved_df = pd.read_csv(output_path)
            assert len(saved_df) == 2
            assert 'timestamp' in saved_df.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
