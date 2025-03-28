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
  access_key = "AKIA4BKZHZZI2LKQ5VK3"
  secret_key = "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"
  region     = "us-west-2"
}