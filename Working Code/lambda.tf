resource "aws_lambda_function" "trading_bot" {
  function_name = "TradingBotFunction"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11" # Updated runtime to Python 3.11
  filename      = "${path.module}/lambda/lambda.zip"

  timeout = 10 # Increased timeout to handle longer executions

  environment {
    variables = {
      DYNAMODB_TABLE       = var.dynamodb_table_name
      SECRETS_MANAGER_NAME = aws_secretsmanager_secret.binance_api_keys.name
    }
  }

  depends_on = [
     aws_iam_role.lambda_role
  ]
}

resource "aws_lambda_permission" "botbro_s3_trigger" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.trading_bot.function_name
  principal     = "s3.amazonaws.com"

  source_arn = aws_s3_bucket.botbro_data.arn
}

