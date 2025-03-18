## Platform lambda resource for finding login profile of users
resource "aws_lambda_function" "monthly_innersource_tagbased_report" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_monthly_innersource_report.zip"
  function_name = "platform_monthly_innersource_report"
  role          = var.master_admin_role_arn
  handler       = "platform_monthly_innersource_report.lambda_handler"
  source_code_hash = data.archive_file.monthly_innersource_report_zip.output_base64sha256

  runtime = "python3.9"
  timeout = 900
  memory_size = 128

  environment {
    variables = {
      BUCKET = "platform-innersource-tags-monthly-report-${var.master_account}"
      ConfigurationAggregator_Name = "aws-controltower-ConfigAggregatorForOrganizations"
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

## Innersource CloudWatch Event Lambda Rule Trigger
resource "aws_cloudwatch_event_rule" "platform_monthly_innersource_report_rule" {
  description = "Scheduled Rule for once a month"
  name = "platform_monthly_innersource_report_trigger"
  schedule_expression = "cron(0 5 1 * ? *)"
  is_enabled = true
}

## Innersource CloudWatch Event Lambda Rule Target
resource "aws_cloudwatch_event_target" "platform_monthly_innersource_report_target" {
  rule      = aws_cloudwatch_event_rule.platform_monthly_innersource_report_rule.name
  target_id = "platform_monthly_innersource_report"
  arn       = aws_lambda_function.monthly_innersource_tagbased_report.arn
}

## Innersource CloudWatch Event Lambda Permissions
resource "aws_lambda_permission" "platform_monthly_innersource_report_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.monthly_innersource_tagbased_report.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.platform_monthly_innersource_report_rule.arn
}


## Innersource tag based resources Reporting Bucket
resource "aws_s3_bucket" "monthly_innersource_report_bucket" {
  bucket = "platform-innersource-tags-monthly-report-${var.master_account}"
  object_lock_enabled = true
  tags = {
    "platform_donotdelete" = "yes"
  }
}

## Innersource tag based resources Reporting Bucket Public Access Block
resource "aws_s3_bucket_public_access_block" "monthly_innersource_report_bucket_block_public_access" {
  bucket = aws_s3_bucket.monthly_innersource_report_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

## Innersource tag based resources Reporting Bucket Ownership Controls
resource "aws_s3_bucket_ownership_controls" "monthly_innersource_report_bucket_ownership_controls" {
  bucket = aws_s3_bucket.monthly_innersource_report_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

## Innersource Report data S3 bucket policy
resource "aws_s3_bucket_policy" "monthly_innersource_report_bucket_policy" {
  bucket = aws_s3_bucket.monthly_innersource_report_bucket.id
  policy = data.aws_iam_policy_document.monthly_innersource_report_bucket_policy.json
}
