data "archive_file" "vpc_snow_integration_invoker_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_snow_networkvpc_integration_invoker.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_snow_networkvpc_integration_invoker.zip"
}

data "archive_file" "vpc_snow_integration_processing_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_snow_networkvpc_integration_processing.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_snow_networkvpc_integration_processing.zip"
}

data "archive_file" "vpc_snow_integration_receiver_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_snow_networkvpc_integration_receiver.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_snow_networkvpc_integration_receiver.zip"
}

data "archive_file" "vpc_snow_integration_response_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_snow_networkvpc_integration_response.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_snow_networkvpc_integration_response.zip"
}

data "archive_file" "vpc_snow_integration_authorizer_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_snow_networkvpc_integration_authorizer.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_snow_networkvpc_integration_authorizer.zip"
}

data "aws_region" "current" {}

# template file for Statemachine
data "template_file" "vpc_snow_integration_state_machine_template" {
  template = "${file("${path.module}/StateMachine/StepFunction.json.tpl")}"

  vars = {
    account_region = data.aws_region.current.name
    account_number = var.master_account
  }
}


data "aws_iam_policy_document" "data_vpc_snow_integration_rest_api_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions   = ["execute-api:Invoke"]
    resources = ["${aws_api_gateway_rest_api.vpc_snow_integration_rest_api.execution_arn}/*/*/*"]
  }

}