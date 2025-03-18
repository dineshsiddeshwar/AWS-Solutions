resource "aws_s3_bucket" "platform-da2-billing-automation" {
  bucket = "platform-da2-billing-automation-${var.account_id}"

  tags = {
    platform_donotdelete  = "yes"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "platform-da2-billing-automation" {
  bucket = aws_s3_bucket.platform-da2-billing-automation.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}


resource "aws_s3_bucket_public_access_block" "platform-da2-billing-automation" {
  bucket = aws_s3_bucket.platform-da2-billing-automation.id
  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

