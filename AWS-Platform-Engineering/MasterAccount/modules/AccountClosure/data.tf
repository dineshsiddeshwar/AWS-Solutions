data "archive_file" "close_account_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_close_account.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_close_account.zip"
}
