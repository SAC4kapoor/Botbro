resource "aws_s3_bucket" "trading_bot_bucket" {
  bucket = var.s3_bucket_name

  tags = {
    Name        = "TradingBotBucket"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "trading_bot_bucket_versioning" {
  bucket = aws_s3_bucket.trading_bot_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}
