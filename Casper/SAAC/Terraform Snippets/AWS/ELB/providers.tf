provider "aws" {
  region = var.aws_region
  default_tags {
    #  Ensure Application Load Balancing resources are tagged according to Organization standards
    tags = var.alb_common_tags
  }
}
