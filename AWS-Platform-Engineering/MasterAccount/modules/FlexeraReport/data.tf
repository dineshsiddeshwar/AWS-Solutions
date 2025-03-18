data "archive_file" "non_flexera_role_report_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_non_flexera_report.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_non_flexera_report.zip"
}

data "aws_iam_policy_document" "cloud_trail_reporting_bucket_policy_flexera" {
  statement {
    sid = "AWSCloudTrailLake1"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }

    actions = [
      "s3:PutObject*",
      "s3:Abort*"
    ]

    resources = [
      "arn:aws:s3:::platform-non-flexera-report-us-east-1-${var.master_account}/*",
      "arn:aws:s3:::platform-non-flexera-report-us-east-1-${var.master_account}"

    ]
    condition {
        test = "StringLike"
        variable = "aws:sourceArn"
        values = ["arn:aws:cloudtrail:us-east-1:${var.master_account}:eventdatastore/*"]      
    }

    condition {
      test     = "StringLike"
      variable = "aws:sourceAccount"

      values = [ var.master_account ]
    }
  }

  statement {
    sid = "AWSCloudTrailLake2"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }

    actions = [
      "s3:GetBucketAcl",
    ]

    resources = [
      "arn:aws:s3:::platform-non-flexera-report-us-east-1-${var.master_account}"

    ]
    condition {
        test = "StringLike"
        variable = "aws:sourceArn"
        values = ["arn:aws:cloudtrail:us-east-1:${var.master_account}:eventdatastore/*"]      
    }

    condition {
      test     = "StringLike"
      variable = "aws:sourceAccount"

      values = [ var.master_account ]
    }
  }
}