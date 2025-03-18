data "aws_iam_role" "orchestratorRole12B410FD" {
  name               = "Platform-Audit-SHARR-Rele-orchestratorRole12B410FD-${var.orchestratorrole_id}"
}
data "aws_lambda_function" "checkSSMDocState06AC440F" {
  function_name = "SO0111-SHARR-checkSSMDocState"
}

data "aws_lambda_function" "sendNotifications1367638A" {
  function_name = "SO0111-SHARR-sendNotifications"
}

data "aws_lambda_function" "getApprovalRequirementE7F50E54" {
    function_name = "SO0111-SHARR-getApprovalRequirement"
}

data "aws_lambda_function" "execAutomation5D89E251" {
  function_name = "SO0111-SHARR-execAutomation"
}

data "aws_lambda_function" "monitorSSMExecStateB496B8AF" {
  function_name = "SO0111-SHARR-monitorSSMExecState"
}

data "aws_cloudwatch_log_group" "OrchestratorLogsEncrypted072D6E38" {
  name = "SO0111-SHARR-Orchestrator"
}

resource "aws_sfn_state_machine" "sfn_state_machine" {
  name     = "SO0111-SHARR-Orchestrator"
  role_arn = data.aws_iam_role.orchestratorRole12B410FD.arn

  definition = <<EOF
  {
    "StartAt": "Get Finding Data from Input",
    "States": {
      "Get Finding Data from Input": {
        "Type": "Pass",
        "Comment": "Extract top-level data needed for remediation",
        "Parameters": {
          "EventType.$": "$.detail-type",
          "Findings.$": "$.detail.findings"
        },
        "Next": "Process Findings"
      },
      "Process Findings": {
        "Type": "Map",
        "Comment": "Process all findings in CloudWatch Event",
        "Next": "EOJ",
        "Parameters": {
          "Finding.$": "$$.Map.Item.Value",
          "EventType.$": "$.EventType"
        },
        "Iterator": {
          "StartAt": "Finding Workflow State NEW?",
          "States": {
            "Finding Workflow State NEW?": {
              "Type": "Choice",
              "Choices": [
                {
                  "Or": [
                    {
                      "Variable": "$.EventType",
                      "StringEquals": "Security Hub Findings - Custom Action"
                    },
                    {
                      "And": [
                        {
                          "Variable": "$.Finding.Workflow.Status",
                          "StringEquals": "NEW"
                        },
                        {
                          "Variable": "$.EventType",
                          "StringEquals": "Security Hub Findings - Imported"
                        }
                      ]
                    }
                  ],
                  "Next": "Get Remediation Approval Requirement"
                }
              ],
              "Default": "Finding Workflow State is not NEW"
            },
            "Finding Workflow State is not NEW": {
              "Type": "Pass",
              "Parameters": {
                "Notification": {
                  "Message.$": "States.Format('Finding Workflow State is not NEW ({}).', $.Finding.Workflow.Status)",
                  "State.$": "States.Format('NOTNEW')"
                },
                "EventType.$": "$.EventType",
                "Finding.$": "$.Finding"
              },
              "Next": "notify"
            },
            "notify": {
              "End": true,
              "Retry": [
                {
                  "ErrorEquals": [
                    "Lambda.ServiceException",
                    "Lambda.AWSLambdaException",
                    "Lambda.SdkClientException"
                  ],
                  "IntervalSeconds": 2,
                  "MaxAttempts": 6,
                  "BackoffRate": 2
                }
              ],
              "Type": "Task",
              "Comment": "Send notifications",
              "TimeoutSeconds": 300,
              "HeartbeatSeconds": 60,
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${data.aws_lambda_function.sendNotifications1367638A.arn}",
                "Payload.$": "$"
              }
            },
            "Automation Document is not Active": {
              "Type": "Pass",
              "Parameters": {
                "Notification": {
                  "Message.$": "States.Format('Automation Document ({}) is not active ({}) in the member account({}).', $.AutomationDocId, $.AutomationDocument.DocState, $.Finding.AwsAccountId)",
                  "State.$": "States.Format('REMEDIATIONNOTACTIVE')",
                  "updateSecHub": "yes"
                },
                "EventType.$": "$.EventType",
                "Finding.$": "$.Finding",
                "AccountId.$": "$.AutomationDocument.AccountId",
                "AutomationDocId.$": "$.AutomationDocument.AutomationDocId",
                "RemediationRole.$": "$.AutomationDocument.RemediationRole",
                "ControlId.$": "$.AutomationDocument.ControlId",
                "SecurityStandard.$": "$.AutomationDocument.SecurityStandard",
                "SecurityStandardVersion.$": "$.AutomationDocument.SecurityStandardVersion"
              },
              "Next": "notify"
            },
            "Automation Doc Active?": {
              "Type": "Choice",
              "Choices": [
                {
                  "Variable": "$.AutomationDocument.DocState",
                  "StringEquals": "ACTIVE",
                  "Next": "Execute Remediation"
                },
                {
                  "Variable": "$.AutomationDocument.DocState",
                  "StringEquals": "NOTACTIVE",
                  "Next": "Automation Document is not Active"
                },
                {
                  "Variable": "$.AutomationDocument.DocState",
                  "StringEquals": "NOTENABLED",
                  "Next": "Security Standard is not enabled"
                },
                {
                  "Variable": "$.AutomationDocument.DocState",
                  "StringEquals": "NOTFOUND",
                  "Next": "No Remediation for Control"
                }
              ],
              "Default": "check_ssm_doc_state Error"
            },
            "Get Automation Document State": {
              "Next": "Automation Doc Active?",
              "Retry": [
                {
                  "ErrorEquals": [
                    "Lambda.ServiceException",
                    "Lambda.AWSLambdaException",
                    "Lambda.SdkClientException"
                  ],
                  "IntervalSeconds": 2,
                  "MaxAttempts": 6,
                  "BackoffRate": 2
                }
              ],
              "Catch": [
                {
                  "ErrorEquals": [
                    "States.ALL"
                  ],
                  "Next": "Orchestrator Failed"
                }
              ],
              "Type": "Task",
              "Comment": "Get the status of the remediation automation document in the target account",
              "TimeoutSeconds": 60,
              "ResultPath": "$.AutomationDocument",
              "ResultSelector": {
                "DocState.$": "$.Payload.status",
                "Message.$": "$.Payload.message",
                "SecurityStandard.$": "$.Payload.securitystandard",
                "SecurityStandardVersion.$": "$.Payload.securitystandardversion",
                "SecurityStandardSupported.$": "$.Payload.standardsupported",
                "ControlId.$": "$.Payload.controlid",
                "AccountId.$": "$.Payload.accountid",
                "RemediationRole.$": "$.Payload.remediationrole",
                "AutomationDocId.$": "$.Payload.automationdocid",
                "ResourceRegion.$": "$.Payload.resourceregion"
              },
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${data.aws_lambda_function.checkSSMDocState06AC440F.arn}",
                "Payload.$": "$"
              }
            },
            "Get Remediation Approval Requirement": {
              "Next": "Get Automation Document State",
              "Retry": [
                {
                  "ErrorEquals": [
                    "Lambda.ServiceException",
                    "Lambda.AWSLambdaException",
                    "Lambda.SdkClientException"
                  ],
                  "IntervalSeconds": 2,
                  "MaxAttempts": 6,
                  "BackoffRate": 2
                }
              ],
              "Catch": [
                {
                  "ErrorEquals": [
                    "States.ALL"
                  ],
                  "Next": "Orchestrator Failed"
                }
              ],
              "Type": "Task",
              "Comment": "Determine whether the selected remediation requires manual approval",
              "TimeoutSeconds": 300,
              "ResultPath": "$.Workflow",
              "ResultSelector": {
                "WorkflowDocument.$": "$.Payload.workflowdoc",
                "WorkflowAccount.$": "$.Payload.workflowaccount",
                "WorkflowRole.$": "$.Payload.workflowrole",
                "WorkflowConfig.$": "$.Payload.workflow_data"
              },
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${data.aws_lambda_function.getApprovalRequirementE7F50E54.arn}",
                "Payload.$": "$"
              }
            },
            "Orchestrator Failed": {
              "Type": "Pass",
              "Parameters": {
                "Notification": {
                  "Message.$": "States.Format('Orchestrator failed: {}', $.Error)",
                  "State.$": "States.Format('LAMBDAERROR')",
                  "Details.$": "States.Format('Cause: {}', $.Cause)"
                },
                "Payload.$": "$"
              },
              "Next": "notify"
            },
            "Execute Remediation": {
              "Next": "Remediation Queued",
              "Retry": [
                {
                  "ErrorEquals": [
                    "Lambda.ServiceException",
                    "Lambda.AWSLambdaException",
                    "Lambda.SdkClientException"
                  ],
                  "IntervalSeconds": 2,
                  "MaxAttempts": 6,
                  "BackoffRate": 2
                }
              ],
              "Catch": [
                {
                  "ErrorEquals": [
                    "States.ALL"
                  ],
                  "Next": "Orchestrator Failed"
                }
              ],
              "Type": "Task",
              "Comment": "Execute the SSM Automation Document in the target account",
              "TimeoutSeconds": 300,
              "HeartbeatSeconds": 60,
              "ResultPath": "$.SSMExecution",
              "ResultSelector": {
                "ExecState.$": "$.Payload.status",
                "Message.$": "$.Payload.message",
                "ExecId.$": "$.Payload.executionid",
                "Account.$": "$.Payload.executionaccount",
                "Region.$": "$.Payload.executionregion"
              },
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${data.aws_lambda_function.execAutomation5D89E251.arn}",
                "Payload.$": "$"
              }
            },
            "Remediation Queued": {
              "Type": "Pass",
              "Comment": "Set parameters for notification",
              "Parameters": {
                "EventType.$": "$.EventType",
                "Finding.$": "$.Finding",
                "AutomationDocument.$": "$.AutomationDocument",
                "SSMExecution.$": "$.SSMExecution",
                "Notification": {
                  "Message.$": "States.Format('Remediation queued for {} control {} in account {}', $.AutomationDocument.SecurityStandard, $.AutomationDocument.ControlId, $.AutomationDocument.AccountId)",
                  "State.$": "States.Format('QUEUED')",
                  "ExecId.$": "$.SSMExecution.ExecId"
                }
              },
              "Next": "Queued Notification"
            },
            "Queued Notification": {
              "Next": "execMonitor",
              "Retry": [
                {
                  "ErrorEquals": [
                    "Lambda.ServiceException",
                    "Lambda.AWSLambdaException",
                    "Lambda.SdkClientException"
                  ],
                  "IntervalSeconds": 2,
                  "MaxAttempts": 6,
                  "BackoffRate": 2
                }
              ],
              "Type": "Task",
              "Comment": "Send notification that a remediation has queued",
              "TimeoutSeconds": 300,
              "HeartbeatSeconds": 60,
              "ResultPath": "$.notificationResult",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${data.aws_lambda_function.sendNotifications1367638A.arn}",
                "Payload.$": "$"
              }
            },
            "execMonitor": {
              "Next": "Remediation completed?",
              "Retry": [
                {
                  "ErrorEquals": [
                    "Lambda.ServiceException",
                    "Lambda.AWSLambdaException",
                    "Lambda.SdkClientException"
                  ],
                  "IntervalSeconds": 2,
                  "MaxAttempts": 6,
                  "BackoffRate": 2
                }
              ],
              "Catch": [
                {
                  "ErrorEquals": [
                    "States.ALL"
                  ],
                  "Next": "Orchestrator Failed"
                }
              ],
              "Type": "Task",
              "Comment": "Monitor the remediation execution until done",
              "TimeoutSeconds": 300,
              "HeartbeatSeconds": 60,
              "ResultPath": "$.Remediation",
              "ResultSelector": {
                "ExecState.$": "$.Payload.status",
                "ExecId.$": "$.Payload.executionid",
                "RemediationState.$": "$.Payload.remediation_status",
                "Message.$": "$.Payload.message",
                "LogData.$": "$.Payload.logdata",
                "AffectedObject.$": "$.Payload.affected_object"
              },
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${data.aws_lambda_function.monitorSSMExecStateB496B8AF.arn}",
                "Payload.$": "$"
              }
            },
            "Wait for Remediation": {
              "Type": "Wait",
              "Seconds": 15,
              "Next": "execMonitor"
            },
            "Remediation completed?": {
              "Type": "Choice",
              "Choices": [
                {
                  "Variable": "$.Remediation.RemediationState",
                  "StringEquals": "Failed",
                  "Next": "Remediation Failed"
                },
                {
                  "Variable": "$.Remediation.ExecState",
                  "StringEquals": "Success",
                  "Next": "Remediation Succeeded"
                },
                {
                  "Variable": "$.Remediation.ExecState",
                  "StringEquals": "TimedOut",
                  "Next": "Remediation Failed"
                },
                {
                  "Variable": "$.Remediation.ExecState",
                  "StringEquals": "Cancelling",
                  "Next": "Remediation Failed"
                },
                {
                  "Variable": "$.Remediation.ExecState",
                  "StringEquals": "Cancelled",
                  "Next": "Remediation Failed"
                },
                {
                  "Variable": "$.Remediation.ExecState",
                  "StringEquals": "Failed",
                  "Next": "Remediation Failed"
                }
              ],
              "Default": "Wait for Remediation"
            },
            "Remediation Failed": {
              "Type": "Pass",
              "Comment": "Set parameters for notification",
              "Parameters": {
                "EventType.$": "$.EventType",
                "Finding.$": "$.Finding",
                "SSMExecution.$": "$.SSMExecution",
                "AutomationDocument.$": "$.AutomationDocument",
                "Notification": {
                  "Message.$": "States.Format('Remediation failed for {} control {} in account {}: {}', $.AutomationDocument.SecurityStandard, $.AutomationDocument.ControlId, $.AutomationDocument.AccountId, $.Remediation.Message)",
                  "State.$": "$.Remediation.ExecState",
                  "Details.$": "$.Remediation.LogData",
                  "ExecId.$": "$.Remediation.ExecId",
                  "AffectedObject.$": "$.Remediation.AffectedObject"
                }
              },
              "Next": "notify"
            },
            "Remediation Succeeded": {
              "Type": "Pass",
              "Comment": "Set parameters for notification",
              "Parameters": {
                "EventType.$": "$.EventType",
                "Finding.$": "$.Finding",
                "AccountId.$": "$.AutomationDocument.AccountId",
                "AutomationDocId.$": "$.AutomationDocument.AutomationDocId",
                "RemediationRole.$": "$.AutomationDocument.RemediationRole",
                "ControlId.$": "$.AutomationDocument.ControlId",
                "SecurityStandard.$": "$.AutomationDocument.SecurityStandard",
                "SecurityStandardVersion.$": "$.AutomationDocument.SecurityStandardVersion",
                "Notification": {
                  "Message.$": "States.Format('Remediation succeeded for {} control {} in account {}: {}', $.AutomationDocument.SecurityStandard, $.AutomationDocument.ControlId, $.AutomationDocument.AccountId, $.Remediation.Message)",
                  "State.$": "States.Format('SUCCESS')",
                  "Details.$": "$.Remediation.LogData",
                  "ExecId.$": "$.Remediation.ExecId",
                  "AffectedObject.$": "$.Remediation.AffectedObject"
                }
              },
              "Next": "notify"
            },
            "check_ssm_doc_state Error": {
              "Type": "Pass",
              "Parameters": {
                "Notification": {
                  "Message.$": "States.Format('check_ssm_doc_state returned an error: {}', $.AutomationDocument.Message)",
                  "State.$": "States.Format('LAMBDAERROR')"
                },
                "EventType.$": "$.EventType",
                "Finding.$": "$.Finding"
              },
              "Next": "notify"
            },
            "Security Standard is not enabled": {
              "Type": "Pass",
              "Parameters": {
                "Notification": {
                  "Message.$": "States.Format('Security Standard ({}) v{} is not enabled.', $.AutomationDocument.SecurityStandard, $.AutomationDocument.SecurityStandardVersion)",
                  "State.$": "States.Format('STANDARDNOTENABLED')",
                  "updateSecHub": "yes"
                },
                "EventType.$": "$.EventType",
                "Finding.$": "$.Finding",
                "AccountId.$": "$.AutomationDocument.AccountId",
                "AutomationDocId.$": "$.AutomationDocument.AutomationDocId",
                "RemediationRole.$": "$.AutomationDocument.RemediationRole",
                "ControlId.$": "$.AutomationDocument.ControlId",
                "SecurityStandard.$": "$.AutomationDocument.SecurityStandard",
                "SecurityStandardVersion.$": "$.AutomationDocument.SecurityStandardVersion"
              },
              "Next": "notify"
            },
            "No Remediation for Control": {
              "Type": "Pass",
              "Parameters": {
                "Notification": {
                  "Message.$": "States.Format('Security Standard {} v{} control {} has no automated remediation.', $.AutomationDocument.SecurityStandard, $.AutomationDocument.SecurityStandardVersion, $.AutomationDocument.ControlId)",
                  "State.$": "States.Format('NOREMEDIATION')",
                  "updateSecHub": "yes"
                },
                "EventType.$": "$.EventType",
                "Finding.$": "$.Finding",
                "AccountId.$": "$.AutomationDocument.AccountId",
                "AutomationDocId.$": "$.AutomationDocument.AutomationDocId",
                "RemediationRole.$": "$.AutomationDocument.RemediationRole",
                "ControlId.$": "$.AutomationDocument.ControlId",
                "SecurityStandard.$": "$.AutomationDocument.SecurityStandard",
                "SecurityStandardVersion.$": "$.AutomationDocument.SecurityStandardVersion"
              },
              "Next": "notify"
            }
          }
        },
        "ItemsPath": "$.Findings"
      },
      "EOJ": {
        "Type": "Pass",
        "Comment": "END-OF-JOB",
        "End": true
      }
    },
    "TimeoutSeconds": 900
}
EOF
logging_configuration {
    log_destination        = "arn:aws:logs:us-east-1:${var.account_id}:log-group:SO0111-SHARR-Orchestrator:*"
    include_execution_data = true
    level                  = "ALL"
  }
depends_on = [data.aws_cloudwatch_log_group.OrchestratorLogsEncrypted072D6E38, data.aws_iam_role.orchestratorRole12B410FD ]
}
