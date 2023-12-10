resource "aws_iam_role" "pipeline_role" {
  name        = "pipeline-role"
  description = "Allows CodePipieline to call AWS services on your behalf"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : "sts:AssumeRole",
        "Principal" : {
          "Service" : "codepipeline.amazonaws.com"
        }
      },
    ]
  })

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AWSCodePipeline_FullAccess",
    "arn:aws:iam::aws:policy/AWSCodeBuildAdminAccess"
  ]

  inline_policy {
    name   = "codestar-full-access"
    policy = jsonencode({
      Version   = "2012-10-17"
      Statement = [
        {
          Action = [
            "codestar:*",
            "codestar-connections:*"
          ]
          Effect   = "Allow"
          Resource = [
            "arn:aws:codestar-connections:eu-central-1:806440980696:connection/3f74118e-5b6c-4852-9d72-208842387ea6"
          ]
        },
      ]
    })
  }

  inline_policy {
    name   = "s3-access"
    policy = jsonencode({
      Version   = "2012-10-17"
      Statement = [
        {
          Action = [
            "s3:*",
          ]
          Effect   = "Allow"
          Resource = [
              aws_s3_bucket.codepipeline_artifact_store.arn,
              "${aws_s3_bucket.codepipeline_artifact_store.arn}/*"
            ],
          
        },
      ]
    })
  }

  inline_policy { # maybe turn this into permissions necessary for chalice deploy
    name   = "codedeploy-access"
    policy = jsonencode({
      Version   = "2012-10-17"
      Statement = [
        {
          Action = [
            "codedeploy:*",
          ]
          Effect   = "Allow"
          Resource = "*"
        },
      ]
    })
  }
}

resource "aws_iam_role" "codebuild_role" {
  name        = "build-role"
  description = "Allows CodeBuild to call AWS services on your behalf"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : "sts:AssumeRole",
        "Principal" : {
          "Service" : "codebuild.amazonaws.com"
        }
      },
    ]
  })

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AWSCodeBuildAdminAccess",
    "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess",
    "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
  ]

  inline_policy {
    name   = "cloudwatch-access"
    policy = jsonencode({
      Version   = "2012-10-17"
      Statement = [
        {
          Action = [
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ]
          Effect   = "Allow"
          Resource = [
            aws_cloudwatch_log_group.codebuild.arn,
            "${aws_cloudwatch_log_group.codebuild.arn}:*",
            aws_cloudwatch_log_group.test_job.arn,
            "${aws_cloudwatch_log_group.test_job.arn}:*",
            aws_cloudwatch_log_group.deploy_job.arn,
            "${aws_cloudwatch_log_group.deploy_job.arn}:*",
          ]
        }
      ]
    })
  }

  inline_policy {
    name = "iam-access"
    policy = jsonencode({
      Version   = "2012-10-17"
      Statement = [
        {
          Action = [
            "iam:AttachRolePolicy",
            "iam:DeleteRolePolicy",
            "iam:DetachRolePolicy",
            "iam:CreateRole",
            "iam:PutRolePolicy",
            "iam:GetRole",
            "iam:PassRole"
          ]
          Effect   = "Allow"
          Resource = "*"
        },
      ]
    })
  }

  inline_policy {
    name = "lambda-access"
    policy = jsonencode({
      Version   = "2012-10-17"
      Statement = [
        {
          Action = [
            "lambda:*",
          ]
          Effect   = "Allow"
          Resource = "*" # this can be better scoped
        },
      ]
    })
  }

  inline_policy {
    name = "api-gateway-access"
    policy = jsonencode({
      Version   = "2012-10-17"
      Statement = [
        {
          Action = [
            "apigateway:*",
          ]
          Effect   = "Allow"
          Resource = "*" # this can be better scoped
        },
      ]
    })
  }

  inline_policy {
    name   = "s3-access"
    policy = jsonencode({
      Version   = "2012-10-17"
      Statement = [
        {
          Action = [
            "s3:*",
          ]
          Effect   = "Allow"
          Resource = [
              aws_s3_bucket.codepipeline_artifact_store.arn,
              "${aws_s3_bucket.codepipeline_artifact_store.arn}/*"
            ]
        },
      ]
    })
  }
}