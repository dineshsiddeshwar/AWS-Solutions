resource "aws_kms_key" "l" {
    count = var.default_key_for_SSE ? 0 : 1 // conditional resource creation
    description = "This key is used for AWS SNS Topic"
    key_usage = "ENCRYPT_DECRYPT"
    customer_master_key_spec = "RSA_2048"
}

# Giving the key alias or name for displaying
resource "aws_kms_alias" "l" {
    count = var.default_key_for_SSE ? 0 : 1 // conditional resource creation
    name = "alias/casper_key_for_SNS"
    target_key_id = aws_kms_key.l[count.index].key_id
}

resource "aws_sns_topic" "casper_sns" {
    name = "casper_sns"
    kms_master_key_id = var.default_key_for_SSE ? "/alias/aws/sns" : aws_kms_alias.l[0].target_key_id  // For Server Side Encryption
}

