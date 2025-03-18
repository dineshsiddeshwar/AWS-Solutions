# UpdateAltContactsFunctionExecutionRole
resource "aws_iam_role" "update_alt_contacts_lambda_role" {
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid" : "AllowExecutionPermissionsOnFunction"
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }                    
                ]
            })
}

resource "aws_iam_role_policy" "update_alt_contacts_lambda_role_inline_policy" {
  name = "LambdaRootAPIMonitorPolicy"
  role = aws_iam_role.update_alt_contacts_lambda_role.id
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
        Sid = "UpdateAltContacts"
        Action = [
          "account:PutAlternateContact",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}
# Lambda to update alternate contacts in member accounts
resource "aws_lambda_function" "update_alternate_contacts_lambda" {
  description   = "Function to update security contact information"
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_update_alternate_contacts.zip"
  function_name = "AlternateContactUpdateLambda"
  role          = aws_iam_role.update_alt_contacts_lambda_role.arn
  handler       = "platform_update_alternate_contacts.lambda_handler"
  source_code_hash = data.archive_file.update_alternate_contacts_lambda_zip.output_base64sha256

  runtime = "python3.8"
  timeout = 400

  environment {
    variables = {
      SECURITY_EMAIL= var.SecurityContactEmail
      SECURITY_CONTACT_NAME= var.SecurityContactName
      SECURITY_CONTACT_TITLE= var.SecurityContactTitle
      SECURITY_CONTACT_PHONE= var.SecurityContactPhone
      OPERATIONS_EMAIL= var.OperationsContactEmail
      OPERATIONS_CONTACT_NAME= var.OperationsContactName
      OPERATIONS_CONTACT_TITLE= var.OperationsContactTitle
      OPERATIONS_CONTACT_PHONE= var.OperationsContactPhone
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}


# ControlTower Account Create EventBridge Rule
resource "aws_cloudwatch_event_rule" "control_tower_account_create_rule" {
  event_pattern = jsonencode({
    source: [
      "aws.controltower"      
    ],
    detail-type = [
      "AWS Service Event via CloudTrail"
    ],
    detail = {
        "eventName": [
          "CreateManagedAccount", 
        ],
        "serviceEventDetails": {
          "createManagedAccountStatus": {
            "state": [
              "SUCCEEDED"
            ]
          }
        }
    },
  })
  is_enabled = true
}

# ControlTower Account Create EventBridge Rule target
resource "aws_cloudwatch_event_target" "control_tower_account_create_rule_target_1" {
  rule      = aws_cloudwatch_event_rule.control_tower_account_create_rule.name
  target_id = "ControlTowerAccountCreateLambdaTarget"
  arn       = aws_lambda_function.update_alternate_contacts_lambda.arn
}

resource "aws_cloudwatch_event_target" "control_tower_account_create_rule_target_2" {
  rule      = aws_cloudwatch_event_rule.control_tower_account_create_rule.name
  target_id = "ControlTowerAccountCreateLambdaTargetSecurityHub"
  arn       = aws_lambda_function.enable_security_hub_standards_lambda.arn
}

#ControlTower Create EventBridgeRule Target Invoke Permission
resource "aws_lambda_permission" "control_tower_account_create_lambda_permission_1" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.update_alternate_contacts_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.control_tower_account_create_rule.arn
}

resource "aws_lambda_permission" "control_tower_account_create_lambda_permission_2" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.enable_security_hub_standards_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.control_tower_account_create_rule.arn
}

# ControlTower Account Update EventBridge Rule
resource "aws_cloudwatch_event_rule" "control_tower_account_update_rule" {
  event_pattern = jsonencode({
    source: [
      "aws.controltower"      
    ],
    detail-type = [
      "AWS Service Event via CloudTrail"
    ],
    detail = {
        "eventName": [
          "UpdateManagedAccount", 
        ],
        "serviceEventDetails": {
          "updateManagedAccountStatus": {
            "state": [
              "SUCCEEDED"
            ]
          }
        }
      }
  })
  is_enabled = true
}

# ControlTower Account Update EventBridge Rule target
resource "aws_cloudwatch_event_target" "control_tower_account_update_rule_target_1" {
  rule      = aws_cloudwatch_event_rule.control_tower_account_update_rule.name
  target_id = "ControlTowerAccountUpdateLambdaTarget"
  arn       = aws_lambda_function.update_alternate_contacts_lambda.arn
}

resource "aws_cloudwatch_event_target" "control_tower_account_update_rule_target_2" {
  rule      = aws_cloudwatch_event_rule.control_tower_account_update_rule.name
  target_id = "ControlTowerAccountUpdateLambdaTargetSecurityHub"
  arn       = aws_lambda_function.enable_security_hub_standards_lambda.arn
}

#ControlTower Update EventBridgeRule Target Invoke Permission
resource "aws_lambda_permission" "control_tower_account_update_lambda_permission_1" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.update_alternate_contacts_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.control_tower_account_update_rule.arn
}

resource "aws_lambda_permission" "control_tower_account_update_lambda_permission_2" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.enable_security_hub_standards_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.control_tower_account_update_rule.arn
}

# Lambda to Enable CIS Foundation Benchmark in member accounts
resource "aws_lambda_function" "enable_security_hub_standards_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_enable_securityhub_standard.zip"
  function_name = "platform_enable_securityhub_standard"
  role          = var.role_arn
  handler       = "platform_enable_securityhub_standard.lambda_handler"
  source_code_hash = data.archive_file.Enable-SecurityHub-Standards_lambda_zip.output_base64sha256
  runtime = "python3.8"
  timeout = 900
  memory_size = 128

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}