data "archive_file" "cfn_stackset_glue_crawler_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_cfn_ss_glue_crawler.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_cfn_ss_glue_crawler.zip"
}

data "aws_iam_policy_document" "cfn_stackset_inventory_bucket_policy" {
  statement {
    sid = "DenyUnencryptedConnections"
    effect = "Deny"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = [
      "s3:*",
    ]

    resources = [
      "arn:aws:s3:::platform-cfn-stackset-inventory-us-east-1-${var.master_account}/*",
      "arn:aws:s3:::platform-cfn-stackset-inventory-us-east-1-${var.master_account}"
      
    ]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"

      values = [
        false
      ]
    }
  }
}

data "archive_file" "cfn_stackset_monitoring_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_cfn_ss_monitoring.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_cfn_ss_monitoring.zip"
}
