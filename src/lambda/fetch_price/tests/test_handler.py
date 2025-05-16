import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path so we can import the handler module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(autouse=True)
def mock_env_variables(monkeypatch):
    """Set up mock environment variables for testing (automatically used in all tests)"""
    monkeypatch.setenv('CRYPTO_API_URL', 'https://api.cryptocompare.com')
    monkeypatch.setenv('ENV', 'test')
    monkeypatch.setenv('RAW_BUCKET', 'test-bucket')
    monkeypatch.setenv('SSM_PARAMETER', '/nebula-stream/test/crypto-api-key')

@pytest.mark.parametrize("api_key", [None, "test-api-key"])
def test_fetch_price(api_key):
    """
    Test fetch_price with mocked responses
    """
    # Import the handler module after environment variables are set
    from handler import fetch_price
    
    # Mock response data
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "BTC": {"USD": 65000},
        "ETH": {"USD": 3500},
        "SOL": {"USD": 150}
    }
    mock_response.raise_for_status.return_value = None

    # Mock the requests.get method
    with patch('requests.get', return_value=mock_response) as mock_get:
        # Call the function
        data = fetch_price(api_key=api_key)
        
        # Verify the expected URL was called
        expected_url = 'https://api.cryptocompare.com/data/price?fsym=BTC,ETH,SOL&tsyms=USD'
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == expected_url
        
        # Verify headers were properly set
        if api_key:
            assert kwargs['headers']['Authorization'] == f'Bearer {api_key}'
        else:
            assert 'Authorization' not in kwargs['headers']
        
        # Verify response handling
        assert isinstance(data, dict)
        assert data == mock_response.json.return_value
