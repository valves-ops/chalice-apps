resource "aws_dynamodb_table" "countries" {
    name                        = "countries-${var.environment}"
    deletion_protection_enabled = true

    billing_mode                = "PROVISIONED"
    read_capacity               = 10
    write_capacity              = 10

    hash_key                    = "cca2"

    attribute {
        name = "cca2"
        type = "S"
    }
}

resource "aws_dynamodb_table" "status" {
    name                        = "status-${var.environment}"
    deletion_protection_enabled = false

    billing_mode                = "PROVISIONED"
    read_capacity               = 10
    write_capacity              = 10

    hash_key                    = "fetched_country"
    range_key                   = "timestamp"

    attribute {
        name = "fetched_country"
        type = "S"
    }

    attribute {
        name = "timestamp"
        type = "S"
    }
}

resource "aws_dynamodb_table" "circuit_breaker_state" {
    name                        = "circuit-breaker-state-${var.environment}"
    deletion_protection_enabled = false

    billing_mode                = "PROVISIONED"
    read_capacity               = 10
    write_capacity              = 10

    hash_key                    = "service_name"

    attribute {
        name = "service_name"
        type = "S"
    }
}

resource "aws_dax_cluster" "dax" {
  cluster_name       = "dax-${var.environment}"
  iam_role_arn       = aws_iam_role.dax_role.arn
  node_type          = "dax.t3.small"
  subnet_group_name  = aws_dax_subnet_group.dax.name
  replication_factor = 1
  security_group_ids = [aws_vpc.vpc.default_security_group_id]
}

resource "aws_dax_subnet_group" "dax" {
  name       = "dax-subnet-group-${var.environment}"
  subnet_ids = [
    aws_subnet.public_subnet_a.id, 
    aws_subnet.public_subnet_b.id,
    aws_subnet.public_subnet_c.id
  ]
}