#Platform Non Pim Role Report
resource "aws_lambda_function" "non_pim_role_report_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_non_pim_roles_report.zip"
  function_name = "platform_non_pim_roles_report"
  role          = var.master_admin_role_arn
  handler       = "platform_non_pim_roles_report.lambda_handler"
  source_code_hash = data.archive_file.non_pim_role_report_lambda_zip.output_base64sha256

  runtime = "python3.8"
  timeout = 900
  memory_size = 2176

  environment {
    variables = {
      BUCKET = "platform-cloudtrail-report-bucket-us-east-1-${var.master_account}"
      AUDIT_ACCOUNT_ID = var.audit_account
      SHARED_ACCOUNT_ID = var.shared_services_account_id
      LOGGING_ACCOUNT_ID = var.logging_account
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# RootActivity CloudWatch Event Lambda Rule Trigger
resource "aws_cloudwatch_event_rule" "non_pim_role_report_lambda_rule" {
  description = "Scheduled Rule for once a month"
  name = "platform_non_pim_role_lambda_trigger"
  schedule_expression = "cron(0 10 1 * ? *)"
  is_enabled = true
}

# RootActivity CloudWatch Event Lambda Rule Target
resource "aws_cloudwatch_event_target" "non_pim_role_report_lambda_rule_target" {
  rule      = aws_cloudwatch_event_rule.non_pim_role_report_lambda_rule.name
  target_id = "NonPimRoleReportFunctionV1"
  arn       = aws_lambda_function.non_pim_role_report_lambda.arn
}

## RootActivity CloudWatch Event Lambda Permissions
resource "aws_lambda_permission" "non_pim_role_report_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.non_pim_role_report_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.non_pim_role_report_lambda_rule.arn
}

#Cloudtrail Role Reporting Bucket
resource "aws_s3_bucket" "cloud_trail_reporting_bucket" {
  bucket = "platform-cloudtrail-report-bucket-us-east-1-${var.master_account}"
  object_lock_enabled = true
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_s3_bucket_public_access_block" "cloud_trail_reporting_bucket_block_public_access" {
  bucket = aws_s3_bucket.cloud_trail_reporting_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_acl" "cloud_trail_reporting_bucket_acl" {
  bucket = aws_s3_bucket.cloud_trail_reporting_bucket.id
}

resource "aws_s3_bucket_ownership_controls" "cloud_trail_reporting_bucket_ownership_controls" {
  bucket = aws_s3_bucket.cloud_trail_reporting_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

#Inventory data S3 bucket policy
resource "aws_s3_bucket_policy" "cloud_trail_reporting_bucket_policy" {
  bucket = aws_s3_bucket.cloud_trail_reporting_bucket.id
  policy = data.aws_iam_policy_document.cloud_trail_reporting_bucket_policy.json
}