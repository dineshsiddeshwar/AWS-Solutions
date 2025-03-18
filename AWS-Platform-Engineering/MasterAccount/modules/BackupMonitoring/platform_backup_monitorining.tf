#Backup Monitoring Logs S3B ucket
resource "aws_s3_bucket" "backup_monitoring_logs_bucket" {
  bucket = "platform-backup-monitoring-logs-us-east-1-${var.master_account}"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backup_monitoring_logs_bucket_encryption" {
  bucket = aws_s3_bucket.backup_monitoring_logs_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "backup_monitoring_logs_bucket_block_public_access" {
  bucket = aws_s3_bucket.backup_monitoring_logs_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "backup_monitoring_logs_bucket_policy" {
  bucket = aws_s3_bucket.backup_monitoring_logs_bucket.id
  policy = data.aws_iam_policy_document.backup_monitoring_logs_bucket_policy.json
}

# Backup Monitoring Report Plan
resource "aws_backup_report_plan" "backup_monitoring_report_plan" {
  name        = "platform_backup_jobs_report_plan"
  description = "Generates Backup Jobs report trigerred by an hourly CW Event Rule"

  report_delivery_channel {
    formats = [
      "CSV",
    ]
    s3_bucket_name = aws_s3_bucket.backup_monitoring_logs_bucket.id
  }

  report_setting {
    report_template = "BACKUP_JOB_REPORT"
    organization_units = [
      var.private_production_ou,
      var.private_staging_ou,
      var.private_exception_ou,
      var.public_staging_ou,
      var.public_production_ou,
      var.public_exception_ou,
      var.managed_services_beagile_ou,
      var.data_management_ou,
      var.hybrid_account_ou,
      var.migration_account_ou
    ]
    regions = [
      "us-east-1",
      "us-east-2",
      "us-west-1",
      "us-west-2",
      "ap-south-1",
      "ap-northeast-1",
      "ap-northeast-2",
      "ap-southeast-1",
      "ap-southeast-2",
      "ca-central-1",
      "eu-central-1",
      "eu-west-1",
      "eu-west-2",
      "eu-west-3",
      "eu-north-1",
      "sa-east-1"    
    ]
  }

}

# Backup Report Lambda Trigger CW Event Rule
resource "aws_cloudwatch_event_rule" "backup_report_trigger_lambda_rule" {
  description = "CloudWatch Event to trigger backup report trigger lambda once 8 hours"
  name = "platform-backup-monitoring-logs-rule"
  schedule_expression = "rate(8 hours)"
  is_enabled = true
}

# Backup Report Lambda Trigger CW Event Rule target
resource "aws_cloudwatch_event_target" "backup_report_trigger_lambda_rule_target" {
  rule      = aws_cloudwatch_event_rule.backup_report_trigger_lambda_rule.name
  target_id = "cloudwatchRuleInvokeLambdaACC"
  arn       = aws_lambda_function.backup_report_trigger_lambda.arn
}

#Rotation CloudWatch Event Lambda Trigger Lambda Permissions
resource "aws_lambda_permission" "backup_report_trigger_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.backup_report_trigger_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.backup_report_trigger_lambda_rule.arn
}

#Backup Report Trigger Function Execution Role
resource "aws_iam_role" "backup_report_trigger_lambda_role" {
  name                =  "platform_backup-report_trigger_lambda_role"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "AllowExecutionPermissionsOnFunction",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole",
                    }
                ]
            })
}

resource "aws_iam_role_policy" "backup_report_trigger_lambda_role_inline_policy" {
  name = "platform_LambdaRootAPIMonitorPolicy"
  role = aws_iam_role.backup_report_trigger_lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "LogStreamAccess"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Sid = "StartBackupReportJob"
        Action = [
          "backup:StartReportJob"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

#Backup Report Trigger Lambda Function
resource "aws_lambda_function" "backup_report_trigger_lambda" {
  description   = "Function that is trigerred on schedule basis and triggers the backup report plan job."
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_backup_monitoring.zip"
  function_name = "platform_backup_report_job_trigger"
  role          = aws_iam_role.backup_report_trigger_lambda_role.arn
  handler       = "platform_backup_monitoring.lambda_handler"
  source_code_hash = data.archive_file.backup_report_trigger_lambda_zip.output_base64sha256
  
  runtime = "python3.8"
  timeout = 300

  environment {
    variables = {
      REPORT_PLAN = "platform_backup_jobs_report_plan"
    }
  }
}

#Athena Table
resource "aws_athena_named_query" "backup_report_table_athena_query" {
  name      = "platform_backup_report_table"
  description = "A query that selects all aggregated data"
  database  = "default"
  query   = "CREATE EXTERNAL TABLE `platform_backup_report_table`(\n    `report_period_start` string, \n    `report_period_end` string, \n    `path_to_root` string, \n    `account_id` string, \n    `region` string, \n    `backup_job_id` string, \n    `job_status` string, \n    `status_message` string, \n    `resource_type` string, \n    `resource_arn` string, \n    `backup_plan_arn` string, \n    `backup_rule_id` string, \n    `creation_date` string, \n    `completion_date` string, \n    `expected_completion_date` string, \n    `recoverypoint_arn` string, \n    `job_run_time` string, \n    `backup_size_in_bytes` string, \n    `backup_vault_name` string, \n    `backup_vault_arn` string, \n    `iam_role_arn` string)\n  ROW FORMAT DELIMITED \n    FIELDS TERMINATED BY ',' \n  STORED AS INPUTFORMAT \n    'org.apache.hadoop.mapred.TextInputFormat' \n  OUTPUTFORMAT \n    'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'\n  LOCATION\n    's3://platform-backup-monitoring-logs-us-east-1-${var.master_account}/Backup/crossaccount/crossregion'\n  TBLPROPERTIES (\n    'case.insensitive'='true', \n    'classification'='csv', \n    'skip.header.line.count'='1', \n    'transient_lastDdlTime'='1686224768')\n"
}

#Athena View
resource "aws_athena_named_query" "backup_report_view_athena_query" {
  name      = "platform_backup_report_view"
  description = "A query that selects all aggregated data"
  database  = "default"
  query   = "\nCREATE OR REPLACE VIEW \"platform_backup_report_view\" AS \n  SELECT DISTINCT\n    account_id Account_ID\n  , backup_job_id Backup_Job_ID\n  , \"date_parse\"(\"split_part\"(creation_date, 'T', 1), '%Y-%m-%d') job_date\n  , job_status Job_Status\n  , status_message\n  , resource_type\n  , resource_arn\n  , creation_date\n  , completion_date\n  , recoverypoint_arn\n  , job_run_time\n  , backup_size_in_bytes\n  , backup_vault_name\n  FROM\n    default.platform_backup_report_table\n  WHERE ((job_status IN ('COMPLETED', 'FAILED')) AND (backup_vault_name = 'platform_backupvault'))\n"
}
