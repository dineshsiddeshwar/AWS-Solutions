provider "aws" {
  region = var.aws_region
  default_tags { 
    tags = var.ses_common_tags   #  Ensure SES Resources are tagged according to organization standards
  
  }
}
