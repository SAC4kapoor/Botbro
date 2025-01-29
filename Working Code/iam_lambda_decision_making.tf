resource "aws_iam_role" "lambda_decision_making_role" {
  name = "DecisionMakingLambdaRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_decision_making_policy" {
  name = "Decision-making-LambdaPolicy"

  role = aws_iam_role.lambda_decision_making_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:DescribeTable",
          "dynamodb:*",
          "dynamodb:CreateTable"
        ],
        Resource = "*"
      },
      {
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface"
        ]
        Effect = "Allow"
        Resource = "*"
      },
      {
        Effect   = "Allow",
        Action   = [
          "secretsmanager:GetSecretValue"
        ],
        Resource = "*"
      },
      {
        Effect   = "Allow",
        Action   = "logs:*",
        Resource = "*"
      }
    ]
  })
}
