terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "5.4.0"
    }
  }
}

provider "aws" {
  # Configuration options
access_key = "AKIAUZD7U647EJO2DUPO"
secret_key = "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"
region = "us-east-2"

}