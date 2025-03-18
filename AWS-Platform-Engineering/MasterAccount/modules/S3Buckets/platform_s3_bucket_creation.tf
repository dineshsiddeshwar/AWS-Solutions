# Agent installation bucket
resource "aws_s3_bucket" "agent_installation_bucket" {
  bucket = "platform-da2-installation-packages-${var.env_type}"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_s3_bucket_public_access_block" "agent_installation_bucket_block_public_access" {
  bucket = aws_s3_bucket.agent_installation_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "agent_installation_bucket_policy" {
  bucket = aws_s3_bucket.agent_installation_bucket.id
  policy = file("${path.module}/BucketPolicy/agent_bucket_policy_${var.env_type}.json")
}

# Account update bucket
resource "aws_s3_bucket" "account_update_bucket" {
  bucket = "platform-account-update-automation-bucket-${var.env_type}"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_s3_bucket_public_access_block" "account_update_bucket_block_public_access" {
  bucket = aws_s3_bucket.account_update_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ATL Terraform Backend Bucket bucket
resource "aws_s3_bucket" "atl_terraform_backend_bucket" {
  bucket = "github-tf-state-bucket-${var.env_type}"
  tags = {
    "platform_donotdelete" = "yes",
     Name = "ATLS3TFbackend"

  }
}

resource "aws_s3_bucket_public_access_block" "atl_terraform_backend_bucket_block_public_access" {
  bucket = aws_s3_bucket.atl_terraform_backend_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "atl_terraform_backend_bucket_policy" {
  bucket = aws_s3_bucket.atl_terraform_backend_bucket.id
  policy = data.aws_iam_policy_document.data_atl_terraform_backend_bucket_policy.json
}

resource "aws_s3_bucket_versioning" "atl_terraform_backend_bucket_versioning" {
  bucket = aws_s3_bucket.atl_terraform_backend_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "atl_terraform_backend_bucket_encryption" {
  bucket = aws_s3_bucket.atl_terraform_backend_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }   
  }
}

