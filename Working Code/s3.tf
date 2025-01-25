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

resource "aws_s3_bucket" "botbro_data" {
  bucket = "botbro-data"

  tags = {
    Name        = "botbro-data-allincluded"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_notification" "botbro_lambda_trigger" {
  bucket = aws_s3_bucket.botbro_data.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.trading_bot.arn
    events              = ["s3:ObjectCreated:Put"]
  }

  depends_on = [aws_lambda_permission.botbro_s3_trigger]
}

