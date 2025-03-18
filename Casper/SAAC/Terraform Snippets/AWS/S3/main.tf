# Policies
# 1.  Ensure AWS S3 buckets are not granting FULL_CONTROL access to authenticated users (least privilege access)

# 9.  S3 buckets should have a Resource Based Policy to allow access to CG IPs Only

resource "aws_s3_bucket" "s3_bucket" {
  bucket = var.s3_bucket_name

  # 6. Ensure Secure transfer is enabled on S3 bucket
  # attach_deny_insecure_transport_policy = true

  # 10. Ensure that AWS S3 buckets use Object Lock for data protection
  object_lock_enabled = true
}

resource "aws_s3_bucket_object_lock_configuration" "s3_bucket_object_lock_configuration" {
  bucket = aws_s3_bucket.s3_bucket.bucket
  rule {
    default_retention {
      mode = var.s3_bucket_object_lock_config_retention_mode
      days = var.s3_bucket_object_lock_config_retention_period
    }
  }
}

# 2. Ensure AWS S3 buckets are not publicly accessible via bucket policies (least privilege access)
# 7. Ensure 'Block public access' setting is turned on
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block

resource "aws_s3_bucket_public_access_block" "s3_bucket_block_public_access" { # S3 Bucket to which this Public Access Block configuration should be applied
  bucket = aws_s3_bucket.s3_bucket.id

  block_public_acls       = true # <------- Whether Amazon S3 should block public ACLs for this bucket. Defaults to false. Enabling this setting does not affect existing policies or ACLs. When set to true.
  block_public_policy     = true # <------- Whether Amazon S3 should block public bucket policies for this bucket. Defaults to false. Enabling this setting does not affect the existing bucket policy. When set to true.
  restrict_public_buckets = true # <------- Whether Amazon S3 should restrict public bucket policies for this bucket. Defaults to false. Enabling this setting does not affect the previously stored bucket policy, except that public and cross-account access within the public bucket policy, including non-public delegation to specific accounts, is blocked.
  ignore_public_acls      = true # <------- Whether Amazon S3 should ignore public ACLs for this bucket. Defaults to false. Enabling this setting does not affect the persistence of any existing ACLs and doesn't prevent new public ACLs from being set.

}


resource "aws_s3_bucket_server_side_encryption_configuration" "s3_bucket_sse" {
  bucket = aws_s3_bucket.s3_bucket.bucket

  rule {
    apply_server_side_encryption_by_default {
      # https://registry.terraform.io/providers/hashicorp/aws%20%20/latest/docs/resources/s3_bucket_server_side_encryption_configuration
      # 5. Ensure S3 Buckets are encrypted at rest using organization managed key(CMK)
      kms_master_key_id = var.s3_sse_key
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_versioning" "s3_bucket_versioning" {
  bucket = aws_s3_bucket.s3_bucket.id
  versioning_configuration {
    status = "Enabled"


    # 4. Todo: Ensure MFA Delete feature is enabled on S3 Bucket.
    # 3. Todo: Ensure MFA is enabled for sensitive S3 resources
    # Accomplishing MFA requires a number of services to be enabled,
    # and varies greatly with implementation. This snippet shows
    # the resource required, but we do not actually implement MFA
    # mfa_delete="Enabled"
  }
}

# 8.  Ensure S3 is communicating with services inside VPC via VPC end-point #
resource "aws_vpc_endpoint" "s3_vpc_endpoint" {
  vpc_id              = var.s3_vpc_id
  service_name        = "com.amazonaws.${var.s3_region}.s3"
  vpc_endpoint_type   = var.s3_vpc_endpoint_type
  security_group_ids  = var.s3_vpc_sgs
  private_dns_enabled = true
}
