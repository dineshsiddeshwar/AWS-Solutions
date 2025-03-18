# EMAIL Teamplate S3 bucket 
resource "aws_s3_bucket" "email_template_bucket" {
  bucket = "email-template-bucket-us-east-1-${var.master_account}"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "email_template_bucket_encryption" {
  bucket = aws_s3_bucket.email_template_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}

# Notifier Function Execution Role
resource "aws_iam_role" "notifier_lambda_role" {
  name = "platform_notifier_role"
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
  managed_policy_arns = [ "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",  "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_role_policy" "notifier_lambda_role_inline_policy" {
  name = "AllowNotiferToGetEmailTemplate"
  role = aws_iam_role.notifier_lambda_role.id
  policy = jsonencode({
    "Version": "2012-10-17"
    "Statement": [
      {
        "Sid": "AllowFunctionAccessToEmailTemplates",
        "Action": [
          "s3:GetObject",
        ],
        "Effect": "Allow",
        "Resource": "arn:aws:s3:::email-template-bucket-us-east-1-${var.master_account}/EmailTemplate/*",
        "Condition": {
          "StringEquals": {
              "aws:PrincipalOrgID": var.org_id,
          }
        }       
      },
      {
        "Sid": "AllowFunctionToSendEmail",
        "Action": [
          "ses:SendEmail",
        ],
        "Effect": "Allow"
        "Resource": "arn:aws:ses:us-east-1:${var.master_account}:identity/*"   
      },
    ]
  })
}

# Notifier Lambda Function
resource "aws_lambda_function" "notifier_lambda" {
  description   = "Function that received SNS events from config rules and emails end users who own the account id of the resource violation."
  filename      = "${path.module}/PythonFunctionZippedFiles/notifier.zip"
  function_name = "Notifier"
  role          = aws_iam_role.notifier_lambda_role.arn
  handler       = "main.lambda_handler"

  runtime = "python3.8"
  timeout = 300

  environment {
    variables = {
      ADMIN_EMAIL = var.sender_id
      S3_BUCKET_NAME = aws_s3_bucket.email_template_bucket.id
      TEAM_DL = var.TeamEmailDL
    }
  }
}

# Rotation Evaluation Lambda Function Execution Role
resource "aws_iam_role" "rotation_evaluation_lambda_role" {
  name                =  "platform_iam_key_rotation_evaluation_lambda_execution_role"
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
  path = "/"
  managed_policy_arns = [ "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole", "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_role_policy" "rotation_evaluation_lambda_role_inline_policy" {
  name = "AllowRotationEvaluationPermissions"
  role = aws_iam_role.rotation_evaluation_lambda_role.id
  policy = jsonencode({
    "Version": "2012-10-17"
    "Statement": [
      {
        "Action": [
          "sts:AssumeRole",
        ],
        "Effect": "Allow",
        "Resource": [
          "arn:aws:iam::*:role/platform_iam_key_rotation_evaluation_lambda_assumed_role",
        ],
        "Condition": {
          "StringEquals": {
              "aws:PrincipalOrgID": var.org_id,
          }
        }       
      },
      {
        "Action": [
          "lambda:InvokeFunction",
        ],
        "Effect": "Allow"
        "Resource": aws_lambda_function.notifier_lambda.arn  
      },
    ]
  })
}

# AccessKey Rotate Evaluation Lambda Function
resource "aws_lambda_function" "access_key_rotate_evaluation_lambda" {
  description   = "ASA Function to rotate IAM Access Keys on specified schedule"
  filename      = "${path.module}/PythonFunctionZippedFiles/access_key_rotation_evaluation.zip"
  function_name = "IAM-Access-Key-Rotation-Evaluation-Function"
  role          = aws_iam_role.rotation_evaluation_lambda_role.arn
  handler       = "main.lambda_handler"

  runtime = "python3.8"
  timeout = 400

  environment {
    variables = {
      RotationPeriod = var.RotationPeriod
      IAMAssumedRoleName = "platform_iam_key_rotation_evaluation_lambda_assumed_role"
      RoleSessionName = "IAM-Access-Key-Rotation-Evaluation-Function"
      Partition = "aws"
      NotifierArn = aws_lambda_function.notifier_lambda.arn 
      EmailTemplateAudit = "iam-key-rotation-notification.html"
      WarnPeriod = var.WarnPeriod
    }
  }
}

# Account Inventory Function Execution- Role
resource "aws_iam_role" "account_inventory_lambda_execution_role" {
  name                =  "platform_account_inventory_lambda_execution_role"
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
  path = "/"
  managed_policy_arns = [ "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole","arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_role_policy" "account_inventory_lambda_execution_role_inline_policy_1" {
  name = "AllowAWSOrgAccess"
  role = aws_iam_role.account_inventory_lambda_execution_role.id
  policy = jsonencode({
    "Version": "2012-10-17"
    "Statement": [
      {
        "Action": [
          "sts:AssumeRole",
        ],
        "Effect": "Allow",
        "Resource": "arn:aws:iam::${var.master_account}:role/platform_list_accounts_role",     
      },
      {
        "Action": [
          "lambda:InvokeFunction",
        ],
        "Effect": "Allow"
        "Resource": aws_lambda_function.access_key_rotate_evaluation_lambda.arn  
      },
    ]
  })
}

resource "aws_iam_role_policy" "account_inventory_lambda_execution_role_inline_policy_2" {
  name = "AllowDynamoDBAccess"
  role = aws_iam_role.account_inventory_lambda_execution_role.id
  policy = jsonencode({
    "Version": "2012-10-17"
    "Statement": [
      {
        "Action": [
          "dynamodb:GetItem",
        ],
        "Effect": "Allow",
        "Resource": "arn:aws:dynamodb:us-east-1:${var.master_account}:table/${var.accountDetailTableName}",    
      },
    ]
  })
}

# List Org Accounts IAM Role
resource "aws_iam_role" "list_accounts_role" {
  name                = "platform_list_accounts_role"
  description         = "IAM Assume Role used by ${var.master_account}'s ASA-Account-Inventory Lambda. This role is used to list accounts in the Organization."
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::${var.master_account}:role/platform_account_inventory_lambda_execution_role"
                        },
                        "Action": "sts:AssumeRole",
                    }
                ]
            })
}

resource "aws_iam_role_policy" "list_accounts_role_inline_policy" {
  name = "AllowListOrgAccounts"
  role = aws_iam_role.list_accounts_role.id
  policy = jsonencode({
    "Version": "2012-10-17"
    "Statement": [
      {
        "Action": [
          "organizations:ListAccounts",
          "organizations:ListAccountsForParent",
          "organizations:ListChildren",
        ],
        "Effect": "Allow",
        "Resource": "*",    
      },
    ]
  })
}

# Account Inventory Lambda Function
resource "aws_lambda_function" "account_inventory_lambda" {
  description   = "Function that calls the DescribeAccount & ListAccounts on AWS Organizations to collect all AWS Account IDs and corresponding Emails."
  filename      = "${path.module}/PythonFunctionZippedFiles/account_inventory.zip"
  function_name = "Account-Inventory"
  role          = aws_iam_role.account_inventory_lambda_execution_role.arn
  handler       = "main.lambda_handler"

  runtime = "python3.8"
  timeout = 300

  environment {
    variables = {
      LambdaRotationEvaluationFunction = "IAM-Access-Key-Rotation-Evaluation-Function"
      OrgListAccount = var.master_account
      OrgListRole = "platform_list_accounts_role"
      RoleSessionName = "IAM-Access-Account-Inventory-Function"
      DynamoDBTable = var.accountDetailTableName
    }
  }
}

# Rotation Notifier CloudWatch Event Rule
resource "aws_cloudwatch_event_rule" "raotation_notifier_cw_rule" {
  description = "CloudWatch Event to trigger Access Key rotation evaluation Lambda Function daily"
  schedule_expression = "cron(0 6 1,15 * ? *)"
  is_enabled = true
}

# Rotation Notifier CloudWatch Event Rule target
resource "aws_cloudwatch_event_target" "raotation_notifier_cw_rule_target" {
  rule      = aws_cloudwatch_event_rule.raotation_notifier_cw_rule.name
  target_id = "AccountInventoryLambdaFunction"
  arn       = aws_lambda_function.account_inventory_lambda.arn
}

#ControlTower Update EventBridgeRule Target Invoke Permission
resource "aws_lambda_permission" "control_tower_account_update_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.account_inventory_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.raotation_notifier_cw_rule.arn
}