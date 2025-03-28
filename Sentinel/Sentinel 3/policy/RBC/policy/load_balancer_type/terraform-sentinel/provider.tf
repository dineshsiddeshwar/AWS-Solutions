terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = ">=4.6.0"
    }
  }
}

provider "aws" {
  shared_credentials_files = ["/Users/DT495QF/.aws/credentials"]
  region                   = "us-east-1"
}