data "archive_file" "scp_exception_receiver_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_scp_exception_reciever.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_scp_exception_reciever.zip"
}

data "aws_iam_policy_document" "data_scp_exception_rest_api_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions   = ["execute-api:Invoke"]
    resources = ["${aws_api_gateway_rest_api.scp_exception_rest_api.execution_arn}/*/*/*"]
  }
}

data "archive_file" "scp_exception_invoker_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_scp_exception_management_invoker.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_scp_exception_management_invoker.zip"
}

data "archive_file" "scp_exception_expiry_handler_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_scp_exception_expiry_handler.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_scp_exception_expiry_handler.zip"
}

data "archive_file" "scp_exception_get_ou_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_scp_get_ou_details.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_scp_get_ou_details.zip"
}

data "archive_file" "scp_exception_adhoc_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_adhoc_scp_exception_management.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_adhoc_scp_exception_management.zip"
}

data "archive_file" "scp_exception_move_account_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_scp_move_account.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_scp_move_account.zip"
}

data "archive_file" "scp_exception_check_ou_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_scp_check_ou.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_scp_check_ou.zip"
}

data "archive_file" "scp_exception_check_status_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_scp_check_status.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_scp_check_status.zip"
}

data "archive_file" "scp_exception_create_policy_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_scp_create_policy.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_scp_create_policy.zip"
}

data "archive_file" "scp_exception_update_policy_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_scp_update_policy.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_scp_update_policy.zip"
}

data "archive_file" "scp_exception_update_db_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_scp_update_db.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_scp_update_db.zip"
}

data "archive_file" "scp_exception_snow_response_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_scp_send_snow_response.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_scp_send_snow_response.zip"
}

data "archive_file" "scp_exception_send_success_email_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_scp_send_success_email.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_scp_send_success_email.zip"
}

data "archive_file" "scp_exception_send_failed_email_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_scp_send_failure_email.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_scp_send_failure_email.zip"
}

data "archive_file" "scp_exception_validate_ou_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_scp_validate_ou.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_scp_validate_ou.zip"
}

data "aws_region" "current" {}

# template file for Statemachine
data "template_file" "scp_exception_state_machine_template" {
  template = "${file("${path.module}/StateMachine/StepFunction.json.tpl")}"

  vars = {
    account_region = data.aws_region.current.name
    account_number = var.master_account
  }
}


