terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

locals {
  aws_cred = jsondecode(file("credentials.json"))
}

# Configure the AWS Provider
provider "aws" {
  region = var.elbv2_region
  access_key = local.aws_cred.aws_access_id
  secret_key = local.aws_cred.aws_secret_key
}