"""
Unit tests for data extraction module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from pathlib import Path
import os
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data.extract import CoinCapExtractor


class TestCoinCapExtractor:
    """Test cases for CoinCapExtractor"""
    
    @pytest.fixture
    def extractor(self):
        """Create extractor instance"""
        return CoinCapExtractor()
    
    @pytest.fixture
    def mock_api_response(self):
        """Mock API response data"""
        return {
            'data': {
                'id': 'bitcoin',
                'rank': '1',
                'symbol': 'BTC',
                'name': 'Bitcoin',
                'priceUsd': '50000.123456',
                'marketCapUsd': '1000000000000',
                'volumeUsd24Hr': '20000000000',
                'changePercent24Hr': '2.5'
            }
        }
    
    @pytest.fixture
    def mock_historical_response(self):
        """Mock historical data response"""
        return {
            'data': [
                {
                    'priceUsd': '50000.00',
                    'time': 1699900000000,
                    'date': '2023-11-14T00:00:00.000Z'
                },
                {
                    'priceUsd': '50100.00',
                    'time': 1699900300000,
                    'date': '2023-11-14T00:05:00.000Z'
                }
            ]
        }
    
    def test_initialization(self, extractor):
        """Test extractor initialization"""
        assert extractor.api_key is not None
        assert extractor.base_url is not None
        assert extractor.asset == 'bitcoin'
        assert extractor.raw_data_dir.exists()
    
    @patch('requests.get')
    def test_fetch_current_price_success(self, mock_get, extractor, mock_api_response):
        """Test successful current price fetch"""
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = extractor.fetch_current_price()
        
        assert result is not None
        assert result['id'] == 'bitcoin'
        assert 'priceUsd' in result
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_fetch_current_price_failure(self, mock_get, extractor):
        """Test failed current price fetch"""
        mock_get.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            extractor.fetch_current_price()
    
    @patch('requests.get')
    def test_fetch_historical_data_success(self, mock_get, extractor, mock_historical_response):
        """Test successful historical data fetch"""
        mock_response = Mock()
        mock_response.json.return_value = mock_historical_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = extractor.fetch_historical_data(interval='m5', days=1)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'priceUsd' in result.columns
        assert 'date' in result.columns
    
    @patch('requests.get')
    def test_fetch_market_data_success(self, mock_get, extractor, mock_api_response):
        """Test successful market data fetch"""
        mock_response = Mock()
        mock_response.json.return_value = {'data': [mock_api_response['data']]}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = extractor.fetch_market_data()
        
        assert result is not None
        assert result['id'] == 'bitcoin'
    
    @patch('requests.get')
    def test_validate_api_connection_success(self, mock_get, extractor, mock_api_response):
        """Test successful API validation"""
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = extractor.validate_api_connection()
        
        assert result is True
    
    @patch('requests.get')
    def test_validate_api_connection_failure(self, mock_get, extractor):
        """Test failed API validation"""
        mock_get.side_effect = Exception("Connection Error")
        
        result = extractor.validate_api_connection()
        
        assert result is False
    
    @patch.object(CoinCapExtractor, 'fetch_current_price')
    @patch.object(CoinCapExtractor, 'fetch_historical_data')
    @patch.object(CoinCapExtractor, 'fetch_market_data')
    def test_extract_and_save(
        self,
        mock_market,
        mock_historical,
        mock_current,
        extractor,
        mock_api_response,
        mock_historical_response
    ):
        """Test complete extract and save process"""
        # Setup mocks
        mock_current.return_value = mock_api_response['data']
        mock_market.return_value = mock_api_response['data']
        
        # Create DataFrame from mock data
        df = pd.DataFrame(mock_historical_response['data'])
        df['date'] = pd.to_datetime(df['date'])
        df['priceUsd'] = df['priceUsd'].astype(float)
        mock_historical.return_value = df
        
        # Execute
        output_path = extractor.extract_and_save()
        
        # Verify
        assert output_path is not None
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.csv'
        
        # Cleanup
        Path(output_path).unlink()
        # Also remove JSON metadata
        json_file = Path(output_path).parent / Path(output_path).stem.replace('crypto_raw', 'extraction_metadata')
        json_file = json_file.with_suffix('.json')
        if json_file.exists():
            json_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])