provider "aws" {

  region = var.aws_region

  default_tags {
    #  Ensure EC2 Resources are tagged according to organization standards
    tags = var.common_tags
  }
}
