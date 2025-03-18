data "archive_file" "update_alternate_contacts_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_update_alternate_contacts.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_update_alternate_contacts.zip"
}

data "archive_file" "Enable-SecurityHub-Standards_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_enable_securityhub_standard.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_enable_securityhub_standard.zip"
}