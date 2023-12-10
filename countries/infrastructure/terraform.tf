terraform {
  backend "s3" {
    bucket = "vcloud-terraform-state"
    key    = "applications/countries-app"
    region = "sa-east-1"
    dynamodb_table = "terraform-state-lock"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.30.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  profile = "personal"
}