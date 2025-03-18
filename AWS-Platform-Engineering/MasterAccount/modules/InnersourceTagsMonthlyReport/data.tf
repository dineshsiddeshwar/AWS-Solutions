data "archive_file" "monthly_innersource_report_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_monthly_innersource_report.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_monthly_innersource_report.zip"
}

data "aws_iam_policy_document" "monthly_innersource_report_bucket_policy" {
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
      "arn:aws:s3:::platform-innersource-tags-monthly-report-${var.master_account}/*",
      "arn:aws:s3:::platform-innersource-tags-monthly-report-${var.master_account}"
      
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
      "arn:aws:s3:::platform-innersource-tags-monthly-report-${var.master_account}"
      
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
