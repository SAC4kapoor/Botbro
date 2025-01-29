import json
import boto3
import requests
import hmac
import hashlib
import time
from decimal import Decimal
from urllib.parse import urlencode

# AWS Services
dynamodb = boto3.client("dynamodb")
resource = boto3.resource("dynamodb")
secretsmanager = boto3.client("secretsmanager")

def get_binance_keys(secret_name):
    """Retrieve Binance API keys from AWS Secrets Manager."""
    try:
        secret_response = secretsmanager.get_secret_value(SecretId=secret_name)
        secret = json.loads(secret_response["SecretString"])
        return secret["BINANCE_API_KEY"], secret["BINANCE_SECRET_KEY"]
    except Exception as e:
        print(f"Error fetching secret {secret_name}: {str(e)}")
        raise e

def sign_request(params, secret_key):
    """Sign Binance API request using HMAC-SHA256."""
    query_string = urlencode(params)
    signature = hmac.new(
        secret_key.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    params["signature"] = signature
    return params

def fetch_binance_balance(api_key, secret_key):
    """Fetch Binance account balance using signed API request."""
    endpoint = "/api/v3/account"
    url = f"https://api.binance.com{endpoint}"

    # Add mandatory parameters
    params = {
        "timestamp": int(time.time() * 1000),  # Current timestamp in milliseconds
    }

    # Sign the request
    signed_params = sign_request(params, secret_key)

    # Add API Key to the headers
    headers = {
        "X-MBX-APIKEY": api_key
    }

    # Make the API request
    response = requests.get(url, headers=headers, params=signed_params)
    response.raise_for_status()  # Raise error if the request fails
    return response.json()

def create_dynamodb_table_if_not_exists(table_name):
    """Create DynamoDB table if it does not exist."""
    try:
        dynamodb.describe_table(TableName=table_name)
        print(f"Step - Table {table_name} already exists.")
    except dynamodb.exceptions.ResourceNotFoundException:
        print(f"Step - Creating table {table_name}...")
        dynamodb.create_table(
            TableName=table_name,
            AttributeDefinitions=[{"AttributeName": "timestamp", "AttributeType": "N"}],
            KeySchema=[{"AttributeName": "timestamp", "KeyType": "HASH"}],  # Partition key
            BillingMode="PAY_PER_REQUEST",
        )
        resource.Table(table_name).wait_until_exists()
        print(f"Step - Table {table_name} created successfully.")

def lambda_handler(event, context):
    try:
        print("Step - Lambda execution started")

        # Step 1: Fetch Binance API keys from Secrets Manager
        secret_name = "binance_api_keys"  # Adjust this to match your secret name
        api_key, secret_key = get_binance_keys(secret_name)
        print("Step - Successfully fetched Binance API keys")

        # Step 2: Fetch Binance account balance
        print("Fetching Binance account balance...")
        balance_data = fetch_binance_balance(api_key, secret_key)
        print("Step - Successfully fetched Binance account balance")

        # Step 3: Ensure a table exists for storing balance
        table_name = "BinanceBalances"
        create_dynamodb_table_if_not_exists(table_name)
        print(f"Step - Table {table_name} is ready for storing data")

        # Step 4: Store balance data in the table
        current_timestamp = int(time.time() * 1000)  # Current Unix timestamp in milliseconds
        print("Step - Timestamp generated")

        # Define a minimum threshold to store balances (to avoid storing values too close to zero)
        min_balance_threshold = Decimal('1e-6')  # e.g., Store values greater than or equal to 0.000001
        print(f"Step - Using threshold: {min_balance_threshold} for storing balances")

        # Parse and store only non-zero balances
        for asset in balance_data["balances"]:
            free = Decimal(asset["free"])
            locked = Decimal(asset["locked"])

            # Check if either free or locked balance exceeds the threshold
            if free >= min_balance_threshold or locked >= min_balance_threshold:
                table = resource.Table(table_name)
                table.put_item(
                    Item={
                        "timestamp": current_timestamp,  # Partition key
                        "asset": asset["asset"],  # Asset name (e.g., BTC, ETH)
                        "free": free,  # Free balance
                        "locked": locked,  # Locked balance
                    }
                )
                print(f"Step - Stored balance for {asset['asset']} - Free: {free}, Locked: {locked}")

        print("Step - Binance balances stored successfully in DynamoDB")        
        
    except Exception as e:
        print(f"Step - Error occurred: {str(e)}")
        raise e
