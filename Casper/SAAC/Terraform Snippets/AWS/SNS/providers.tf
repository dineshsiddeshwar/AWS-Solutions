provider "aws" {
  region = var.aws_region
  
  default_tags {
    # Ensure SNS resources are tagged according to organization standards
    tags = var.common_tags
  }
}
