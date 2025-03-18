data "archive_file" "scim_sso_assigner_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_SCIM_SSO_assigner.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_SCIM_SSO_assigner.zip"
}
