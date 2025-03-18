provider "aws" {
  region = var.db_deployment_region
  access_key = aws_access_id  /* put your access id */
  secret_key = aws_secret_key /* put your secret key */
}