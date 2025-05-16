import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'vendor'))

import json
import logging
from datetime import datetime, timezone
import boto3
import requests

essm = boto3.client('ssm')
s3 = boto3.client('s3')

# Enviroment variables set in lambda configuration
env = os.getenv('ENV', 'dev')
bucket_name = os.getenv('RAW_BUCKET', 'nebula-stream-raw-dev')
ssm_parameter_name = os.getenv('SSM_PARAMETER', f'/nebula-stream/{env}/crypto-api-key')
api_url = os.getenv('CRYPTO_API_URL')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_api_key() -> str:
  """
  Retrieve the Crypto API key from the SSM parameter store
  """
  response = essm.get_parameter(
    Name=ssm_parameter_name,
    WithDecryption=True
  )
  return response['Parameter']['Value']

def fetch_price(api_key: str) -> dict:
  """
    Call the crypto API and return the JSON payload.
  """
  headers = {}

  if api_key:
    headers['Authorization'] = f'Bearer {api_key}'

  response = requests.get(f'{api_url}/data/price?fsym=BTC,ETH,SOL&tsyms=USD', headers=headers, timeout=10)
  response.raise_for_status()
  return response.json()

def store_to_s3(data: dict) -> None:
  """
  Store the JSON payload tin S3 with a timestamped key.
  """

  ts = datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')
  key = f"{ts}.json"
  s3.put_object(
    Bucket=bucket_name,
    Key=key,
    Body=json.dumps(data),
    ContentType='application/json'
  )
  logger.info(f"Stored data to s3://{bucket_name}/{key}")

def handler(event: dict, context: dict) -> dict:
  """
  Lambda entry point: fetch price and store in s3
  """
  try:
    api_key = get_api_key()
    data = fetch_price(api_key)
    store_to_s3(data)
    return {
      'statusCode': 200,
      'body': json.dumps({'message': 'Price data fetched and stored successfully'})
    }
  except Exception as e:
    logger.error(f"Error in fetch_price handler: {e}", exc_info=True)
    raise
    