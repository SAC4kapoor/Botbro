resource "aws_cloudwatch_event_rule" "trading_bot_schedule" {
  name                = "MarketDataTrigger"
  schedule_expression = "cron(0/30 * * * ? *)"  # Trigger every 30 minutes
}

resource "aws_cloudwatch_event_target" "trading_bot_target" {
  rule      = aws_cloudwatch_event_rule.trading_bot_schedule.name
  target_id = "MarketDatalambda"
  arn       = aws_lambda_function.market_data.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.market_data.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.trading_bot_schedule.arn
}
