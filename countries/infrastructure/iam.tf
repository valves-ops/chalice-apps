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
