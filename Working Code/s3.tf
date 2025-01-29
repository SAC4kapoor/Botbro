# Data Bucket for BotBro
resource "aws_s3_bucket" "trading_bot_bucket" {
  bucket = var.s3_BotBro_bucket_name

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

# Trigger Bucket for Market Data
resource "aws_s3_bucket" "botbro_data" {
  bucket = var.s3_Market_bucket_name

  tags = {
    Name        = "botbro-data-Market-lambda-trigger"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "market_lambda_bucket_versioning" {
  bucket = aws_s3_bucket.botbro_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Trigger Bucket for Decision Lambda
resource "aws_s3_bucket" "decision_making_bucket" {
  bucket = var.s3_Decision_making_bucket_name

  tags = {
    Name        = "DecisionMakingTriggerBucket"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "decision_making_bucket_versioning" {
  bucket = aws_s3_bucket.decision_making_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_notification" "botbro_lambda_trigger" {
  bucket = aws_s3_bucket.botbro_data.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.market_data.arn
    events              = ["s3:ObjectCreated:Put"]
  }

  depends_on = [aws_lambda_permission.botbro_market_data_s3_trigger]
}

resource "aws_s3_bucket_notification" "decision_making_lambda_trigger" {
  bucket = aws_s3_bucket.decision_making_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.decision_making.arn
    events              = ["s3:ObjectCreated:Put"]
  }

  depends_on = [aws_lambda_permission.botbro_decision_s3_trigger]
}
