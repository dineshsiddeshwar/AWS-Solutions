data "aws_region" "current" {}

locals {
    region = data.aws_region.current.name
}

#Hub Root Activity Event Bus
resource "aws_cloudwatch_event_bus" "hub_root_activity_event_bus" {
  name = "platform-hub-root-activity"
}

#Hub Root Activity Event Bus Policy
resource "aws_cloudwatch_event_bus_policy" "hub_root_activity_event_bus_policy" {
  policy         = data.aws_iam_policy_document.hub_root_activity_event_bus_policy.json
  event_bus_name = aws_cloudwatch_event_bus.hub_root_activity_event_bus.name
}

#RootActivity Notification Function Execution Role
resource "aws_iam_role" "root_activity_notification_lambda_execution_role" {
  name                =  "platform_root_monitoring_iam_role"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "AllowExecutionPermissionsOnFunction"
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole",
                    }
                ]
            })
}

resource "aws_iam_role_policy" "root_activity_notification_lambda_execution_role_inline_policy" {
  name = "LambdaRootAPIMonitorPolicy"
  role = aws_iam_role.root_activity_notification_lambda_execution_role.id
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
        Sid = "ListAccount"
        Action = [
          "organizations:ListAccounts"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Sid = "S3WritePolicy"
        Action = [
          "s3:PutObject"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:s3:::platform-root-activity-events-bucket-us-east-1-${var.master_account}/*"
      },
    ]
  })
}

#Root Activity Notification Lambda Function
resource "aws_lambda_function" "root_activity_notification_lambda" {
  description   = "Function that received SNS events from config rules and emails end users who own the account id of the resource violation."
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_root_activity_monitor.zip"
  function_name = "platform-root-activity-monitor"
  role          = aws_iam_role.root_activity_notification_lambda_execution_role.arn
  handler       = "platform_root_activity_monitor.lambda_handler"
  source_code_hash = data.archive_file.root_activity_notification_lambda_zip.output_base64sha256

  runtime = "python3.8"
  timeout = 300

  environment {
    variables = {
      ExemptionDays = var.RootMonitoringExemptionDays
      ROOT_LOGIN_BUCKET = aws_s3_bucket.root_activity_events_bucket.id
    }
  }
}

# RootActivity CloudWatch Event Lambda Rule Trigger
resource "aws_cloudwatch_event_rule" "root_activity_lambda_trigger_lambda_rule" {
  description = "CloudWatch Event to trigger Access Key auto-rotation Lambda Function daily"
  name = "platform-hub-capture-root-activity"
  event_bus_name = aws_cloudwatch_event_bus.hub_root_activity_event_bus.name
  event_pattern = jsonencode({
    detail-type = [
      "AWS Console Sign In via CloudTrail"
    ],
    detail = {
      "eventName": [
          "ConsoleLogin", 
        ],
        "userIdentity": {
          "type": [
              "Root"
            ]
        }
    },
  })
  is_enabled = true
}

# RootActivity CloudWatch Event Lambda Rule Target
resource "aws_cloudwatch_event_target" "root_activity_lambda_trigger_lambda_rule_target" {
  rule      = aws_cloudwatch_event_rule.root_activity_lambda_trigger_lambda_rule.name
  target_id = "cloudwatchRuleInvokeLambdaACC"
  arn       = aws_lambda_function.root_activity_notification_lambda.arn
  event_bus_name = aws_cloudwatch_event_bus.hub_root_activity_event_bus.name
}

## RootActivity CloudWatch Event Lambda Permissions
resource "aws_lambda_permission" "root_activity_lambda_trigger_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.root_activity_notification_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.root_activity_lambda_trigger_lambda_rule.arn
}

#Root Activity Events Bucket
resource "aws_s3_bucket" "root_activity_events_bucket" {
  bucket = "platform-root-activity-events-bucket-us-east-1-${var.master_account}"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "root_activity_events_bucket_encryption" {
  bucket = aws_s3_bucket.root_activity_events_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "root_activity_events_bucket_block_public_access" {
  bucket = aws_s3_bucket.root_activity_events_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

#Athena S3 Bucket
resource "aws_s3_bucket" "athena_s3_bucket" {
  bucket = "platform-athena-output-storage-us-east-1-${var.master_account}"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "athena_s3_bucket_encryption" {
  bucket = aws_s3_bucket.athena_s3_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "athena_s3_bucket_block_public_access" {
  bucket = aws_s3_bucket.athena_s3_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

#Athena Table
resource "aws_athena_named_query" "root_login_event_table_athena_query" {
  name      = "root-login-event"
  description = "A query that selects all aggregated data"
  database  = "default"
  query   = "CREATE EXTERNAL TABLE `platform_root_login_event`(\n  `location` string COMMENT 'from deserializer', \n  `account_name` string COMMENT 'from deserializer', \n  `detail` struct\u003ceventtime:string,eventname:string,sourceipaddress:string,recipientaccountid:string\u003e COMMENT 'from deserializer')\nROW FORMAT SERDE \n  'org.openx.data.jsonserde.JsonSerDe' \nWITH SERDEPROPERTIES ( \n  'ignore.malformed.json'='true') \nSTORED AS INPUTFORMAT \n  'org.apache.hadoop.mapred.TextInputFormat' \nOUTPUTFORMAT \n  'org.apache.hadoop.hive.ql.io.IgnoreKeyTextOutputFormat'\nLOCATION\n  's3://platform-root-activity-events-bucket-us-east-1-${var.master_account}/'\nTBLPROPERTIES (\n  'transient_lastDdlTime'='1677237369')\n"
}

#Athena View
resource "aws_athena_named_query" "root_login_event_view_athena_query" {
  name      = "root-login-event-view"
  description = "A query that selects all aggregated data"
  database  = "default"
  query   = "CREATE OR REPLACE VIEW \"platform_root_login_event_view\" AS  SELECT\n  account_name AccountName\n, detail.recipientAccountId AccountID , detail.eventTime Timestamp , detail.eventName Event , detail.sourceIPAddress SourceIP , location FROM\n  default.platform_root_login_event\n"
}