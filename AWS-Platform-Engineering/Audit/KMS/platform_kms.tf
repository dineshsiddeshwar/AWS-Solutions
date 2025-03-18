resource "aws_kms_key" "sharr_key" {
    enable_key_rotation = true
  
}

resource "aws_kms_key_policy" "sharr_key" {
    key_id = aws_kms_key.sharr_key.id
    policy = templatefile("${path.module}/policy.json",{ account_id = var.account_id })
}

resource "aws_kms_alias" "sharr_key" {
  name          = "alias/SO0111-SHARR-Key"
  target_key_id = aws_kms_key.sharr_key.key_id
}