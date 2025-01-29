resource "aws_dynamodb_table" "binance_balances" {
  name           = "BinanceBalances"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "timestamp"

  attribute {
    name = "timestamp"
    type = "N"
  }

  tags = {
    Environment = var.environment
  }
}
