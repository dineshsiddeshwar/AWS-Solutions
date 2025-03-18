#Platform Non Pim Role Report
resource "aws_lambda_function" "daily_instance_details" {
  filename      = "${path.module}/PythonFunctionZippedFiles/daily_instance_details.zip"
  function_name = "daily_instance_details"
  role          = var.master_admin_role_arn
  handler       = "daily_instance_details.lambda_handler"
  source_code_hash = data.archive_file.daily_instance_details_zip.output_base64sha256

  runtime = "python3.8"
  timeout = 900
  memory_size = 2176

  environment {
    variables = {
      BUCKET = "platform-daily-instance-report-${var.master_account}"
      ConfigurationAggregator_Name = "aws-controltower-ConfigAggregatorForOrganizations"
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# RootActivity CloudWatch Event Lambda Rule Trigger
resource "aws_cloudwatch_event_rule" "daily_instance_report_lambda_rule" {
  description = "Scheduled Rule for Daily Trigger"
  name = "daily_instance_details_lambda_trigger"
  schedule_expression = "cron(0 10 * * ? *)"
  is_enabled = true
}

# RootActivity CloudWatch Event Lambda Rule Target
resource "aws_cloudwatch_event_target" "daily_instance_report_lambda_rule_target" {
  rule      = aws_cloudwatch_event_rule.daily_instance_report_lambda_rule.name
  target_id = "NonPimRoleReportFunctionV1"
  arn       = aws_lambda_function.daily_instance_details.arn
}

## RootActivity CloudWatch Event Lambda Permissions
resource "aws_lambda_permission" "daily_instance_report_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.daily_instance_details.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_instance_report_lambda_rule.arn
}

#Cloudtrail Role Reporting Bucket
resource "aws_s3_bucket" "daily_instance_report_bucket" {
  bucket = "platform-daily-instance-report-${var.master_account}"
  object_lock_enabled = true
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_s3_bucket_public_access_block" "daily_instance_report_bucket_block_public_access" {
  bucket = aws_s3_bucket.daily_instance_report_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "daily_instance_report_bucket_ownership_controls" {
  bucket = aws_s3_bucket.daily_instance_report_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

#Inventory data S3 bucket policy
resource "aws_s3_bucket_policy" "daily_instance_report_bucket_policy" {
  bucket = aws_s3_bucket.daily_instance_report_bucket.id
  policy = data.aws_iam_policy_document.daily_instance_report_bucket_policy.json
}