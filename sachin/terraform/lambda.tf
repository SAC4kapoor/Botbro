resource "aws_lambda_function" "trading_bot" {
  function_name = "TradingBotFunction"
  role          = aws_iam_role.lambda_role.arn
  handler       = "bot.lambda_handler"
  runtime       = "python3.8"
  filename      = "${path.module}/lambda/trading-bot.zip"

  environment {
    variables = {
      DYNAMODB_TABLE       = var.dynamodb_table_name
      SECRETS_MANAGER_NAME = var.secrets_manager_name
    }
  }

  depends_on = [aws_iam_role.lambda_role]
}
