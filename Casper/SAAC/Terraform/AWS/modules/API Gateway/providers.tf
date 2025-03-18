provider "aws" {
  region = var.aws_region
  default_tags {
    # 7. Ensure API Gateway Resources are tagged according to standards
    tags = var.common_tags
  }
}
