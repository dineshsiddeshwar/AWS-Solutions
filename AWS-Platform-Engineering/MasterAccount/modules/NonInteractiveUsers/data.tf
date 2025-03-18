# getting current account number
data "aws_caller_identity" "current" {}

# getting current region
data "aws_region" "current" {}

data "archive_file" "platform_noninteractive_user_invoker_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_noninteractive_user_invoker.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_noninteractive_user_invoker.zip"
}

data "archive_file" "platform_noninteractive_user_payer_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_noninteractive_user_payer.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_noninteractive_user_payer.zip"
}

data "archive_file" "platform_noninteractive_user_receiver_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_noninteractive_user_receiver.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_noninteractive_user_receiver.zip"
}

data "archive_file" "platform_noninteractive_user_response_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_noninteractive_user_response.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_noninteractive_user_response.zip"
}

data "aws_iam_policy_document" "data_noninteractive_user_snow_integartion_rest_api_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions   = ["execute-api:Invoke"]
    resources = ["arn:aws:execute-api:${local.region}:${local.accountid}:${aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id}/*/*/*"]
  }
}