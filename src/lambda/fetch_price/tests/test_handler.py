import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timezone

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

def test_handler_success():
    """
    Test successful execution of the handler function
    """
    from handler import handler
    
    # Mock SSM response
    mock_ssm_response = {
        'Parameter': {
            'Value': 'test-api-key'
        }
    }
    
    # Mock API response
    mock_api_response = {
        'BTC': {'USD': 65000},
        'ETH': {'USD': 3500},
        'SOL': {'USD': 150}
    }
    
    # Mock S3 put_object
    mock_s3_put = MagicMock()
    
    with patch('handler.essm.get_parameter', return_value=mock_ssm_response) as mock_ssm, \
         patch('handler.requests.get') as mock_get, \
         patch('handler.s3.put_object', mock_s3_put):
        
        # Setup mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call handler
        result = handler({}, {})
        
        # Verify SSM was called correctly
        mock_ssm.assert_called_once_with(
            Name='/nebula-stream/test/crypto-api-key',
            WithDecryption=True
        )
        
        # Verify API was called correctly
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == 'https://api.cryptocompare.com/data/price?fsym=BTC,ETH,SOL&tsyms=USD'
        assert kwargs['headers']['Authorization'] == 'Bearer test-api-key'
        
        # Verify S3 was called correctly
        mock_s3_put.assert_called_once()
        s3_args, s3_kwargs = mock_s3_put.call_args
        assert s3_kwargs['Bucket'] == 'test-bucket'
        assert s3_kwargs['ContentType'] == 'application/json'
        assert json.loads(s3_kwargs['Body']) == mock_api_response
        
        # Verify handler response
        assert result['statusCode'] == 200
        assert json.loads(result['body']) == {'message': 'Price data fetched and stored successfully'}

def test_handler_ssm_error():
    """
    Test handler when SSM parameter retrieval fails
    """
    from handler import handler
    
    with patch('handler.essm.get_parameter', side_effect=Exception('SSM Error')):
        with pytest.raises(Exception) as exc_info:
            handler({}, {})
        assert str(exc_info.value) == 'SSM Error'

def test_handler_api_error():
    """
    Test handler when API call fails
    """
    from handler import handler
    
    # Mock SSM response
    mock_ssm_response = {
        'Parameter': {
            'Value': 'test-api-key'
        }
    }
    
    with patch('handler.essm.get_parameter', return_value=mock_ssm_response), \
         patch('handler.requests.get', side_effect=Exception('API Error')):
        with pytest.raises(Exception) as exc_info:
            handler({}, {})
        assert str(exc_info.value) == 'API Error'

def test_handler_s3_error():
    """
    Test handler when S3 upload fails
    """
    from handler import handler
    
    # Mock SSM response
    mock_ssm_response = {
        'Parameter': {
            'Value': 'test-api-key'
        }
    }
    
    # Mock API response
    mock_api_response = {
        'BTC': {'USD': 65000},
        'ETH': {'USD': 3500},
        'SOL': {'USD': 150}
    }
    
    with patch('handler.essm.get_parameter', return_value=mock_ssm_response), \
         patch('handler.requests.get') as mock_get, \
         patch('handler.s3.put_object', side_effect=Exception('S3 Error')):
        
        # Setup mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            handler({}, {})
        assert str(exc_info.value) == 'S3 Error'

def test_store_to_s3():
    """
    Test store_to_s3 function with focus on timestamp formatting and S3 storage
    """
    from handler import store_to_s3
    
    # Mock data
    test_data = {
        'BTC': {'USD': 65000},
        'ETH': {'USD': 3500},
        'SOL': {'USD': 150}
    }
    
    # Mock S3 client
    mock_s3 = MagicMock()
    
    with patch('handler.s3', mock_s3):
        # Call the function
        store_to_s3(test_data)
        
        # Verify S3 was called
        mock_s3.put_object.assert_called_once()
        
        # Get the arguments used in the call
        args, kwargs = mock_s3.put_object.call_args
        
        # Verify bucket name
        assert kwargs['Bucket'] == 'test-bucket'
        
        # Verify content type
        assert kwargs['ContentType'] == 'application/json'
        
        # Verify the data was properly JSON serialized
        assert json.loads(kwargs['Body']) == test_data
        
        # Verify the key format (timestamp.json)
        key = kwargs['Key']
        assert key.endswith('.json')
        
        # Extract timestamp from key
        timestamp_str = key[:-5]  # Remove '.json'
        
        # Verify timestamp format
        try:
            # Parse the timestamp string back to datetime
            parsed_time = datetime.strptime(timestamp_str, '%Y-%m-%d_%H-%M-%S')
            # Add UTC timezone to make it timezone-aware
            parsed_time = parsed_time.replace(tzinfo=timezone.utc)
            # Verify it's a recent timestamp (within last minute)
            now = datetime.now(timezone.utc)
            time_diff = abs((now - parsed_time).total_seconds())
            assert time_diff < 60, "Timestamp should be recent"
        except ValueError as e:
            pytest.fail(f"Invalid timestamp format: {e}")

def test_store_to_s3_with_empty_data():
    """
    Test store_to_s3 function with empty data
    """
    from handler import store_to_s3
    
    # Mock S3 client
    mock_s3 = MagicMock()
    
    with patch('handler.s3', mock_s3):
        # Call the function with empty data
        store_to_s3({})
        
        # Verify S3 was called
        mock_s3.put_object.assert_called_once()
        
        # Get the arguments used in the call
        args, kwargs = mock_s3.put_object.call_args
        
        # Verify empty data was properly stored
        assert json.loads(kwargs['Body']) == {}
        
        # Verify the key format is still correct
        key = kwargs['Key']
        assert key.endswith('.json')
        assert len(key) > 5  # Should have timestamp + .json
