resource "aws_iam_role" "platform_audit_admin_role" {
  name        = "Platform_AuditAdmin"
  description = "Role to assume in Audit Account to perform actions"
  assume_role_policy = jsonencode({
    "Version" : "2008-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : [
            "lambda.amazonaws.com",
            "s3.amazonaws.com"
          ]
        },
        "Action" : "sts:AssumeRole",
      }
    ]
  })
  managed_policy_arns = [aws_iam_policy.policy_platform_audit_admin.arn]
  tags = {
    platform_donotdelete = "yes"
  }
}

resource "aws_iam_role" "platform_service_cloudhealth_role" {
  name        = "platform_service_cloudhealth"
  description = "Role to assume in CloudHealth Actions"
  assume_role_policy = jsonencode({
    "Version" : "2008-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : "arn:aws:iam::${var.platform_cloudhealth_account}:root"
        },
        "Action" : "sts:AssumeRole",
        "Condition" : {
          "StringEquals" : {
            "sts:ExternalId" : var.platform_cloudhealth_external_id
          }
        }
      }
    ]
  })
  managed_policy_arns = [aws_iam_policy.policy_platform_cloud_health_policy.arn]
  tags = {
    platform_donotdelete = "yes"
  }
}

resource "aws_iam_role" "platform_ServiceNow_ITOM_Discovery_Child_Role" {
  name = "ServiceNow_ITOM_Discovery_Child_Role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ec2.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : "arn:aws:iam::247990085610:role/ServiceNowEC2Role"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
  managed_policy_arns = [aws_iam_policy.policy_platform_ITOM_Discovery_Child_Policy.arn]
}

resource "aws_iam_instance_profile" "platform_ServiceNow_ITOM_Discovery_Child_InstanceProfile" {
  name = var.service_now_itom_discovery_child_instance_profile
  role = aws_iam_role.platform_ServiceNow_ITOM_Discovery_Child_Role.name
}

resource "aws_iam_role" "platform_tfc_audit_role" {
  name        = "platform_tfc_audit_role"
  description = "Role to assume by TFC in Audit Account to perform actions"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          #type = "Federated"
          Federated = "arn:aws:iam::${var.account_id}:oidc-provider/app.terraform.io"
        },
        "Action" : "sts:AssumeRoleWithWebIdentity",
        "Condition" : {
          "StringEquals" : {
            "app.terraform.io:aud" : "aws.workload.identity"
          },
          "StringLike" : {
            "app.terraform.io:sub" : "organization:ecp-shell-prod:project:*:workspace:*:run_phase:*"
          }
        }
      }
    ]
  })
  managed_policy_arns = [aws_iam_policy.policy_platform_audit_admin.arn]
   inline_policy {
    name = "sharr_tfc_permissions"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
             "states:*",
             "kms:*",
             "ssm:*",
             "sns:*"

          ]
          Resource = "*"
          Effect   = "Allow"
        }
      ]
    })
  }
  tags = {
    platform_donotdelete = "yes"
  }
}


resource "aws_iam_role" "platform_pytest" {
  name        = "platform_pytest"
  description = "This role will be used by github actions for running pytest in this account."
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          Federated = "arn:aws:iam::${var.account_id}:oidc-provider/token.actions.githubusercontent.com"
        },
        "Action" : "sts:AssumeRoleWithWebIdentity",
        "Condition" : {
          "StringEquals" : {
            "token.actions.githubusercontent.com:aud" : "sts.amazonaws.com"
          },
          "StringLike" : {
            "token.actions.githubusercontent.com:sub" : "repo:sede-x/AWS-at-Shell-Platform-Engineering:*"
          }
        }
      }
    ]
  })
  managed_policy_arns = [aws_iam_policy.policy_platform_audit_admin.arn]
  tags = {
    platform_donotdelete = "yes"
  }
}

#################################Sharr##############################################

data "aws_kms_key" "sharr_key" {
  key_id = "alias/SO0111-SHARR-Key"

}
resource "aws_iam_role" "orchestratorRole46A9F242" {
  name        = "SO0111-SHARR-Orchestrator-Admin"
  description = "Lambda role to allow cross account read-only SHARR orchestrator functions"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          Service = "lambda.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
  inline_policy {
    name = "CIS41EventsRuleRoleDefaultPolicy9D41E873"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = "states:StartExecution",
          Resource = "arn:aws:states:us-east-1:${var.account_id}:stateMachine:SO0111-SHARR-Orchestrator"
          Effect   = "Allow"
        }
      ]
    })
  }

  inline_policy {
    name = "SO0111-SHARR_Orchestrator"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ]
          Resource = "*"
          Effect   = "Allow"
        },
        {
          Action = [
            "ssm:GetParameter",
            "ssm:GetParameters",
            "ssm:PutParameter"
          ]
          Resource = "arn:aws:ssm:*:${var.account_id}:parameter/Solutions/SO0111/*"
          Effect   = "Allow"
        },
        {
          Action = "sts:AssumeRole"
          Resource = [
            "arn:aws:iam::*:role/SO0111-SHARR-Orchestrator-Member",
            "arn:aws:iam::${var.payer_account_id}:role/platform-sharr-exception-ec2-13-role",
          ]
          Effect = "Allow"
        },
        {
          Action   = "organizations:ListTagsForResource"
          Resource = "*"
          Effect   = "Allow"
        },
        {
          Action   = "securityhub:BatchUpdateFindings"
          Resource = "*"
          Effect   = "Allow"
        }
      ]
    }
    )
  }
  inline_policy {
    name = "SO0111-SHARR_Orchestrator_Notifier"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ]
          Resource = "*"
          Effect   = "Allow"
        },
        {
          Action   = "securityhub:BatchUpdateFindings"
          Resource = "*"
          Effect   = "Allow"
        },
        {
          Action = [
            "ssm:GetParameter",
            "ssm:PutParameter"
          ]
          Resource = "arn:aws:ssm:us-east-1:${var.account_id}:parameter/Solutions/SO0111/*"
          Effect   = "Allow"
        },
        {
          Action = [
            "kms:Encrypt",
            "kms:Decrypt",
            "kms:GenerateDataKey"
          ]
          Resource = data.aws_kms_key.sharr_key.arn
          Effect   = "Allow"
        },
        {
          Action   = "sns:Publish"
          Resource = "arn:aws:sns:us-east-1:${var.account_id}:SO0111-SHARR_Topic"
          Effect   = "Allow"
        }
      ]
    })
  }
}

resource "aws_iam_role" "notifyRole40298120" {
  name        = "Platform-Audit-SHARR-Releases-notifyRole40298120-${var.notifyRole_id}"
  description = "Lambda role to perform notification and logging from orchestrator step function"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          Service = "lambda.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
  inline_policy {
    name = "SO0111-SHARR_Orchestrator_Notifier"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ]
          Effect   = "Allow"
          Resource = "*"
          
        },
        {
          Action   = "securityhub:BatchUpdateFindings"
          Effect   = "Allow"
          Resource = "*"
        },
        {
          Action = [
            "ssm:GetParameter",
            "ssm:PutParameter"
          ]
          Effect   = "Allow"
          Resource = "arn:aws:ssm:us-east-1:${var.account_id}:parameter/Solutions/SO0111/*"
        },
        {
          Action = [
            "kms:Encrypt",
            "kms:Decrypt",
            "kms:GenerateDataKey"
          ]
          Effect   = "Allow"
          Resource = data.aws_kms_key.sharr_key.arn
        },
        {
          Action   = "sns:Publish"
          Effect   = "Allow"
          Resource = "arn:aws:sns:us-east-1:${var.account_id}:SO0111-SHARR_Topic"
        }
      ]
    })
  }
}

resource "aws_iam_role" "createCustomActionRoleF0047414" {
  name        = "Platform-Audit-SHARR-Rele-createCustomActionRoleF0-${var.customactionrole_id}"
  description = "Lambda role to allow creation of Security Hub Custom Actions"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          Service = "lambda.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
  inline_policy {
    name = "SO0111-SHARR_Custom_Action"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
            "cloudwatch:PutMetricData"
          ]
          Effect   = "Allow"
          Resource = "*"
        },
        {
          Action = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ]
          Effect   = "Allow"
          Resource = "*"
        },
        {
          Action = [
            "securityhub:CreateActionTarget",
            "securityhub:DeleteActionTarget"
          ]
          Effect   = "Allow"
          Resource = "*"
        },
        {
          Action = [
            "ssm:GetParameter",
            "ssm:GetParameters",
            "ssm:PutParameter"
          ]
          Effect   = "Allow"
          Resource = "arn:aws:ssm:*:${var.account_id}:parameter/Solutions/SO0111/*"
      }]
    })
  }
}

resource "aws_iam_role" "orchestratorRole12B410FD" {
  name = "Platform-Audit-SHARR-Rele-orchestratorRole12B410FD-${var.orchestratorrole_id}"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          Service = "states.us-east-1.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })

  inline_policy {
    name = "BasePolicy"

    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
            "logs:CreateLogDelivery",
            "logs:GetLogDelivery",
            "logs:UpdateLogDelivery",
            "logs:DeleteLogDelivery",
            "logs:ListLogDeliveries",
            "logs:PutResourcePolicy",
            "logs:DescribeResourcePolicies",
            "logs:DescribeLogGroups"
          ]
          Effect   = "Allow"
          Resource = "*"
        },
        {
          Action = "lambda:InvokeFunction"
          Effect = "Allow"
          Resource = [
            "arn:aws:lambda:us-east-1:${var.account_id}:function:SO0111-SHARR-checkSSMDocState",
            "arn:aws:lambda:us-east-1:${var.account_id}:function:SO0111-SHARR-execAutomation",
            "arn:aws:lambda:us-east-1:${var.account_id}:function:SO0111-SHARR-monitorSSMExecState",
            "arn:aws:lambda:us-east-1:${var.account_id}:function:SO0111-SHARR-sendNotifications",
            "arn:aws:lambda:us-east-1:${var.account_id}:function:SO0111-SHARR-getApprovalRequirement"
          ]
        },
        {
          Action = [
            "kms:Encrypt",
            "kms:Decrypt",
            "kms:GenerateDataKey"
          ]
          Effect   = "Allow"
          Resource = "arn:aws:kms:us-east-1:${var.account_id}:alias/SO0111-SHARR-Key"
        },
      ]
    })
  }
}


resource "aws_iam_role" "RemediateWithSharrEventsRuleRole4BE0B6FF" {
  name = "Platform-Audit-SHARR-Rele-RemediateWithSharrEvents-${var.remediatewithsharreventsrule_id}"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          Service = "events.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })

  inline_policy {
    name = "RemediateWithSharrEventsRuleRoleDefaultPolicy44783695"

    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
            "states:StartExecution"
          ]
          Effect   = "Allow"
          Resource = "arn:aws:states:us-east-1:${var.account_id}:stateMachine:SO0111-SHARR-Orchestrator"
        }
      ]
    })
  }
}

resource "aws_iam_role" "CIS41EventsRuleRoleAFBA33A3" {
  name = "Platform-Audit-SHARR-Rele-CIS41EventsRuleRoleAFBA3-${var.cis41eventsrulerole_id}"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          Service = "events.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })

  inline_policy {
    name = "CIS41EventsRuleRoleDefaultPolicy9D41E873"

    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
            "states:StartExecution"
          ]
          Effect   = "Allow"
          Resource = "arn:aws:states:us-east-1:${var.account_id}:stateMachine:SO0111-SHARR-Orchestrator"
        }
      ]
    })
  }
}


resource "aws_iam_role" "SecHubIAM9HandlingLambdaRole" {
  name        = "platform_SecHubIAM9HandlingLambdaRole"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          Service = [
                  "lambda.amazonaws.com",
                  "securityhub.amazonaws.com"
          ]
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
  inline_policy {
    name = "platform_SecHubIAM9HandlingLambdaRolePolicy"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
            "securityhub:BatchUpdateFindings",
            "securityhub:GetFindings",
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ]
          Effect   = "Allow"
          Resource = "*"
          
        },
        {
          Action   = "organizations:DescribeAccount"
          Effect   = "Allow"
          Resource = "*"
        }
      ]
    })
  }
  tags = {
    platform_donotdelete = "yes"
  }
}

data "aws_lambda_function" "SecHubIAM9HandlingLambdaFunction" {
  function_name = "platform_sechub_iam9_handling_lambda_function"
}

resource "aws_iam_role" "SecHubIAM9HandlingSchedularRole" {
  name        = "platform_SecHubIAM9HandlingSchedularRole"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          Service = [
                  "scheduler.amazonaws.com"
          ]
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
  inline_policy {
    name = "platform_SecHubIAM9HandlingSchedularRolePolicy"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
            "lambda:InvokeFunction",
          ]
          Effect   = "Allow"
          Resource = data.aws_lambda_function.SecHubIAM9HandlingLambdaFunction.arn
          
        }
      ]
    })
  }
  tags = {
    platform_donotdelete = "yes"
  }
}