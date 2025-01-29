resource "aws_lambda_function" "binance_balance_lambda" {
  function_name = var.lambda_function_name
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11" # Updated runtime to Python 3.11
  filename      = "${path.module}/lambda/fetch_balance/fetch_balance.zip"

  timeout = 30 # Set timeout to 30 seconds
  role          = aws_iam_role.lambda_fetch_balance_role.arn
  vpc_config {
    subnet_ids         = [aws_subnet.private_subnet.id]
    security_group_ids = [aws_security_group.lambda_sg.id]
  }
  environment {
    variables = {
      SECRETS_MANAGER_NAME = var.secrets_manager_name
    }
  }
  
}

resource "aws_lambda_permission" "botbro_fetch_balance_s3_trigger" {
  statement_id  = "AllowS3InvokeFetchBalance"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.binance_balance_lambda.function_name # Correct function name
  principal     = "s3.amazonaws.com"

  source_arn = aws_s3_bucket.botbro_balance_data.arn # Correct S3 bucket ARN
}