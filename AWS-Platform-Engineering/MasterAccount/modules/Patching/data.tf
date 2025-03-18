# Resource Sync Bucket policy 
data "aws_iam_policy_document" "data_resource_sync_bucket_policy" {
  statement {
    sid = "SSMBucketPermissionsCheck"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ssm.amazonaws.com"]
    }

    actions = [
      "s3:GetBucketAcl",
    ]

    resources = [
      aws_s3_bucket.resource_sync_bucket.arn,
    ]
  }

  statement {
    sid = "SSMBucketDelivery"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ssm.amazonaws.com"]
    }

    actions = [
      "s3:PutObject",
    ]

    resources = [
      "${aws_s3_bucket.resource_sync_bucket.arn}/*",
    ]

    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-server-side-encryption"

      values = [
        "aws:kms",
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-server-side-encryption-aws-kms-key-id"

      values = [
        aws_kms_key.patching_managed_instance_encryption_key.arn,
      ]
    }
  }

  statement {
    sid = "SSMWrite"
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = [
      "s3:PutObject",
    ]

    resources = [
      "${aws_s3_bucket.resource_sync_bucket.arn}/*",
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
    sid = "SSMBucketDeliveryTagging"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ssm.amazonaws.com"]
    }

    actions = [
      "s3:PutObjectTagging",
    ]

    resources = [
      "arn:aws:s3:::${aws_s3_bucket.resource_sync_bucket.bucket}/*/accountid=*/*",
    ]
  }
}

# Execution Logs Bucket policy 
data "aws_iam_policy_document" "data_execution_logs_bucket_policy" {
  statement {
    sid = "SSMWrite"
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = [
      "s3:PutObject","s3:PutObjectAcl"
    ]

    resources = [
      "${aws_s3_bucket.execution_logs_bucket.arn}/*",
    ]

    condition {
      test     = "StringEquals"
      variable = "aws:PrincipalOrgID"

      values = [
        var.org_id,
      ]
    }
  }
}

# zip file for emergency patching lambda
data "archive_file" "emergency_patching_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_emergency_patching.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_emergency_patching.zip"
}

# Patch Baseline Override Bucket policy 
data "aws_iam_policy_document" "data_patch_baseline_override_bucket_policy" {
  statement {
    sid = "OrgRead"
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = [
      "s3:GetObject",
    ]

    resources = [
      "${aws_s3_bucket.patch_baseline_override_bucket.arn}/*",
    ]

    condition {
      test     = "StringEquals"
      variable = "aws:PrincipalOrgID"

      values = [
        var.org_id,
      ]
    }
  }
}

# Glue crawler role policy 
data "aws_iam_policy_document" "ssm_glue_crawler_policy" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject", "s3:PutObject",
    ]

    resources = [
      "${aws_s3_bucket.resource_sync_bucket.arn}/*",
      "${aws_s3_bucket.ec2_inventory_bucket.arn}/*"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "kms:Decrypt",
    ]

    resources = [
      aws_kms_key.ec2_inventory_encryption_key.arn,
      aws_kms_key.patching_managed_instance_encryption_key.arn
    ]
  }
}


# Delete Glue Table Column Function Role policy 
data "aws_iam_policy_document" "ssm_delete_glue_table_column_function_policy" {
  statement {
    effect = "Allow"

    actions = [
      "glue:GetTable", "glue:UpdateTable",
    ]

    resources = [
      "arn:aws:glue:us-east-1:${var.master_account}:catalog",
      "arn:aws:glue:us-east-1:${var.master_account}:database/${aws_glue_catalog_database.ssm_glue_catalog_database.name}",
      "arn:aws:glue:us-east-1:${var.master_account}:table/${aws_glue_catalog_database.ssm_glue_catalog_database.name}/aws_instanceinformation"
    ]
  }
}

# zip file for SSM Delete Glue Table Column lambda
data "archive_file" "ssm_delete_glue_table_column_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/SSM-DeleteGlueTableColumnFunction.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/SSM-DeleteGlueTableColumnFunction.zip"
}


# Master InventoryGlue crawler Role policy 
data "aws_iam_policy_document" "master_inventory_glue_crawler_policy" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject", "s3:PutObject",
    ]

    resources = [
      "${aws_s3_bucket.ec2_inventory_bucket.arn}/*",
    ]
  }
  statement {
    effect = "Allow"

    actions = [
      "kms:Decrypt",
    ]

    resources = [
      aws_kms_key.ec2_inventory_encryption_key.arn,
    ]
  }
}

# zip file for Patching report lambda
data "archive_file" "patching_report_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_patch_report_monthly.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_patch_report_monthly.zip"
}

# Patching report Bucket policy 
data "aws_iam_policy_document" "data_patching_report_bucket_policy" {
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
      "${aws_s3_bucket.patching_report_bucket.arn}/*",
       aws_s3_bucket.patching_report_bucket.arn
    ]

    condition {
      test     = "StringNotLike"
      variable = "aws:PrincipalArn"

      values = [
        "arn:aws:iam::${var.master_account}:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_platform_Operator*",
        var.role_arn
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
      "s3:PutBucketPolicy",
      "s3:DeleteObject",
      "s3:DeleteBucketPolicy",
      "s3:DeleteBucket",
      "s3:PutBucketVersioning",
      "s3:PutEncryptionConfiguration"
    ]

    resources = [
      "${aws_s3_bucket.patching_report_bucket.arn}/*",
       aws_s3_bucket.patching_report_bucket.arn
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

# KMS Key policy for EC2 Inventory encryption key
data "aws_iam_policy_document" "data_ec2_inventory_encryption_key_policy" {
  policy_id = "AccountPolicy"
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
    sid = "Allow use of the key by Systems Manager"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ssm.amazonaws.com"]
    }

    actions = [
      "kms:DescribeKey", "kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey", "kms:GenerateDataKeyWithoutPlaintext",
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
      "kms:Encrypt", "kms:GenerateDataKey",
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
}

# zip file for EC2 Inventory Secondary lambda
data "archive_file" "ec2_inventory_secondary_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_ec2_inventory_secondary.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_ec2_inventory_secondary.zip"
}

# zip file for EC2 Inventory Main lambda
data "archive_file" "ec2_inventory_main_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_ec2_inventory_main.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_ec2_inventory_main.zip"
}

# template file for Master Inventory Report Statemachine
data "template_file" "master_inventory_state_machine_template" {
  template = "${file("${path.module}/StateMachine/MasterInventoryReportStepFunction.json.tpl")}"

  vars = {
    main_lambda_arn = aws_lambda_function.ec2_inventory_main_lambda.arn
    secondary_lambda_arn = aws_lambda_function.ec2_inventory_secondary_lambda.arn
  }
}

# zip file for Account details lambda
data "archive_file" "account_details_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_accounts_details.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_accounts_details.zip"
}


# Account details Glue crawler role policy 
data "aws_iam_policy_document" "account_details_glue_crawler_policy" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject", "s3:PutObject",
    ]

    resources = [
      "${aws_s3_bucket.account_details_bucket.arn}/*",
    ]
  }
  statement {
    effect = "Allow"

    actions = [
      "kms:Decrypt",
    ]

    resources = [
      aws_kms_key.ec2_inventory_encryption_key.arn
    ]
  }
}


# Zip file for Maintenace Window Deletion Secondary lambda
data "archive_file" "maintenance_window_deletion_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_delete_maintenance_windows.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_delete_maintenance_windows.zip"
}

# template file for Maintenace Window Deletion  Statemachine
data "template_file" "maintenance_window_deletion_state_machine_template" {
  template = "${file("${path.module}/StateMachine/MasterInventoryReportStepFunction.json.tpl")}"

  vars = {
    main_lambda_arn = aws_lambda_function.ec2_inventory_main_lambda.arn
    secondary_lambda_arn = aws_lambda_function.maintenance_window_deletion_lambda.arn
  }
}

# Zip file for Report Patch Compliance lambda
data "archive_file" "report_patch_compliance_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_report_patch_compliance_monthly.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_report_patch_compliance_monthly.zip"
}

data "archive_file" "falcon_installation_compliance_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_falcon_installation_compliance.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_falcon_installation_compliance.zip"
}

data "archive_file" "sqs_to_dynamodb_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_patch_sqs_to_dynamo.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_patch_sqs_to_dynamo.zip"
}

data "archive_file" "dynamo_report_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_patch_dynamo_report.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_patch_dynamo_report.zip"
}

data "aws_iam_policy_document" "patching_metadata_iam_policy" {
  statement {
    sid    = "Allow access from child accounts"
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.patching_metadata.arn]

    condition {
      test     = "StringEquals"
      variable = "aws:PrincipalOrgID"
      values   = [var.org_id]
    }
  }
}
