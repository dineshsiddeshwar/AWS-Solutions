#IAM Role for platform_close_account Lambda function
resource "aws_iam_role" "close_account_lambda_role" {
  name                =  "platform_close_account_lambda_role"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole",
                    }
                ]
            })
  path                = "/"
}

resource "aws_iam_role_policy" "close_account_lambda_role_inline_policy" {
  name = "CloseAccountLambdaRolePolicy"
  role = aws_iam_role.close_account_lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "Organizations"
        Action = [
          "organizations:CloseAccount",
          "organizations:DescribeAccount",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Sid = "CWLogs"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        Effect   = "Allow"
        Resource = "${aws_cloudwatch_log_group.close_account_log_group.arn}:*"
      },
    ]
  })
}

#Lambda function to automate AWS account closure
resource "aws_lambda_function" "close_account_lambda" {
  description   = "This Lambda function automates the closure of AWS account using Organizations API calls"
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_close_account.zip"
  function_name = "platform_close_account"
  role          = aws_iam_role.close_account_lambda_role.arn
  handler       = "platform_close_account.lambda_handler"
  source_code_hash = data.archive_file.close_account_lambda_zip.output_base64sha256

  runtime = "python3.10"
  timeout = 300
  memory_size = 128

  tags = {
    "platform_donotdelete" = "yes"
  }
}

#CloudWatch Log Group for platform_close_account Lambda function
resource "aws_cloudwatch_log_group" "close_account_log_group" {
  name = "/aws/lambda/platform_close_account"

  tags = {
    platform_donotdelete = "yes"
  }
}

#KMS Key to encrypt SNS Topic
resource "aws_kms_key" "close_account_sns_data_encryption_key" {
  description = "AWS KMS Key to encrypt the SNS Topic at-rest"
  is_enabled = true
  enable_key_rotation = true
  deletion_window_in_days = 7
}


#KMS Key Policy for CloseAccSNSKMSKey
resource "aws_kms_alias" "close_account_sns_data_encryption_key_alias" {
  name          = "alias/CloseAccount-SNSTopic-Key"
  target_key_id = aws_kms_key.close_account_sns_data_encryption_key.key_id
}

#KMS Key Policy for CloseAccSNSKMSKey 
resource "aws_kms_key_policy" "close_account_sns_data_encryption_key_policy" {
  key_id = aws_kms_key.close_account_sns_data_encryption_key.id
  policy = jsonencode({
    Id = "KMS-Key-Policy"
    Statement = [
      {
        Action = "kms:*"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${var.master_account}:root"
        }

        Resource = "*"
        Sid      = "Enable IAM User Permissions"
      },
      {
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey*"
        ]
        Effect = "Allow"
        Principal = {
          Service = "cloudwatch.amazonaws.com"
        }

        Resource = "*"
        Sid      = "Allow CloudWatch for CMK"
      },
    ]
    Version = "2012-10-17"
  })
}

#CloudWatch Metric Filter to capture account closure limit breached from platform_close_account CW Log Group
resource "aws_cloudwatch_log_metric_filter" "close_account_metric_filter" {
  name           = var.close_account_metric_filter_name
  pattern        = "ConstraintViolationException"
  log_group_name = aws_cloudwatch_log_group.close_account_log_group.name

  metric_transformation {
    name      = "AccountClosure"
    namespace = "QuotaExceeded"
    value     = "1"
    unit      = "Count"
  }
}

#SNS Topic to get notified about closure limit breach
resource "aws_sns_topic" "close_account_sns_topic" {
  name = "ClosureQuotaExceedException-SNSTopic"
  kms_master_key_id = aws_kms_key.close_account_sns_data_encryption_key.id
  tags = {
    "platform_donotdelete" = "yes"
  }
}

#SNS Subscription for SNS Topic ClosureQuotaExceedException-SNSTopic
resource "aws_sns_topic_subscription" "close_account_sns_topic_subscription" {
  topic_arn = aws_sns_topic.close_account_sns_topic.arn
  protocol  = "email"
  endpoint  = var.admin_dl
}


#CloudWatch Alarm to notify about closure limit breach
resource "aws_cloudwatch_metric_alarm" "close_account_alarm" {
  alarm_name                = "CloseAccountQuotaExceededAlarm"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  metric_name               = "AccountClosure"
  namespace                 = "QuotaExceeded"
  period                    = 60
  statistic                 = "Sum"
  threshold                 = 1.0
  alarm_description         = "CloudWatch alarm to notify when close account quota is exceeded for the past 30 days."
  alarm_actions             = [aws_sns_topic.close_account_sns_topic.arn]
}