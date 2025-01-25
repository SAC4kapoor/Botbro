import json
import boto3
import requests
import os
from decimal import Decimal

# AWS Services
dynamodb = boto3.resource("dynamodb")
secrets_manager = boto3.client("secretsmanager")

def get_binance_api_keys():
    print("Step - Fetch Binance API keys started")
    secret_name = os.environ["SECRETS_MANAGER_NAME"]
    response = secrets_manager.get_secret_value(SecretId=secret_name)
    secrets = json.loads(response["SecretString"])
    print("Step - Fetch Binance API keys passed")
    return secrets["BINANCE_API_KEY"], secrets["BINANCE_SECRET_KEY"]

def lambda_handler(event, context):
    try:
        print("Step - Lambda execution started")

        # Step 1: Fetch API keys
        binance_api_key, binance_secret_key = get_binance_api_keys()

        # Step 2: Fetch market data from Binance API
        print("Step - Fetch market data started")
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
        price_data = response.json()
        print("Step - Fetch market data passed")

        # Step 3: Store market data in DynamoDB
        print("Step - Store market data in DynamoDB started")
        table_name = os.environ["DYNAMODB_TABLE"]
        table = dynamodb.Table(table_name)
        table.put_item(
            Item={
                "symbol": price_data["symbol"],
                "price": Decimal(price_data["price"]),
                "timestamp": int(context.aws_request_id[-8:], 16),
            }
        )
        print("Step - Store market data in DynamoDB passed")

        print("Step - Lambda execution completed successfully")
    except Exception as e:
        print(f"Step - Error occurred: {str(e)}")
        raise e