data "template_file" "snow_integration_state_machine_template" {
  template = "${file("${path.module}/StateMachine/SnowIntegrationStateMachine.json.tpl")}"

  vars = {
    account_number = var.master_account
    account_region = "us-east-1"
  }
}

data "template_file" "snow_integration_state_machine_template_ga" {
  template = "${file("${path.module}/StateMachine/platform_snow_integration_state_machine_ga.json.tpl")}"

  vars = {
    account_number = var.master_account
    account_region = "us-east-1"
  }
}

data "archive_file" "snow_integartion_invoker_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_snow_integration_invoker.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_snow_integration_invoker.zip"
}

data "archive_file" "snow_integartion_processing_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_snow_integration_processing.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_snow_integration_processing.zip"
}

data "archive_file" "snow_integartion_receiver_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_snow_integration_receiver.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_snow_integration_receiver.zip"
}

data "archive_file" "snow_integartion_authorizer_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_snow_integration_authorizer.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_snow_integration_authorizer.zip"
}

data "archive_file" "platform_snow_integration_response_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_snow_integration_response.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_snow_integration_response.zip"
}

data "archive_file" "platform_snow_integration_processing_ga_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_snow_integration_processing_ga.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_snow_integration_processing_ga.zip"
}

data "archive_file" "platform_snow_integration_parameters_ga_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_snow_integration_parameters_ga.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_snow_integration_parameters_ga.zip"
}

data "archive_file" "platform_snow_integration_supporttag_ga_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_snow_integration_supporttag_ga.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_snow_integration_supporttag_ga.zip"
}

data "archive_file" "platform_snow_integration_githubaction_ga_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_snow_integration_githubaction_ga.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_snow_integration_githubaction_ga.zip"
}

data "archive_file" "platform_snow_integration_tfcworkspace_ga_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_snow_integration_tfcworkspace_ga.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_snow_integration_tfcworkspace_ga.zip"
}

data "aws_iam_policy_document" "data_snow_integartion_rest_api_policy" {
  statement {
    sid = "allow statement"
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions   = ["execute-api:Invoke"]
    resources = ["${aws_api_gateway_rest_api.snow_integartion_rest_api.execution_arn}/*/*/*"]
  }
}