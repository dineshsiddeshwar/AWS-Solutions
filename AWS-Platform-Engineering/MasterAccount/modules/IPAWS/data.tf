data "archive_file" "ipaws_integration_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_ipaws_integration.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_ipaws_integration.zip"
}