data "aws_iam_role" "orchestratorRole46A9F242" {
  name = "SO0111-SHARR-Orchestrator-Admin"
}

data "aws_iam_role" "notifyRole40298120" {
  name = "Platform-Audit-SHARR-Releases-notifyRole40298120-${var.notifyRole_id}"
}

data "aws_iam_role" "createCustomActionRoleF0047414" {
  name                = "Platform-Audit-SHARR-Rele-createCustomActionRoleF0-${var.customactionrole_id}"
}

resource "aws_lambda_layer_version" "SharrLambdaLayer5BF8F147" {
    layer_name = "SharrLambdaLayer5BF8F147"
    description = "SO0111 SHARR Common functions used by the solution"
    s3_bucket = "solutions-us-east-1"
    s3_key = "aws-security-hub-automated-response-and-remediation/v2.0.0/lambda/layer.zip"
    compatible_runtimes = ["python3.9"]
    license_info = "https://www.apache.org/licenses/LICENSE-2.0"
    compatible_architectures = []
}

resource "aws_lambda_function" "checkSSMDocState06AC440F" {
  s3_bucket = "solutions-us-east-1"
  s3_key = "aws-security-hub-automated-response-and-remediation/v2.0.0/lambda/check_ssm_doc_state.py.zip"
  function_name = "SO0111-SHARR-checkSSMDocState"
  description = "Checks the status of an SSM Automation Document in the target account"
  role          = data.aws_iam_role.orchestratorRole46A9F242.arn
  handler       = "check_ssm_doc_state.lambda_handler"
  memory_size = 256
  layers = [aws_lambda_layer_version.SharrLambdaLayer5BF8F147.arn]
  runtime = "python3.9"

  timeout = 600
  depends_on = [data.aws_iam_role.orchestratorRole46A9F242]

  environment {
    variables = {
      log_level = "info"
      AWS_PARTITION  = "aws"
      SOLUTION_ID = "SO0111"
      SOLUTION_VERSION = "v2.0.0"
    }
  }
}

resource "aws_lambda_function" "getApprovalRequirementE7F50E54" {
  s3_bucket = "solutions-us-east-1"
  s3_key = "aws-security-hub-automated-response-and-remediation/v2.0.0/lambda/get_approval_requirement.py.zip"
  function_name = "SO0111-SHARR-getApprovalRequirement"
  description = "Determines if a manual approval is required for remediation"
  role          = data.aws_iam_role.orchestratorRole46A9F242.arn
  handler       = "get_approval_requirement.lambda_handler"
  memory_size = 256
  layers = [aws_lambda_layer_version.SharrLambdaLayer5BF8F147.arn]
  runtime = "python3.9"

  timeout = 600
  depends_on = [data.aws_iam_role.orchestratorRole46A9F242]

  environment {
    variables = {
      log_level = "info"
      AWS_PARTITION  = "aws"
      SOLUTION_ID = "SO0111"
      SOLUTION_VERSION = "v2.0.0"
      WORKFLOW_RUNBOOK = ""
    }
  }
}


resource "aws_lambda_function" "execAutomation5D89E251" {
  s3_bucket = "solutions-us-east-1"
  s3_key = "aws-security-hub-automated-response-and-remediation/v2.0.0/lambda/exec_ssm_doc.py.zip"
  function_name = "SO0111-SHARR-execAutomation"
  description = "Executes an SSM Automation Document in a target account"
  role          = data.aws_iam_role.orchestratorRole46A9F242.arn
  handler       = "exec_ssm_doc.lambda_handler"
  memory_size = 256
  layers = [aws_lambda_layer_version.SharrLambdaLayer5BF8F147.arn]
  runtime = "python3.9"

  timeout = 600
  depends_on = [data.aws_iam_role.orchestratorRole46A9F242]

  environment {
    variables = {
      log_level = "info"
      AWS_PARTITION  = "aws"
      SOLUTION_ID = "SO0111"
      SOLUTION_VERSION = "v2.0.0"
    }
  }
}


resource "aws_lambda_function" "monitorSSMExecStateB496B8AF" {
  s3_bucket = "solutions-us-east-1"
  s3_key = "aws-security-hub-automated-response-and-remediation/v2.0.0/lambda/check_ssm_execution.py.zip"
  function_name = "SO0111-SHARR-monitorSSMExecState"
  description = "Checks the status of an SSM automation document execution"
  role          = data.aws_iam_role.orchestratorRole46A9F242.arn
  handler       = "check_ssm_execution.lambda_handler"
  memory_size = 256
  layers = [aws_lambda_layer_version.SharrLambdaLayer5BF8F147.arn]
  runtime = "python3.9"

  timeout = 600
  depends_on = [data.aws_iam_role.orchestratorRole46A9F242]

  environment {
    variables = {
      log_level = "info"
      AWS_PARTITION  = "aws"
      SOLUTION_ID = "SO0111"
      SOLUTION_VERSION = "v2.0.0"
    }
  }
}

resource "aws_lambda_function" "sendNotifications1367638A" {
  s3_bucket = "solutions-us-east-1"
  s3_key = "aws-security-hub-automated-response-and-remediation/v2.0.0/lambda/send_notifications.py.zip"
  function_name = "SO0111-SHARR-sendNotifications"
  description = "Sends notifications and log messages"
  role          = data.aws_iam_role.notifyRole40298120.arn
  handler       = "send_notifications.lambda_handler"
  memory_size = 256
  layers = [aws_lambda_layer_version.SharrLambdaLayer5BF8F147.arn]
  runtime = "python3.9"

  timeout = 600
  depends_on = [data.aws_iam_role.notifyRole40298120]

  environment {
    variables = {
      log_level = "info"
      AWS_PARTITION  = "aws"
      SOLUTION_ID = "SO0111"
      SOLUTION_VERSION = "v2.0.0"
    }
  }
}


resource "aws_lambda_function" "CreateCustomActionE7A973F5" {
  s3_bucket = "solutions-us-east-1"
  s3_key = "aws-security-hub-automated-response-and-remediation/v2.0.0/lambda/action_target_provider.zip"
  function_name = "SO0111-SHARR-CustomAction"
  description = "Custom resource to create an action target in Security Hub"
  role          = data.aws_iam_role.createCustomActionRoleF0047414.arn
  handler       = "action_target_provider.lambda_handler"
  memory_size = 256
  layers = [aws_lambda_layer_version.SharrLambdaLayer5BF8F147.arn]
  runtime = "python3.9"

  timeout = 600
  depends_on = [data.aws_iam_role.createCustomActionRoleF0047414]

  environment {
    variables = {
      log_level = "info"
      AWS_PARTITION  = "aws"
      SOLUTION_ID = "SO0111"
      SOLUTION_VERSION = "v2.0.0"
      sendAnonymousMetrics = "Yes"
    }
  }
}


data "archive_file" "lambda1" {
  type        = "zip"
  source_file = "${path.module}/platform_sharr_exception_ec2_13.py"
  output_path = "${path.module}/platform_sharr_exception.zip"
}
data "aws_sfn_state_machine" "sfn_state_machine" {
  name     = "SO0111-SHARR-Orchestrator"
}
resource "aws_lambda_function" "Ec213ExceptionLambdaFunction" {
  filename      = data.archive_file.lambda1.output_path
  function_name = "platform_sharr_exception_ec2_13"
  description = "Lambda function to handle tag-based exception for open SSH/RDP port which is EC2.13 control in Security Hub"
  role          = data.aws_iam_role.orchestratorRole46A9F242.arn
  handler       = "platform_sharr_exception_ec2_13.lambda_handler"
  memory_size = 128
  source_code_hash = data.archive_file.lambda1.output_base64sha256

  runtime = "python3.10"

  timeout = 600

  environment {
    variables = {
      EXCEPTION_DDB_TABLE = "platform_EC213ExceptionTable"
      EXCEPTION_TAG_KEY = "port_exception"
      EXCEPTION_TAG_VALUE = "yes"
      PAYER_ACCOUNT_ID = var.payer_account_id
      STEP_FUNCTION_ARN =  data.aws_sfn_state_machine.sfn_state_machine.arn
    }
  }
}

data "aws_kms_key" "sharr_key" {
   key_id  = "alias/SO0111-SHARR-Key"
  
}
resource "aws_cloudwatch_log_group" "OrchestratorLogsEncrypted072D6E38" {
  name = "SO0111-SHARR-Orchestrator"
  retention_in_days = 365
  kms_key_id = data.aws_kms_key.sharr_key.arn
}


resource "aws_cloudwatch_event_rule" "RemediateWithSharrRemediateCustomAction40B496D2" {
  name        = "Remediate_with_SHARR_CustomAction"
  description = "Remediate with ASR"
  is_enabled = true
  event_pattern = jsonencode({
    source = ["aws.securityhub"]
    detail-type = [
      "Security Hub Findings - Custom Action"]
    resources = ["arn:aws:securityhub:us-east-1:${var.account_id}:action/custom/ASRRemediation"]
    detail = {
      findings = {
        Compliance = {
          Status =["FAILED", "WARNING"]
        }
      }
    }
    
  })
}

data "aws_iam_role" "RemediateWithSharrEventsRuleRole4BE0B6FF" {
  name               = "Platform-Audit-SHARR-Rele-RemediateWithSharrEvents-${var.remediatewithsharreventsrule_id}"
}

resource "aws_cloudwatch_event_target" "RemediateWithSharrRemediateCustomAction40B496D2" {
  rule      = aws_cloudwatch_event_rule.RemediateWithSharrRemediateCustomAction40B496D2.name
  target_id = "Target0"
  arn       = data.aws_sfn_state_machine.sfn_state_machine.arn
  role_arn  = data.aws_iam_role.RemediateWithSharrEventsRuleRole4BE0B6FF.arn
}

resource "aws_cloudwatch_event_rule" "CIS41AutoEventRuleABBCCC9F" {
  name        = "CIS_1.2.0_4.1_AutoTrigger"
  description = "Remediate CIS 1.2.0 4.1 automatic remediation trigger event rule."
  is_enabled = true
  event_pattern = jsonencode({
    source = ["aws.securityhub"]
    detail-type = ["Security Hub Findings - Imported"]
    detail = {
      findings = {
        Compliance = {
          Status =["FAILED", "WARNING"]
        },
        GeneratorId = ["arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.2.0/rule/4.1"],
        Workflow = {
          Status = ["NEW"]
        },
        RecordState =  ["ACTIVE"]
      }
    }
    
  })
}

resource "aws_cloudwatch_event_target" "CIS41AutoEventRuleABBCCC9F" {
  rule      = aws_cloudwatch_event_rule.CIS41AutoEventRuleABBCCC9F.name
  target_id = "Target0"
  arn       = aws_lambda_function.Ec213ExceptionLambdaFunction.arn
}

resource "aws_lambda_permission" "CIS41AutoEventRuleABBCCC9FLambdaPermission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.Ec213ExceptionLambdaFunction.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.CIS41AutoEventRuleABBCCC9F.arn
  statement_id = var.CIS41AutoEventRule_statement_id
}

resource "aws_cloudwatch_event_rule" "CIS42AutoEventRule8BF03E8E" {
  name        = "CIS_1.2.0_4.2_AutoTrigger"
  description = "Remediate CIS 1.2.0 4.2 automatic remediation trigger event rule."
  is_enabled = true
  event_pattern = jsonencode({
    source = ["aws.securityhub"]
    detail-type = ["Security Hub Findings - Imported"]
    detail = {
      findings = {
        Compliance = {
          Status =["FAILED", "WARNING"]
        },
        GeneratorId = ["arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.2.0/rule/4.2"],
        Workflow = {
          Status = ["NEW"]
        },
        RecordState =  ["ACTIVE"]
      }
    }
    
  })
}

resource "aws_cloudwatch_event_target" "CIS42AutoEventRule8BF03E8E" {
  rule      = aws_cloudwatch_event_rule.CIS42AutoEventRule8BF03E8E.name
  target_id = "Target0"
  arn       = aws_lambda_function.Ec213ExceptionLambdaFunction.arn
}


resource "aws_lambda_permission" "CIS42AutoEventRule8BF03E8ELambdaPermission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.Ec213ExceptionLambdaFunction.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.CIS42AutoEventRule8BF03E8E.arn
  statement_id = var.CIS42AutoEventRule_statement_id
}

resource "aws_cloudwatch_event_rule" "SCEC213AutoEventRule8D6D5712" {
  name        = "SC_2.0.0_EC2.13_AutoTrigger"
  description = "Remediate SC 2.0.0 EC2.13 automatic remediation trigger event rule."
  is_enabled = true
  event_pattern = jsonencode({
    source = ["aws.securityhub"]
    detail-type = ["Security Hub Findings - Imported"]
    detail = {
      findings = {
        Compliance = {
          Status =["FAILED", "WARNING"]
        },
        GeneratorId = ["security-control/EC2.13"],
        Workflow = {
          Status = ["NEW"]
        },
        RecordState =  ["ACTIVE"]
      }
    }
    
  })
}

resource "aws_cloudwatch_event_target" "SCEC213AutoEventRule8D6D5712" {
  rule      = aws_cloudwatch_event_rule.SCEC213AutoEventRule8D6D5712.name
  target_id = "Target0"
  arn       = aws_lambda_function.Ec213ExceptionLambdaFunction.arn
}

resource "aws_lambda_permission" "SCEC213AutoEventRule8D6D5712LambdaPermission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.Ec213ExceptionLambdaFunction.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.SCEC213AutoEventRule8D6D5712.arn
  statement_id = var.SCEC213AutoEventRule_statement_id
}

resource "aws_cloudwatch_event_rule" "SCEC214AutoEventRule6C02D226" {
  name        = "SC_2.0.0_EC2.14_AutoTrigger"
  description = "Remediate SC 2.0.0 EC2.14 automatic remediation trigger event rule."
  is_enabled = true
  event_pattern = jsonencode({
    source = ["aws.securityhub"]
    detail-type = ["Security Hub Findings - Imported"]
    detail = {
      findings = {
        Compliance = {
          Status =["FAILED", "WARNING"]
        },
        GeneratorId = ["security-control/EC2.14"],
        Workflow = {
          Status = ["NEW"]
        },
        RecordState =  ["ACTIVE"]
      }
    }
    
  })
}

resource "aws_cloudwatch_event_target" "SCEC214AutoEventRule6C02D226" {
  rule      = aws_cloudwatch_event_rule.SCEC214AutoEventRule6C02D226.name
  target_id = "Target0"
  arn       = aws_lambda_function.Ec213ExceptionLambdaFunction.arn
}

resource "aws_lambda_permission" "SCEC214AutoEventRule6C02D226LambdaPermission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.Ec213ExceptionLambdaFunction.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.SCEC214AutoEventRule6C02D226.arn
  statement_id = var.SCEC214AutoEventRule_statement_id
}