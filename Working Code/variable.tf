variable "aws_region" {
  default     = "us-east-1"
  description = "AWS region to deploy resources"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for Lambda deployment packages"
  default     = "trading-bot-bucket"
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table for market data"
  default     = "MarketData"
}

variable "secrets_manager_name" {
  description = "Name of the Secrets Manager entry for API keys"
  default     = "BinanceAPIKeys"
}

variable "binance_api_key" {
  description = "Your Binance API key"
}

variable "binance_secret_key" {
  description = "Your Binance Secret key"
}

variable "environment" {
  description = "Deployment environment"
  default     = "Production"
}
