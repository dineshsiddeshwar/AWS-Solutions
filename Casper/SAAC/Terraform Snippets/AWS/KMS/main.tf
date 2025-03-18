resource "aws_kms_key" "s3_kms_key" {
  description             = "KMS key used to encrypt s3"
  deletion_window_in_days = var.kms_deletion_window_in_days
}

resource "aws_kms_alias" "s3_encryption_key" {
  name          = "alias/my-key"
  target_key_id = aws_kms_key.s3_kms_key.key_id
}
