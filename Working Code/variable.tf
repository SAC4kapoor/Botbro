variable "aws_region" {
  default     = "us-east-1"
  description = "AWS region to deploy resources"
}

variable "s3_BotBro_bucket_name" {
  description = "Name of the S3 bucket for Lambda deployment packages"
  default     = "trading-bot-bucket"
}

variable "s3_Market_bucket_name" {
  description = "Name of the S3 bucket for Lambda deployment packages"
  
}

variable "s3_Decision_making_bucket_name" {
  description = "Name of the S3 bucket for Lambda deployment packages"
  
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

variable "lambda_function_name" {
  description = "The name of the Lambda function"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet"
  type        = string
}

variable "private_subnet_cidr" {
  description = "CIDR block for the private subnet"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for the Lambda function"
  type        = list(string)
}
