data "archive_file" "cis_score_report_for_latest_ami_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_CIS_Get_Latest_AMI.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_CIS_Get_Latest_AMI.zip"
}

data "archive_file" "cis_launch_ec2_instances_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_CIS_Launch_EC2_Instance.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_CIS_Launch_EC2_Instance.zip"
}

data "archive_file" "cis_get_ec2_ssm_reporting_status_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_CIS_Get_EC2_SSM_Reporting_Status.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_CIS_Get_EC2_SSM_Reporting_Status.zip"
}

data "archive_file" "cis_get_cis_report_using_ssm_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_CIS-Get_CIS_Report_Using_SSM.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_CIS-Get_CIS_Report_Using_SSM.zip"
}

data "archive_file" "cis_update_cis_score_dynamodb_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_CIS_Update_CIS_Score_DynamoDB.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_CIS_Update_CIS_Score_DynamoDB.zip"
}

data "archive_file" "cis_terminate_ec2_instance_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_CIS_Terminate_EC2_Instance.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_CIS_Terminate_EC2_Instance.zip"
}

data "archive_file" "cis_failure_notification_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_CIS_Send_notification_on_failure.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_CIS_Send_notification_on_failure.zip"
}

# template file for cis state machine
data "template_file" "cis_state_machine_template" {
  template = "${file("${path.module}/StateMachineTemplate/CISStepFunction.json.tpl")}"

  vars = {
    account_number = var.master_account
    account_region = "us-east-1"
  }
}