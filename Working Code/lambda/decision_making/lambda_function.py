import json
import boto3
import requests
import numpy as np

# AWS Services
lambda_client = boto3.client("lambda")
dynamodb = boto3.resource("dynamodb")

# Constants
SENTIMENT_API_URL = "https://api.sentimentapi.com/v1/crypto"
MAX_PORTFOLIO_ALLOCATION = 0.2
MIN_SENTIMENT_SCORE = 0.5

### SMA & RSI Calculation Functions ###
def simple_moving_average(data, period):
    """Calculate Simple Moving Average (SMA)."""
    if len(data) < period:
        return np.mean(data)  # Return average of available data instead of None
    return np.mean(data[-period:])

def relative_strength_index(data, period=14):
    """Calculate Relative Strength Index (RSI)."""
    if len(data) < period:
        return 50  # Default to neutral RSI if not enough data

    deltas = np.diff(data)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])

    if avg_loss == 0:
        return 100  # RSI is 100 if no losses

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_technical_indicators(data):
    """Calculate SMA and RSI without external dependencies."""
    print("Step 1: Calculating technical indicators (SMA 50, SMA 200, RSI)...")
    sma_50 = simple_moving_average(data, 50)
    sma_200 = simple_moving_average(data, 200)
    rsi = relative_strength_index(data, 14)

    print(f"Computed Indicators - SMA_50: {sma_50}, SMA_200: {sma_200}, RSI: {rsi}")
    print("Step 1 Completed: Technical indicators calculated successfully.")

    return {
        "sma_50": sma_50 if sma_50 is not None else 0,
        "sma_200": sma_200 if sma_200 is not None else 0,
        "rsi": rsi if rsi is not None else 50
    }

### Fetch Data from External Services ###
def fetch_sentiment_score(symbol):
    """Fetch sentiment score for a given crypto symbol."""
    print(f"Step 2: Fetching sentiment score for {symbol}...")
    try:
        response = requests.get(f"{SENTIMENT_API_URL}?symbol={symbol}")
        response.raise_for_status()
        sentiment_data = response.json()
        score = sentiment_data.get("sentiment_score", 0)
        print(f"Sentiment Score for {symbol}: {score}")
        print("Step 2 Completed: Sentiment score fetched successfully.")
        return score
    except Exception as e:
        print(f"Error fetching sentiment score: {e}")
        return 0  # Default to neutral sentiment if error

def fetch_portfolio_allocation(symbol):
    """Fetch portfolio allocation for the given symbol from DynamoDB."""
    print(f"Step 3: Fetching portfolio allocation for {symbol}...")
    try:
        table = dynamodb.Table("PortfolioAllocation")
        response = table.get_item(Key={"symbol": symbol})
        allocation = response.get("Item", {}).get("allocation", 0)
        print(f"Portfolio Allocation for {symbol}: {allocation}")
        print("Step 3 Completed: Portfolio allocation fetched successfully.")
        return float(allocation)
    except Exception as e:
        print(f"Error fetching portfolio allocation: {e}")
        return 0  # Default to no allocation if error

### Trading Strategy ###
def evaluate_opportunity(data):
    """Evaluate whether there's an opportunity to trade."""
    print(f"Step 4: Evaluating trade opportunity for {data['symbol']}...")
    symbol = data["symbol"]
    current_price = data["current_price"]
    indicators = data["indicators"]

    if any(v is None for v in indicators.values()):
        print(f"Skipping trade evaluation due to missing indicator values: {indicators}")
        return False

    is_bullish = current_price > indicators["sma_50"] > indicators["sma_200"]
    is_oversold = indicators["rsi"] < 30

    if is_bullish and is_oversold:
        print(f"Trade Opportunity Detected for {symbol}!")
        print("Step 4 Completed: Trade opportunity evaluation successful.")
        return True
    
    print("Step 4 Completed: No opportunity detected for trade.")
    return False

### AWS Lambda Handler ###
def lambda_handler(event, context):
    """Main Lambda handler function."""
    try:
        print("🚀 Lambda Execution Started...")
        print(f"Event received: {json.dumps(event)}")

        symbol = event["symbol"]
        current_price = float(event["current_price"])
        close_prices = event["close_prices"]

        if not isinstance(close_prices, list) or len(close_prices) < 2:
            return {"status": "ERROR", "reason": "Invalid or insufficient close_prices data"}

        # Step 1: Calculate technical indicators
        indicators = calculate_technical_indicators(close_prices)

        # Step 2: Evaluate basic opportunity
        if not evaluate_opportunity({"symbol": symbol, "current_price": current_price, "indicators": indicators}):
            print("No opportunity detected. Lambda execution completed.")
            return {"status": "NO_OPPORTUNITY", "reason": "No trade opportunity"}

        # Step 3: Fetch sentiment score
        sentiment_score = fetch_sentiment_score(symbol)
        if sentiment_score < MIN_SENTIMENT_SCORE:
            print("No opportunity detected due to low sentiment score. Lambda execution completed.")
            return {"status": "NO_OPPORTUNITY", "reason": "Low sentiment"}

        # Step 4: Fetch portfolio allocation
        portfolio_allocation = fetch_portfolio_allocation(symbol)
        if portfolio_allocation >= MAX_PORTFOLIO_ALLOCATION:
            print("No opportunity detected due to portfolio allocation limit. Lambda execution completed.")
            return {"status": "NO_OPPORTUNITY", "reason": "Portfolio allocation limit exceeded"}

        # Step 5: Trigger balance check Lambda and place order
        print(f"Step 5: Triggering Balance Check Lambda for {symbol}...")
        payload = {
            "symbol": symbol,
            "order_type": "BUY",
            "price": current_price
        }
        response = lambda_client.invoke(
            FunctionName="BalanceCheckLambda",
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )

        response_payload = json.loads(response["Payload"].read())
        print(f"Balance Check Lambda response: {response_payload}")
        print("Step 5 Completed: Balance check triggered successfully.")

        if response_payload.get("status") == "SUCCESS":
            print(f"Trade executed for {symbol} at {current_price}.")
            print("🚀 Lambda Execution Completed Successfully!")
            return {"status": "TRADE_EXECUTED", "symbol": symbol, "price": current_price}
        else:
            print("No opportunity detected after balance check. Lambda execution completed.")
            return {"status": "NO_OPPORTUNITY", "reason": response_payload.get("reason")}

    except Exception as e:
        print(f"Error in Decision-Making Lambda: {str(e)}")
        return {"status": "ERROR", "reason": str(e)}