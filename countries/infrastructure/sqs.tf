resource "aws_sqs_queue" "fetch_requests" {
  name                      = "fetch-requests-${var.environment}"
  delay_seconds             = 0
#   max_message_size          = 262144
  message_retention_seconds = 24*60*60  # 1 day
  receive_wait_time_seconds = 0
  visibility_timeout_seconds = 5*60   # 5 min
  sqs_managed_sse_enabled = true
}

resource "aws_sqs_queue" "fetch_requests_dlq" {
  name = "fetch-requests-dlq-${var.environment}"
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.fetch_requests.arn]
  })
}

resource "aws_sqs_queue_redrive_policy" "fetch_requests" {
  queue_url = aws_sqs_queue.fetch_requests.id
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.fetch_requests_dlq.arn
    maxReceiveCount     = 4
  })
}


resource "aws_vpc_endpoint" "sqs_endpoint" {
  vpc_id            = aws_vpc.vpc.id
  service_name      = "com.amazonaws.${var.aws_region}.sqs"
  vpc_endpoint_type = "Interface"

  private_dns_enabled = true

  tags = {
    Name = "${var.environment}-sqs-endpoint"
    Environment = var.environment
  }
}

resource "aws_vpc_endpoint_subnet_association" "sqs_endpoint_subnet_a" {
  subnet_id       = aws_subnet.public_subnet_a.id
  vpc_endpoint_id = aws_vpc_endpoint.sqs_endpoint.id
}

resource "aws_vpc_endpoint_subnet_association" "sqs_endpoint_subnet_b" {
  subnet_id       = aws_subnet.public_subnet_b.id
  vpc_endpoint_id = aws_vpc_endpoint.sqs_endpoint.id
}

resource "aws_vpc_endpoint_subnet_association" "sqs_endpoint_subnet_c" {
  subnet_id       = aws_subnet.public_subnet_c.id
  vpc_endpoint_id = aws_vpc_endpoint.sqs_endpoint.id
}