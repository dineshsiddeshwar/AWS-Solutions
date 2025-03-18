data "archive_file" "request_tgw_resource_share_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_request_TGW_resource_share.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_request_TGW_resource_share.zip"
}

data "archive_file" "platform_request_TGW_resource_share_ga_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_request_TGW_resource_share_ga.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_request_TGW_resource_share_ga.zip"
}

data "archive_file" "accept_tgw_resource_share_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_accept_TGW_resource_share.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_accept_TGW_resource_share.zip"
}

data "archive_file" "platform_accept_TGW_resource_share_ga_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_accept_TGW_resource_share_ga.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_accept_TGW_resource_share_ga.zip"
}

data "archive_file" "create_tgw_attachment_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_create_TGW_attachment.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_create_TGW_attachment.zip"
}

data "archive_file" "platform_create_TGW_attachment_ga_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_create_TGW_attachment_ga.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_create_TGW_attachment_ga.zip"
}

data "archive_file" "accept_tgw_attachment_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_accept_TGW_attachment.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_accept_TGW_attachment.zip"
}

data "archive_file" "platform_accept_TGW_attachment_ga_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_accept_TGW_attachment_ga.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_accept_TGW_attachment_ga.zip"
}

data "archive_file" "configure_vpc_tgw_route_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_configure_vpc_traffic_to_TGW.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_configure_vpc_traffic_to_TGW.zip"
}

data "archive_file" "platform_configure_vpc_traffic_to_TGW_ga_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_configure_vpc_traffic_to_TGW_ga.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_configure_vpc_traffic_to_TGW_ga.zip"
}

data "archive_file" "verify_tgw_association_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_verify_TGW_route_association.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_verify_TGW_route_association.zip"
}

data "archive_file" "platform_verify_TGW_route_association_ga_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_verify_TGW_route_association_ga.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_verify_TGW_route_association_ga.zip"
}

data "archive_file" "vpc_tgw_extension_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_vpc_extension_tgw_update.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_vpc_extension_tgw_update.zip"
}

data "archive_file" "platform_vpc_extension_tgw_update_ga_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_vpc_extension_tgw_update_ga.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_vpc_extension_tgw_update_ga.zip"
}

data "archive_file" "disassociate_tgw_attachment_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_disassociate_TGW_attachment.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_disassociate_TGW_attachment.zip"
}

data "archive_file" "platform_disassociate_TGW_attachment_ga_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_disassociate_TGW_attachment_ga.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_disassociate_TGW_attachment_ga.zip"
}

data "archive_file" "disassociate_tgw_resource_share_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_disassociate_TGW_resource_share.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_disassociate_TGW_resource_share.zip"
}

data "archive_file" "disassociate_tgw_resource_share_ga_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_disassociate_TGW_resource_share_ga.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_disassociate_TGW_resource_share_ga.zip"
}

data "template_file" "tgw_integration_state_machine_template_ga" {
  template = "${file("${path.module}/StateMachine/platform_tgw_integration_automation_ga.json.tpl")}"

  vars = {
    account_number = var.master_account
    account_region = "us-east-1"
  }
}