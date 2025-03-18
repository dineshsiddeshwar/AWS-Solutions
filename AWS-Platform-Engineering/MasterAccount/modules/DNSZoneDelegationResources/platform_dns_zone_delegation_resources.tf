# DNS Zone Delegation topic encryption key
resource "aws_kms_key" "dns_zone_delegation_data_encryption_key" {
  description = "AWS KMS Key to encrypt the PEM file"
  is_enabled = true
  enable_key_rotation = true
}

# DNS Zone Delegation topic encryption key policy
resource "aws_kms_key_policy" "dns_zone_delegation_data_encryption_key_policy" {
  key_id = aws_kms_key.dns_zone_delegation_data_encryption_key.id
  policy = jsonencode({
    "Version": "2012-10-17",
    "Id": "key-consolepolicy-3",
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${var.master_account}:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        },
        {
            "Sid": "Enable IAM child account role",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "kms:Decrypt",
            "Resource": "arn:aws:kms:us-east-1:${var.master_account}:key/*",
            "Condition": {
                "StringEquals": {
                    "aws:PrincipalOrgID": var.org_id
                },
                "StringLike": {
                    "aws:PrincipalArn": "arn:aws:iam::*:role/platform*"
                }
            }
        },
        {
            "Sid": "Allow access for Key Administrators",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "kms:Create*",
                "kms:Describe*",
                "kms:Enable*",
                "kms:List*",
                "kms:Put*",
                "kms:Update*",
                "kms:Revoke*",
                "kms:Disable*",
                "kms:Get*",
                "kms:Delete*",
                "kms:TagResource",
                "kms:UntagResource"
            ],
            "Resource": "*",
            "Condition": {
                "StringLike": {
                    "aws:PrincipalArn": "arn:aws:iam::${var.master_account}:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_platform_*"
                }
            }
        }
    ]
})
}

# DNS Zone Delegation topic encryption key alias
resource "aws_kms_alias" "dns_zone_delegation_data_encryption_key_alias" {
  name          = "alias/DNSKey"
  target_key_id = aws_kms_key.dns_zone_delegation_data_encryption_key.key_id
}
