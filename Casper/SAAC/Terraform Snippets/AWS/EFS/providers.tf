provider "aws" {
  region = var.aws_region
  default_tags {
    # Ensure EFS resources are tagged according to organization standards
    tags = var.efs_common_tags
  }
}
