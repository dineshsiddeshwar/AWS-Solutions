provider "aws" {
  region = var.aws_region
  default_tags {
    tags = var.dynamodb_common_tags
  }
}
