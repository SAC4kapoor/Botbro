resource "aws_cloudwatch_event_rule" "trading_bot_schedule" {
  name                = "TradingBotTrigger"
  schedule_expression = "rate(5 minutes)" # Adjust trigger frequency here
}

resource "aws_cloudwatch_event_target" "trading_bot_target" {
  rule      = aws_cloudwatch_event_rule.trading_bot_schedule.name
  target_id = "TradingBot"
  arn       = aws_lambda_function.trading_bot.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.trading_bot.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.trading_bot_schedule.arn
}
