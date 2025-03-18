data "archive_file" "backup_report_trigger_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_backup_monitoring.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_backup_monitoring.zip"
}

data "aws_iam_policy_document" "backup_monitoring_logs_bucket_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${var.master_account}:role/aws-service-role/reports.backup.amazonaws.com/AWSServiceRoleForBackupReports"]
    }

    actions = [
      "s3:*",
    ]

    resources = [
      "arn:aws:s3:::platform-backup-monitoring-logs-us-east-1-${var.master_account}/*",
      "arn:aws:s3:::platform-backup-monitoring-logs-us-east-1-${var.master_account}"
      
    ]
  }
}

