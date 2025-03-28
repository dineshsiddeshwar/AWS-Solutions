terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "4.63.0"
    }
  }
}

provider "aws" {
  region = "us-west-2"
  shared_credentials_files = ["/users/DT495QF/.aws/credentials"]
}

resource "aws_s3_bucket" "lb_logs" {
  bucket = "my-tf-test-bucket"
}


resource "aws_lb" "test" {
  name               = "test-lb-tf"
  internal           = false
  load_balancer_type = "application"

  access_logs {
    bucket  = aws_s3_bucket.lb_logs.id
    enabled = true
  }
}