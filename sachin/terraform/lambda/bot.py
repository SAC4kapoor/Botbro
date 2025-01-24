import json
import boto3
import requests
import os
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
secrets_manager = boto3.client("secretsmanager")

def get_binance_api_keys():
    secret_name = os.environ["SECRETS_MANAGER_NAME"]
    response = secrets_manager.get_secret_value(SecretId=secret_name)
    secrets = json.loads(response["SecretString"])
    return secrets["BINANCE_API_KEY"], secrets["BINANCE_SECRET_KEY"]

def lambda_handler(event, context):
    binance_api_key, binance_secret_key = get_binance_api_keys()
    response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
    price_data = response.json()

    table_name = os.environ["DYNAMODB_TABLE"]
    table = dynamodb.Table(table_name)
    table.put_item(
        Item={
            "symbol": price_data["symbol"],
            "price": Decimal(price_data["price"]),
            "timestamp": int(context.aws_request_id[-8:], 16),
        }
    )

    print(f"Saved {price_data['symbol']} price: {price_data['price']} to DynamoDB.")
