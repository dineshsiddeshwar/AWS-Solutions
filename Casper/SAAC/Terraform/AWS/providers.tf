provider "aws" {
  region = var.aws_region
  default_tags {
    # 8. Ensure EFS resources are tagged according to CG standards
    tags = var.common_tags
  }
}
