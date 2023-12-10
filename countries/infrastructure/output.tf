output "dax_endpoint" {
  value = aws_dax_cluster.dax.cluster_address
}

output "sqs_vpc_endpoint" {
    value = aws_vpc_endpoint.sqs_endpoint.dns_entry
}

output "public_subnet_a" {
    value = aws_subnet.public_subnet_a.id
}

output "public_subnet_b" {
    value = aws_subnet.public_subnet_b.id
}

output "public_subnet_c" {
    value = aws_subnet.public_subnet_c.id
}

output "vpc_security_group_id" {
    value = aws_vpc.vpc.default_security_group_id
}

output "private_subnet_a" {
    value = aws_subnet.private_subnet_a.id
}
