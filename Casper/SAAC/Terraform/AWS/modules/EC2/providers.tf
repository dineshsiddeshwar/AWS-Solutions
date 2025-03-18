locals {
    aws_cred = jsondecode(file("./credentials.json")) 
}
provider "aws" {
  region = var.ec2_region
  access_key = local.aws_cred.aws_access_id  /* put your access id */
  secret_key = local.aws_cred.aws_secret_key /* put your secret key */
}