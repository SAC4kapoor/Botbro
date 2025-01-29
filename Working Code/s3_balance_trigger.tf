resource "aws_s3_bucket" "botbro_balance_data" {
  bucket = "botbro-balance-data"

  tags = {
    Name        = "botbro-data-balance"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_notification" "botbro_fetch_balance_lambda_trigger" {
  bucket = aws_s3_bucket.botbro_balance_data.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.binance_balance_lambda.arn
    events              = ["s3:ObjectCreated:Put"]
  }

  depends_on = [aws_lambda_permission.botbro_fetch_balance_s3_trigger]
}
