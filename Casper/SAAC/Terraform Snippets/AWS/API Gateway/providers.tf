provider "aws" {
  region = var.aws_region
  default_tags {
    # Ensure API Gateway Resources are tagged according to Organization standards
    tags = var.common_tags
  }
}
