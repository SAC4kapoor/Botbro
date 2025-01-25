resource "aws_secretsmanager_secret" "binance_api_keys" {
  name        = var.secrets_manager_name
  description = "Binance API keys for the trading bot"

  tags = {
    Environment = var.environment
  }
}
resource "aws_secretsmanager_secret_version" "binance_api_keys_value" {
  secret_id = aws_secretsmanager_secret.binance_api_keys.id

  secret_string = jsonencode({
    BINANCE_API_KEY    = var.binance_api_key,
    BINANCE_SECRET_KEY = var.binance_secret_key
  })
}
