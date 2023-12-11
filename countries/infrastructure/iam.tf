resource "aws_iam_role" "dax_role" {
  name = "dax-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "dax.amazonaws.com"
        }
      },
    ]
  })

  inline_policy {
    name = "dynamodb_access"

    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action   = ["dynamodb:*"]
          Effect   = "Allow"
          Resource = [
            aws_dynamodb_table.countries.arn,
            aws_dynamodb_table.status.arn,
            aws_dynamodb_table.circuit_breaker_state.arn
          ]
        },
      ]
    })
  }
}

resource "aws_iam_role" "chalice_lambda_role" {
  name = "chalice-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
  ]

  inline_policy {
          name   = "countries-dev-api_handler"
          policy = jsonencode(
                {
                  Statement = [
                      {
                          Action   = [
                              "dynamodb:BatchGetItem",
                              "dynamodb:BatchWriteItem",
                              "dynamodb:PutItem",
                              "dynamodb:DeleteItem",
                              "dynamodb:Scan",
                              "dynamodb:Query",
                              "dynamodb:UpdateItem",
                              "dynamodb:GetItem",
                            ]
                          Effect   = "Allow"
                          Resource = [
                              aws_dynamodb_table.countries.arn,
                              aws_dynamodb_table.status.arn,
                              aws_dynamodb_table.circuit_breaker_state.arn,
                            ]
                        },
                      {
                          Action   = [
                              "dax:BatchGetItem",
                              "dax:BatchWriteItem",
                              "dax:PutItem",
                              "dax:DeleteItem",
                              "dax:Scan",
                              "dax:Query",
                              "dax:UpdateItem",
                              "dax:GetItem",
                            ]
                          Effect   = "Allow"
                          Resource = [
                              aws_dax_cluster.dax.arn,
                            ]
                        },
                      {
                          Action   = [
                              "sqs:GetQueueUrl",
                              "sqs:GetQueueAttributes",
                              "sqs:ReceiveMessage",
                              "sqs:SendMessage",
                              "sqs:DeleteMessage",
                            ]
                          Effect   = "Allow"
                          Resource = [
                              aws_sqs_queue.fetch_requests.arn,
                            ]
                        },
                      {
                          Action   = [
                              "logs:CreateLogStream",
                              "logs:CreateLogGroup",
                              "logs:PutLogEvents",
                            ]
                          Effect   = "Allow"
                          Resource = [
                              "arn:*:logs:*:*:*",
                            ]
                        },
                      {
                          Action   = [
                              "logs:CreateLogGroup",
                              "logs:CreateLogStream",
                              "logs:PutLogEvents",
                              "ec2:CreateNetworkInterface",
                              "ec2:DescribeNetworkInterfaces",
                              "ec2:DeleteNetworkInterface",
                              "ec2:AssignPrivateIpAddresses",
                              "ec2:UnassignPrivateIpAddresses",
                            ]
                          Effect   = "Allow"
                          Resource = "*"
                        },
                    ]
                  Version   = "2012-10-17"
                }
            )
        }
}