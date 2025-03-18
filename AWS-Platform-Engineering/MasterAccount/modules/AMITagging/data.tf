data "archive_file" "tagautomation_create_resource_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_tagautomation_create_resource.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_tagautomation_create_resource.zip"
}

data "archive_file" "ami_tagging_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_ami_tagging.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_ami_tagging.zip"
}

data "archive_file" "eks_ami_tagging_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_ami_tagging_eks.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_ami_tagging_eks.zip"
}

data "archive_file" "exception_scheduled_ami_tagging_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_exception_scheduled_ami_tagging.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_exception_scheduled_ami_tagging.zip"
}

data "archive_file" "exception_ami_tagging_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_exception_ami_tagging.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_exception_ami_tagging.zip"
}

data "archive_file" "custom_ami_tagging_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_Custome-AMI-Tagging.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_Custome-AMI-Tagging.zip"
}