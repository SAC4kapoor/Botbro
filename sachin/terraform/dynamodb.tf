resource "aws_dynamodb_table" "market_data" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "symbol"

  attribute {
    name = "symbol"
    type = "S"
  }

  tags = {
    Environment = var.environment
  }
}
