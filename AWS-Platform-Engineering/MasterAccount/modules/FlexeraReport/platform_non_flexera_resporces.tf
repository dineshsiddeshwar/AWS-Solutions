resource "aws_s3_bucket" "platform_non_flexera_report" {
  bucket = "platform-non-flexera-report-us-east-1-${var.master_account}"
  object_lock_enabled = true
    tags = {
      "platform_donotdelete" = "yes"
    }
}

resource "aws_s3_bucket_public_access_block" "non_flexera_report_bucket_block_public_access" {
  bucket = aws_s3_bucket.platform_non_flexera_report.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


resource "aws_s3_bucket_ownership_controls" "non_flexera_reporting_bucket_ownership_controls" {
  bucket = aws_s3_bucket.platform_non_flexera_report.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

#Inventory data S3 bucket policy
resource "aws_s3_bucket_policy" "non_flexera_reporting_bucket_policy" {
  bucket = aws_s3_bucket.platform_non_flexera_report.id
  policy = data.aws_iam_policy_document.cloud_trail_reporting_bucket_policy_flexera.json
}

resource "aws_lambda_function" "platform_non_flexera_report" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_non_flexera_report.zip"
  function_name = "platform_non_flexera_report"
  role          = var.master_admin_role_arn
  handler       = "platform_non_flexera_report.lambda_handler"
  source_code_hash = data.archive_file.non_flexera_role_report_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 128
  timeout = 900

  environment {
    variables = {
      bucket_name	 = aws_s3_bucket.platform_non_flexera_report.bucket
      athena_query = "SELECT account_id, account_name, aws_region, instance_id, instance_state, flexera_status, year, month, date FROM flexera_compliance_dashboard WHERE instance_state = 'running' AND flexera_status = 'Non-Flexera-Instance' AND instance_id IS NOT NULL AND ((CAST(year AS INT) = YEAR(CURRENT_DATE) AND CAST(month AS INT) = MONTH(CURRENT_DATE) - 1) OR (CAST(year AS INT) = YEAR(CURRENT_DATE) - 1 AND CAST(month AS INT) = 12))" 
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_cloudwatch_event_rule" "lambda_schedule_non_flexera" {
  name                = "platform_lambda_schedule_non_flexera"
  schedule_expression = "cron(0 3 1 * ? *)"  # This schedle to run this at 3 AM on the first day of every month

  tags = {
    Name = "lambda_schedule"
  }
}
resource "aws_cloudwatch_event_target" "lambda_target_non_flexera" {
  rule      = aws_cloudwatch_event_rule.lambda_schedule_non_flexera.name
  target_id = "IdEventRule"
  arn = aws_lambda_function.platform_non_flexera_report.arn
}

resource "aws_lambda_permission" "backup_failed_jobs_report_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.platform_non_flexera_report.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_schedule_non_flexera.arn
}