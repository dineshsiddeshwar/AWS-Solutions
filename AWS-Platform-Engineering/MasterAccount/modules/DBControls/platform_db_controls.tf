# SSM Parameter store 
resource "aws_ssm_parameter" "scorecard_bucket_parameter" {
  name  = "ScoreCardBucketName"
  type  = "String"
  value = var.ScoreCardBucketName
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_ssm_parameter" "dpsom_dl_parameter" {
  name  = "DPSOMDL"
  type  = "String"
  value = var.DPSOMDL
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_ssm_parameter" "scorecard_db_table_name_parameter" {
  name  = "ScoreCardDBTableName"
  type  = "String"
  value = var.ScoreCardDBTableName
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_ssm_parameter" "config_aggregator_name_parameter" {
  name  = "ConfigAggregatorName"
  type  = "String"
  value = var.ConfigAggregatorName
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# DB ScoreCard Table
resource "aws_dynamodb_table" "db_scorecard_table" {
  name           = var.ScoreCardDBTableName
  read_capacity  = 5
  write_capacity = 5

  hash_key       = "unix_timestamp"

  point_in_time_recovery { 
    enabled = true 
  }

  attribute {
    name = "unix_timestamp"
    type = "N"
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# DB Controls Role
resource "aws_iam_role" "db_controls_role" {
  name                =  "platform_dynamodb_dbcontrols"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "*"
                        },
                        "Action": "sts:AssumeRole",
                    }
                ]
            })
  path = "/"
  managed_policy_arns = [ aws_iam_policy.db_controls_policy.arn,  "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_policy" "db_controls_policy" {
  name        = "platform_dynamodb_dbcontrols_policy"
  path        = "/"
  description = "DBControlsPolicy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:*",
        ]
        Effect   = "Allow"
        Resource = aws_dynamodb_table.db_scorecard_table.arn
        Sid = "VisualEditor0"
      },
    ]
  })
}

# Create Report From DynamoDB Role
resource "aws_iam_role" "create_report_from_dynamodb_role" {
  name                =  "platform_CreateReportFromDynamoDBRole"
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
  path = "/"
  managed_policy_arns = [ 
    aws_iam_policy.create_report_from_dynamodb_policy.arn,
    "arn:aws:iam::aws:policy/AWSConfigUserAccess",
     "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"
  ]
}

resource "aws_iam_policy" "create_report_from_dynamodb_policy" {
  name        = "platform_CreateReportFromDynamoDBPolicy"
  path        = "/"
  description = "CreateReportFromDynamoDBPolicy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:*",
        ]
        Effect   = "Allow"
        Resource = [aws_dynamodb_table.db_scorecard_table.arn]
        Sid = "VisualEditor0"
      },
      {
        Action = [
          "ssm:GetParameters",
          "ssm:GetParameter"
        ]
        Effect   = "Allow"
        Resource = ["arn:aws:ssm:*:${var.master_account}:parameter/*"]
        Sid = "VisualEditor1"
      },
      {
        Action = [
          "ses:SendEmail"
        ]
        Effect   = "Allow"
        Resource = "*"
        Sid = "VisualEditor2"
      },
      {
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = ["arn:aws:logs:us-east-1:${var.master_account}:log-group:/aws/lambda/ScoreCardCreateReportFromDynamoDB:*"]
        Sid = "VisualEditor3"
      },
      {
          Action = [
              "logs:CreateLogGroup"
          ],
          Resource = [
              "arn:aws:logs:us-east-1:136349175397:*"
          ],
          Effect = "Allow",
          Sid = "VisualEditor4"
      }
    ]
  })
}

# Create Report From DynamoDB Lambda
resource "aws_lambda_function" "create_report_from_dynamodb_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_ScoreCardCreateReportFromDynamoDB.zip"
  function_name = "platform_ScoreCardCreateReportFromDynamoDB"
  role          = aws_iam_role.create_report_from_dynamodb_role.arn
  handler       = "platform_ScoreCardCreateReportFromDynamoDB.lambda_handler"
  source_code_hash = data.archive_file.create_report_from_dynamodb_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_cloudwatch_event_rule" "create_report_from_dynamodb_lambda_schedule" {
  count = var.env_type == "prod" ? 1 : 0
  name = "CreateReportFromDynamoDB_lambda_rule"
  description = "Scheduled Rule once every month"
  schedule_expression = "cron(0 1 27 * ? *)"
  is_enabled = true
}

resource "aws_cloudwatch_event_target" "create_report_from_dynamodb_lambda_target" {
  count = var.env_type == "prod" ? 1 : 0
  rule      = aws_cloudwatch_event_rule.create_report_from_dynamodb_lambda_schedule[count.index].name
  target_id = "CreateReportFromDynamoDBV1"
  arn       = aws_lambda_function.create_report_from_dynamodb_lambda.arn
}

resource "aws_lambda_permission" "create_report_from_dynamodb_lambda_permission" {
  count = var.env_type == "prod" ? 1 : 0
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.create_report_from_dynamodb_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.create_report_from_dynamodb_lambda_schedule[count.index].arn
}

# ScoreCard Invoke StepFunction Organisation Role
resource "aws_iam_role" "scorecard_invoke_step_function_role" {
  name                =  "platform_ScoreCardInvokeStepFunctionOrganisationRole"
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
  path = "/"
  managed_policy_arns = [ 
    aws_iam_policy.scorecard_invoke_step_function_policy.arn,  "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"
  ]
}

resource "aws_iam_policy" "scorecard_invoke_step_function_policy" {
  name        = "platform_ScoreCardInvokeStepFunctionOrganisationPolicy"
  path        = "/"
  description = "ScoreCardInvokeStepFunctionOrganisationPolicy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "organizations:ListAccounts",
        ]
        Effect   = "Allow"
        Resource = "*"
        Sid = "VisualEditor1"
      },
      {
        Action = [
          "sts:AssumeRole"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:iam::*:role/platform_InvokeStepFunctionChildAccountRole"
        Sid = "VisualEditor2"
      },
      {
        Action = [
          "logs:CreateLogGroup"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:us-east-1:${var.master_account}:*"
        Sid = "VisualEditor3"
      }
    ]
  })
}

# ScoreCard Invoke Step Function Organisation
resource "aws_lambda_function" "scorecard_invoke_step_function_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_ScoreCardInvokeStepFunctionOrganisation.zip"
  function_name = "platform_ScoreCardInvokeStepFunctionOrganisation"
  role          = aws_iam_role.scorecard_invoke_step_function_role.arn
  handler       = "platform_ScoreCardInvokeStepFunctionOrganisation.lambda_handler"
  source_code_hash = data.archive_file.scorecard_invoke_step_function_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 512
  timeout = 900

  environment {
    variables = {
      StateMachine_Name = "platform_RDSDBControlsStateMachine"
    }
  }
  tags = {
    "platform_donotdelete" = "yes"
  }
}


