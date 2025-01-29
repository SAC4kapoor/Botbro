resource "aws_lambda_function" "market_data" {
  function_name = "MarketDataFunction"
  role          = aws_iam_role.market_data_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.13" # Updated runtime to Python 3.13
  s3_bucket     = "bot-bro-bucket"
  s3_key        = "lambda-function/market/lambda.zip"
  layers        = ["arn:aws:lambda:ap-south-1:336392948345:layer:AWSSDKPandas-Python313:1"] # Add the layer ARN

  timeout = 30 # Set timeout to 30 seconds

  vpc_config {
    subnet_ids         = [aws_subnet.private_subnet.id]
    security_group_ids = [aws_security_group.lambda_sg.id]
  }

  

  depends_on = [
    aws_iam_role.market_data_role
  ]
}

resource "aws_lambda_permission" "botbro_market_data_s3_trigger" {
  statement_id  = "Market-Data-AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.market_data.function_name
  principal     = "s3.amazonaws.com"

  source_arn = aws_s3_bucket.botbro_data.arn
}
