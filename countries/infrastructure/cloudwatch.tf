resource "aws_cloudwatch_log_group" "codebuild" {
  name = "codebuild-logs"
  retention_in_days = 365
}

resource "aws_cloudwatch_log_stream" "codebuild" {
  log_group_name = aws_cloudwatch_log_group.codebuild.name
  name           = "build-logs"
}


resource "aws_cloudwatch_log_group" "test_job" {
  name = "test-job-logs"
  retention_in_days = 365
}

resource "aws_cloudwatch_log_stream" "test_job" {
  log_group_name = aws_cloudwatch_log_group.test_job.name
  name           = "test-job-logs"
}


resource "aws_cloudwatch_log_group" "deploy_job" {
  name = "deploy-job-logs"
  retention_in_days = 365
}

resource "aws_cloudwatch_log_stream" "deploy_job" {
  log_group_name = aws_cloudwatch_log_group.deploy_job.name
  name           = "deploy-job-logs"
}