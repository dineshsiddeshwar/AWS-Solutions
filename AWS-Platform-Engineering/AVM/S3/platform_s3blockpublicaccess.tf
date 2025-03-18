resource "aws_s3_account_public_access_block" "platform_security_s3_block_public" {
  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls  = true
  restrict_public_buckets = true
  account_id = var.account_id
}