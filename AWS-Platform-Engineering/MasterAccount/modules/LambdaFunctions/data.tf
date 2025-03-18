data "archive_file" "default_vpc_deletion_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_default_vpc_deletion.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_default_vpc_deletion.zip"
}

data "archive_file" "vpc_provision_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_vpc_provision.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_vpc_provision.zip"
}

data "archive_file" "falcon_baseline_Report_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_falcon_baseline_report.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_falcon_baseline_report.zip"
}

data "archive_file" "account_request_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_account_request.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_account_request.zip"
}

data "archive_file" "verifyproduct_parameters_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_verifyproduct_parameters.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_verifyproduct_parameters.zip"
}

data "archive_file" "fetch_dl_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_fetch_dl.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_fetch_dl.zip"
}

data "archive_file" "provision_child_account_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_provision_child_account.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_provision_child_account.zip"
}

data "archive_file" "provision_product_status_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_provision_product_status.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_provision_product_status.zip"
}

data "archive_file" "update_dltable_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_update_dltable.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_update_dltable.zip"
}

data "archive_file" "update_account_table_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_update_account_table.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_update_account_table.zip"
}

data "archive_file" "account_authorization_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_child_account_roles.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_child_account_roles.zip"
}

data "archive_file" "access_management_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_access_management.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_access_management.zip"
}

data "archive_file" "add_stackinstance_to_stackset_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_add_stackinstance_to_stackset.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_add_stackinstance_to_stackset.zip"
}

data "archive_file" "set_budget_in_childaccount_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_set_budget_in_childaccount.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_set_budget_in_childaccount.zip"
}

data "archive_file" "enable_enterprise_support_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_enable_enterprise_support.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_enable_enterprise_support.zip"
}

data "archive_file" "analyzer_enable_child_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_analyzer_enable_child.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_analyzer_enable_child.zip"
}

data "archive_file" "security_sns_topic_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_security_sns_topic.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_security_sns_topic.zip"
}

data "archive_file" "security_s3_block_public_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_security_s3_block_public.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_security_s3_block_public.zip"
}

data "archive_file" "security_enable_ebs_encryption_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_security_enable_ebs_encryption.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_security_enable_ebs_encryption.zip"
}

data "archive_file" "security_emr_block_public_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_security_emr_block_public.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_security_emr_block_public.zip"
}

data "archive_file" "setup_backup_resource_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_setup_backup_resource.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_setup_backup_resource.zip"
}

data "archive_file" "send_templated_mail_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_send_templated_mail.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_send_templated_mail.zip"
}

data "archive_file" "installfalcon_linux_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_installfalcon_linux.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_installfalcon_linux.zip"
}

data "archive_file" "installFalcon_windows_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_InstallFalcon_Windows.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_InstallFalcon_Windows.zip"
}

data "archive_file" "installFlexeraAgent_linux_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_InstallFlexeraAgent_Linux.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_InstallFlexeraAgent_Linux.zip"
}

data "archive_file" "installFlexeraAgent_Windows_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_InstallFlexeraAgent_Windows.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_InstallFlexeraAgent_Windows.zip"
}

data "archive_file" "installCloudHealth_Linux_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_InstallCloudHealth_Linux.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_InstallCloudHealth_Linux.zip"
}

data "archive_file" "installCloudHealth_Windows_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_InstallCloudHealth_Windows.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_InstallCloudHealth_Windows.zip"
}

data "archive_file" "installCloudWatchAgent_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_InstallCloudWatchAgent.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_InstallCloudWatchAgent.zip"
}

data "archive_file" "installRapid7_Linux_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_InstallRapid7_Linux.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_InstallRapid7_Linux.zip"
}

data "archive_file" "installRapid7_windows_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_InstallRapid7_windows.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_InstallRapid7_windows.zip"
}

data "archive_file" "chargeable_resource_inventory_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_chargeable_resource_inventory.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_chargeable_resource_inventory.zip"
}

data "archive_file" "decom_mail_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_decom_mail.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_decom_mail.zip"
}

data "archive_file" "move_decom_ou_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_move_decom_ou.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_move_decom_ou.zip"
}

data "archive_file" "SSM_Association_Domainjoin_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_SSM_Association_Domainjoin.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_SSM_Association_Domainjoin.zip"
}

data "archive_file" "stack_set_iac_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_stack_set_iac.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_stack_set_iac.zip"
}

data "archive_file" "network_launch_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_network_launch.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_network_launch.zip"
}

data "archive_file" "network_fetch_cidr_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_network_fetch_cidr.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_network_fetch_cidr.zip"
}

data "archive_file" "network_vpc_extension_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_network_vpc_extension.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_network_vpc_extension.zip"
}

data "archive_file" "network_vpc_creation_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_network_vpc_creation.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_network_vpc_creation.zip"
}

data "archive_file" "network_subnet_creation_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_network_subnet_creation.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_network_subnet_creation.zip"
}

data "archive_file" "network_update_table_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_network_update_table.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_network_update_table.zip"
}

data "archive_file" "network_vpc_associations_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_network_vpc_associations.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_network_vpc_associations.zip"
}

data "archive_file" "network_create_resolver_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_network_create_resolver.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_network_create_resolver.zip"
}

data "archive_file" "network_enable_igw_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_network_enable_igw.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_network_enable_igw.zip"
}

data "archive_file" "ssm_agent_autoupdate_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_ssm_agent_autoupdate.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_ssm_agent_autoupdate.zip"
}

data "archive_file" "update_child_account_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_update_child_account.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_update_child_account.zip"
}

data "archive_file" "os_detailst_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_os_details.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_os_details.zip"
}

data "archive_file" "sg_details_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_sg_details.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_sg_details.zip"
}

data "archive_file" "securityhub_refinements_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_securityhub_refinements.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_securityhub_refinements.zip"
}

data "archive_file" "create_custom_insights_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_create_custom_insights.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_create_custom_insights.zip"
}

data "archive_file" "non_routable_vpc_extension_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_non_routable_vpc_extension.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_non_routable_vpc_extension.zip"
}

data "archive_file" "non_routable_network_resources_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_non_routable_network_resources.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_non_routable_network_resources.zip"
}

data "archive_file" "platform_network_custom_resource_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_network_custom_resource.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_network_custom_resource.zip"
}
data "archive_file" "platform_interactive_user_query_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_interactive_user_query.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_interactive_user_query.zip"
}

data "archive_file" "platform_interactive_user_test_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_interactive_user_test.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_interactive_user_test.zip"
}

data "archive_file" "platform_linux_association_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_linux_association.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_linux_association.zip"
}

data "archive_file" "platform_windows_association_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_windows_association.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_windows_association.zip"
}
