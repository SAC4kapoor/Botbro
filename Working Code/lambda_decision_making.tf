resource "aws_lambda_function" "decision_making" {
  function_name = "DecisionMakingFunction"
  role          = aws_iam_role.lambda_decision_making_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.13" # Updated runtime to Python 3.13
  s3_bucket     = "bot-bro-bucket"
  s3_key        = "lambda-function/decision/lambda.zip"
  layers        = ["arn:aws:lambda:ap-south-1:336392948345:layer:AWSSDKPandas-Python313:1"] # Add the layer ARN

  timeout = 30 # Set timeout to 30 seconds

  vpc_config {
    subnet_ids         = [aws_subnet.private_subnet.id]
    security_group_ids = [aws_security_group.lambda_sg.id]
  }

  # Add environment variables here
  environment {
    variables = {
      SENTIMENT_API_URL         = "https://api.sentimentapi.com/v1/crypto"
      MAX_PORTFOLIO_ALLOCATION  = "0.2" # 20% of total portfolio
      MIN_SENTIMENT_SCORE       = "0.5" # Minimum sentiment score to take action
    }
  }

  depends_on = [
    aws_iam_role.lambda_decision_making_role
  ]
}

# Grant Market Data Lambda permission to invoke Decision-Making Lambda
resource "aws_lambda_permission" "market_data_invoke_permission" {
  statement_id  = "AllowMarketDataInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.decision_making.function_name
  principal     = "lambda.amazonaws.com"
  source_arn    = aws_lambda_function.market_data.arn
}

resource "aws_lambda_permission" "botbro_decision_s3_trigger" {
  statement_id  = "Decision-Making-alowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.decision_making.function_name
  principal     = "s3.amazonaws.com"

  source_arn = aws_s3_bucket.decision_making_bucket.arn
}
