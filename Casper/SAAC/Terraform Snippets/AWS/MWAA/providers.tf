provider "aws" {
  region = var.aws_region # string
   default_tags {
    #  Ensure resources are tagged according to Organization standards
    tags = var.common_tags
  }
}
