# policy document for kms key
data "aws_iam_policy_document" "data_backup_jobs_data_encryption_key_policy" {
  statement {
    sid = "Enable IAM User Permissions"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${var.master_account}:root"]
    }

    actions = [
      "kms:*",
    ]

    resources = [
      "*",
    ]
  }

  statement {
    sid = "Allow use of the key by Lambda"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = [
      "kms:DescribeKey", 
      "kms:Encrypt", 
      "kms:Decrypt", 
      "kms:ReEncrypt*", 
      "kms:GenerateDataKey", 
      "kms:GenerateDataKeyWithoutPlaintext"
    ]

    resources = [
      "*",
    ]
  }

  statement {
    sid = "Allow use of the key by Glue"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"]
    }

    actions = [
      "kms:DescribeKey", 
      "kms:Encrypt", 
      "kms:Decrypt", 
      "kms:ReEncrypt*", 
      "kms:GenerateDataKey", 
      "kms:GenerateDataKeyWithoutPlaintext"
    ]

    resources = [
      "*",
    ]
  }

  statement {
    sid = "Allow use of the key by service roles within the organization"
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = [
      "kms:Encrypt", 
      "kms:GenerateDataKey"
    ]

    resources = [
      "*",
    ]

    condition {
      test     = "StringEquals"
      variable = "aws:PrincipalOrgID"

      values = [
        var.org_id,
      ]
    }
  }

  statement {
    sid = "Enable Operator Permissions"
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = [
      "kms:Decrypt",
    ]

    resources = [
      "*",
    ]

    condition {
      test     = "StringLike"
      variable = "aws:PrincipalArn"

      values = [
        "arn:aws:iam::${var.master_account}:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_platform_Operator*",
      ]
    }
  }
}


# policy document for glue crawler role
data "aws_iam_policy_document" "backup_jobs_glue_crawler_policy" {
  statement {
    effect = "Allow"

    actions = [
      "kms:Decrypt",
    ]

    resources = [
      aws_kms_key.backup_jobs_data_encryption_key.arn,
    ]
  }
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject", "s3:PutObject",
    ]

    resources = [
      "${aws_s3_bucket.backup_jobs_bucket.arn}/*",
    ]
  }
}


# zip file for backup jobs report lambda
data "archive_file" "backup_jobs_report_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_backups_jobs_report.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_backups_jobs_report.zip"
}

# zip file for failed backup jobs new report lambda
data "archive_file" "platform_failed_backup_jobs_new_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_failed_backup_jobs_new.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_failed_backup_jobs_new.zip"
}

# policy document for failed backup jobs bucket
data "aws_iam_policy_document" "data_falied_backup_jobs_bucket_policy" {
  statement {
    sid = "DenyAllExcept"
    effect = "Deny"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = [
      "s3:*",
    ]

    resources = [
      "${aws_s3_bucket.failed_backup_jobs_bucket.arn}/*",
      "${aws_s3_bucket.failed_backup_jobs_bucket.arn}"
    ]

    condition {
      test     = "StringNotLike"
      variable = "aws:PrincipalArn"

      values = [
        "arn:aws:iam::${var.master_account}:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_platform_Operator*",
        var.role_arn,
        aws_iam_role.backup_jobs_glue_crawler_role.arn,
        "arn:aws:iam::${var.master_account}:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_platform_ContributorExternal*"        
      ]
    }
  }

  statement {
    sid = "DenyAllOperator"
    effect = "Deny"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = [
      "s3:PutObject", 
      "s3:PutObjectRetention", 
      "s3:DeleteObjectVersion", 
      "s3:PutBucketPolicy*", 
      "s3:DeleteObject", 
      "s3:DeleteBucketPolicy",
      "s3:DeleteBucket",
      "s3:PutBucketVersioning",
      "s3:PutEncryptionConfiguration"
    ]

    resources = [
      "${aws_s3_bucket.failed_backup_jobs_bucket.arn}/*",
      "${aws_s3_bucket.failed_backup_jobs_bucket.arn}"
    ]

    condition {
      test     = "StringLike"
      variable = "aws:PrincipalArn"

      values = [
        "arn:aws:iam::${var.master_account}:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_platform_Operator*"
      ]
    }
  }
}

# zip file for failed backup jobs report lambda
data "archive_file" "failed_backup_jobs_report_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_failed_backups_jobs_report.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_failed_backups_jobs_report.zip"
}
