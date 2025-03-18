data "archive_file" "trb_automation_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_TRB_management_payer.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_TRB_management_payer.zip"
}

data "archive_file" "trb_automation_monitoring_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_TRB_management_monitoring.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_TRB_management_monitoring.zip"
}

data "archive_file" "trb_automation_monitoring_lambda_child_trigger_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_TRB_management_payer_child_account_trigger.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_TRB_management_payer_child_account_trigger.zip"
}

data "archive_file" "trb_result_aggregator_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_TRB_management_payer_result_aggregator.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_TRB_management_payer_result_aggregator.zip"
}

data "aws_iam_policy_document" "data_trb_automation_rest_api_policy" {
  statement {
    sid = "allow statement"
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions   = ["execute-api:Invoke"]
    resources = ["${aws_api_gateway_rest_api.trb_automation_rest_api.execution_arn}/*/*/*"]
  }
}

# step function template
data "template_file" "trb_automation_step_function" {
  template = file("${path.module}/StateMachine/platform_TRB_management_payer_child_trigger.json.tpl")

  vars = {
    account_number = var.master_account
    account_region = "us-east-1"
  }
}