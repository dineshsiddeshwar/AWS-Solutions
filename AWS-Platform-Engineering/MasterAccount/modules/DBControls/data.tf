data "archive_file" "create_report_from_dynamodb_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_ScoreCardCreateReportFromDynamoDB.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_ScoreCardCreateReportFromDynamoDB.zip"
}

data "archive_file" "scorecard_invoke_step_function_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_ScoreCardInvokeStepFunctionOrganisation.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_ScoreCardInvokeStepFunctionOrganisation.zip"
}
