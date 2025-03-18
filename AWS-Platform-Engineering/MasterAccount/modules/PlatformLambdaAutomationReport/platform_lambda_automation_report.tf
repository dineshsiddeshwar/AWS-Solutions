#Platform lambda resource for automation Report
resource "aws_lambda_function" "platform_lambda_automation_report" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_lambda_automation_report.zip"
  function_name = "platform_lambda_automation_report"
  role          = var.master_admin_role_arn
  handler       = "platform_lambda_automation_report.lambda_handler"
  source_code_hash = data.archive_file.platform_lambda_automation_report_zip.output_base64sha256

  runtime = "python3.9"
  timeout = 900
  memory_size = 128

  environment {
    variables = {
      BUCKET = "platform-automation-report-bucket-us-east-1-${var.master_account}"
      MASTER_ACCOUNT_ID = var.master_account
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
resource "aws_cloudwatch_event_rule" "platform_automation_report_lambda_rule" {
  description = "Scheduled Rule for once a month"
  name = "platform_automation_report_lambda_trigger"
  schedule_expression = "cron(35 11 1 * ? *)"
  is_enabled = true
}

# RootActivity CloudWatch Event Lambda Rule Target
resource "aws_cloudwatch_event_target" "platform_automation_report_lambda_rule_target" {
  rule      = aws_cloudwatch_event_rule.platform_automation_report_lambda_rule.name
  target_id = "PlatformAutomationLambdaReportFunctionV1"
  arn       = aws_lambda_function.platform_lambda_automation_report.arn
}

## RootActivity CloudWatch Event Lambda Permissions
resource "aws_lambda_permission" "platform_automation_report_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.platform_lambda_automation_report.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.platform_automation_report_lambda_rule.arn
}

#lambda function for lambda-fuction create and role policy chnaged alert
resource "aws_lambda_function" "platform_lambda_automation_alert" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_lambda_automation_alert.zip"
  function_name = "platform_lambda_automation_alert"
  role          = var.master_admin_role_arn
  handler       = "platform_lambda_automation_alert.lambda_handler"
  source_code_hash = data.archive_file.platform_lambda_automation_alert_zip.output_base64sha256

  runtime = "python3.9"
  timeout = 900
  memory_size = 128

  environment {
    variables = {
      BUCKET = "platform-automation-report-bucket-us-east-1-${var.master_account}"
      MASTER_ACCOUNT_ID = var.master_account
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
resource "aws_cloudwatch_event_rule" "platform_automation_alert_lambda_rule" {
  description = "Scheduled Rule for daily alert"
  name = "platform_automation_alert_lambda_trigger"
  schedule_expression = "cron(30 11 * * ? *)"
  is_enabled = true
}

# RootActivity CloudWatch Event Lambda Rule Target
resource "aws_cloudwatch_event_target" "platform_automation_alert_lambda_rule_target" {
  rule      = aws_cloudwatch_event_rule.platform_automation_alert_lambda_rule.name
  target_id = "PlatformAutomationLambdaAlertFunctionV1"
  arn       = aws_lambda_function.platform_lambda_automation_alert.arn
}

## RootActivity CloudWatch Event Lambda Permissions
resource "aws_lambda_permission" "platform_automation_alert_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.platform_lambda_automation_alert.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.platform_automation_alert_lambda_rule.arn
}



#platform automation Reporting Bucket
resource "aws_s3_bucket" "platform_automation_reporting_bucket" {
  bucket = "platform-automation-report-bucket-us-east-1-${var.master_account}"
  object_lock_enabled = true
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_s3_bucket_public_access_block" "platform_automation_reporting_bucket_block_public_access" {
  bucket = aws_s3_bucket.platform_automation_reporting_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "platform_automation_reporting_bucket_ownership_controls" {
  bucket = aws_s3_bucket.platform_automation_reporting_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

#Inventory data S3 bucket policy
resource "aws_s3_bucket_policy" "platform_automation_reporting_bucket_policy" {
  bucket = aws_s3_bucket.platform_automation_reporting_bucket.id
  policy = data.aws_iam_policy_document.platform_automation_reporting_bucket_policy.json
}
