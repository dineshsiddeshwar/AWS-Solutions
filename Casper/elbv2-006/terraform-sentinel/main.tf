terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "5.12.0"
    }
  }
}

provider "aws" {
  # Configuration options
  }

resource "aws_lb_target_group" "ip-type-target" {
  name        = "tf-elbv2-target-group"
  target_type = "ip"
}