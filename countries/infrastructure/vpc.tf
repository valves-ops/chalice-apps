data "aws_availability_zones" "available" {}

resource "aws_vpc" "vpc" {
  cidr_block           = "${var.vpc_cidr_prefix}.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "tf-${var.environment}-default-vpc",
    Description = "Terraform managed VPC"
    Environment = var.environment
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id
  tags   = {
    Name = "tf-${var.environment}-main-gateway"
    Environment = var.environment
  }
}

resource "aws_default_route_table" "internet_route" {
  default_route_table_id = aws_vpc.vpc.default_route_table_id

  # The default route mapping VPC's CIDR block to local is created implicitly

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "tf-${var.environment}-internet-route-table"
    Environment = var.environment
  }
}

resource "aws_subnet" "public_subnet_a" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = "${var.vpc_cidr_prefix}.10.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  tags                    = {
    Name = "${var.environment}-public-subnet-a"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "public_subnet_a_to_internet" {
  subnet_id      = aws_subnet.public_subnet_a.id
  route_table_id = aws_default_route_table.internet_route.id
}

resource "aws_subnet" "public_subnet_b" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = "${var.vpc_cidr_prefix}.11.0/24"
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true
  tags                    = {
    Name = "${var.environment}-public-subnet-b"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "subnet_b_to_internet" {
  subnet_id      = aws_subnet.public_subnet_b.id
  route_table_id = aws_default_route_table.internet_route.id
}

resource "aws_subnet" "public_subnet_c" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = "${var.vpc_cidr_prefix}.12.0/24"
  availability_zone       = data.aws_availability_zones.available.names[2]
  map_public_ip_on_launch = true
  tags                    = {
    Name = "${var.environment}-public-subnet-c"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "public_subnet_c_to_internet" {
  subnet_id      = aws_subnet.public_subnet_c.id
  route_table_id = aws_default_route_table.internet_route.id
}


resource "aws_eip" "nat_eip" {
  vpc        = true
  depends_on = [aws_internet_gateway.igw]

  tags = {
    Name = "tf-${var.environment}-nat-ip"
    Environment = var.environment
  }
}

resource "aws_nat_gateway" "nat_gw" {
  subnet_id     = aws_subnet.public_subnet_a.id
  allocation_id = aws_eip.nat_eip.allocation_id
  depends_on    = [aws_internet_gateway.igw]

  tags = {
    Name = "tf-${var.environment}-nat-gateway"
    Environment = var.environment
  }

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

resource "aws_route_table" "private_subnet_route" {
  vpc_id = aws_vpc.vpc.id

  # The default route mapping VPC's CIDR block to local is created implicitly

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gw.id
  }

  tags = {
    Name = "tf-${var.environment}-nat-route-table"
    Environment = var.environment
  }
}


resource "aws_subnet" "private_subnet_a" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = "${var.vpc_cidr_prefix}.0.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = false
  tags                    = {
    Name = "${var.environment}-private-subnet-a"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "private_subnet_a_routing" {
  subnet_id      = aws_subnet.private_subnet_a.id
  route_table_id = aws_route_table.private_subnet_route.id
}
