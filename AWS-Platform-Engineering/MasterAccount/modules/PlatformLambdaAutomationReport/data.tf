data "archive_file" "platform_lambda_automation_report_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_lambda_automation_report.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_lambda_automation_report.zip"
}

data "archive_file" "platform_lambda_automation_alert_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_lambda_automation_alert.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_lambda_automation_alert.zip"
}

data "aws_iam_policy_document" "platform_automation_reporting_bucket_policy" {
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
      "arn:aws:s3:::platform-automation-report-bucket-us-east-1-${var.master_account}/*",
      "arn:aws:s3:::platform-automation-report-bucket-us-east-1-${var.master_account}"
      
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
      "arn:aws:s3:::platform-automation-report-bucket-us-east-1-${var.master_account}"
      
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
