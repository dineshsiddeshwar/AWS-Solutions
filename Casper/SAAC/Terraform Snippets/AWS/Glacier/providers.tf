provider "aws" {
  region = var.aws_region

   default_tags {
    tags = var.common_tags #  Ensure Amazon S3 Glacier uses standard organizational resource tagging method
  }
}
