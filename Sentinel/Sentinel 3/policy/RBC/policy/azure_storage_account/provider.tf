terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "4.61.0"
    }
  }
}

provider "aws" {
  # Configuration options
  shared_credentials_files = ["/Users/DT495QF/.aws/credentials"]
  profile                  = "default"
  region                   = "us-west-2"
}