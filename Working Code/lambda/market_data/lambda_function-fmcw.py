import json
import boto3
import requests
import time
from decimal import Decimal
import pandas as pd  # For indicator calculations

# AWS Services
dynamodb = boto3.client("dynamodb")
resource = boto3.resource("dynamodb")
lambda_client = boto3.client("lambda")

def fetch_data(url, retries=3, backoff=2):
    """Fetch data from the given URL with retries."""
    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
            if attempt < retries - 1:
                time.sleep(backoff)
                backoff *= 2
            else:
                raise

def calculate_indicators(historical_prices):
    """Calculate SMA, RSI, and other indicators."""
    prices = pd.Series(historical_prices)
    sma_50 = prices.rolling(window=50).mean().iloc[-1]
    sma_200 = prices.rolling(window=200).mean().iloc[-1]
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs.iloc[-1]))
    return {"sma_50": sma_50, "sma_200": sma_200, "rsi": rsi}

def lambda_handler(event, context):
    try:
        print("Step - Lambda execution started")

        # List of symbols to fetch data for
        symbols = ["BTCUSDT", "ETHUSDT"]  # Truncated for simplicity

        for symbol in symbols:
            # Step 1: Fetch market price and historical data
            print(f"Fetching market data for {symbol}...")
            price_data = fetch_data(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}")
            historical_data = fetch_data(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=200")

            # Parse historical closing prices
            historical_prices = [float(kline[4]) for kline in historical_data]

            # Step 2: Calculate indicators
            indicators = calculate_indicators(historical_prices)
            sma_50, sma_200, rsi = indicators["sma_50"], indicators["sma_200"], indicators["rsi"]

            # Step 3: Pre-check for trade opportunity
            current_price = float(price_data["price"])
            basic_opportunity = (
                current_price > sma_50 > sma_200 and rsi < 30
            )  # Example: Bullish trend + oversold

            # Step 4: Store data in DynamoDB
            table_name = f"{symbol}_MarketData"
            resource.Table(table_name).put_item(
                Item={
                    "timestamp": int(time.time() * 1000),
                    "symbol": symbol,
                    "price": Decimal(current_price),
                    "sma_50": Decimal(str(sma_50)),
                    "sma_200": Decimal(str(sma_200)),
                    "rsi": Decimal(str(rsi)),
                }
            )

            # Step 5: Trigger Decision-Making Lambda if opportunity exists
            if basic_opportunity:
                lambda_client.invoke(
                    FunctionName="DecisionMakingLambda",
                    InvocationType="Event",  # Asynchronous invocation
                    Payload=json.dumps({
                        "symbol": symbol,
                        "current_price": current_price,
                        "indicators": indicators,
                    }),
                )
                print(f"Opportunity detected for {symbol}, triggering Decision-Making Lambda.")

        print("Step - Lambda execution completed successfully")
    except Exception as e:
        print(f"Step - Error occurred: {str(e)}")
        raise e
