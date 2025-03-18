#Default VPC deletion lambda
resource "aws_lambda_function" "default_vpc_deletion_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_default_vpc_deletion.zip"
  function_name = "platform_default_vpc_deletion"
  role          = var.role_arn
  handler       = "platform_default_vpc_deletion.lambda_handler"
  source_code_hash = data.archive_file.default_vpc_deletion_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# VPC provision lambda
resource "aws_lambda_function" "vpc_provision_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_vpc_provision.zip"
  function_name = "platform_vpc_provision"
  role          = var.role_arn
  handler       = "platform_vpc_provision.lambda_handler"
  source_code_hash = data.archive_file.vpc_provision_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}



# Falcon Baseline report Lambda
resource "aws_lambda_function" "falcon_baseline_Report_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_falcon_baseline_report.zip"
  function_name = "platform_falcon_baseline_report"
  role          = var.role_arn
  handler       = "platform_falcon_baseline_report.lambda_handler"
  source_code_hash = data.archive_file.falcon_baseline_Report_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  environment {
    variables = {
      BUCKET = "patching-report-us-east-1-${var.master_account}"

    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Falcon Baseline report schedule
resource "aws_cloudwatch_event_rule" "falcon_baseline_Report_schedule" {
  name        = "platform_facon_lambda_trigger"
  description = "Scheduled Rule for every 12 hours"
  schedule_expression = "cron(0 11 3 * ? *)"
  is_enabled = true
}

resource "aws_cloudwatch_event_target" "falcon_baseline_Report_target" {
  rule      = aws_cloudwatch_event_rule.falcon_baseline_Report_schedule.name
  target_id = "FalconReportFunctionV1"
  arn       = aws_lambda_function.falcon_baseline_Report_lambda.arn
}

resource "aws_lambda_permission" "falcon_baseline_Report_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.falcon_baseline_Report_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.falcon_baseline_Report_schedule.arn
}

# Account Request Lambda
resource "aws_lambda_function" "account_request_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_account_request.zip"
  function_name = "platform_account_request"
  role          = var.role_arn
  handler       = "platform_account_request.lambda_handler"
  source_code_hash = data.archive_file.account_request_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Verify Product Parameters Lambda
resource "aws_lambda_function" "verifyproduct_parameters_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_verifyproduct_parameters.zip"
  function_name = "platform_verifyproduct_parameters"
  role          = var.role_arn
  handler       = "platform_verifyproduct_parameters.lambda_handler"
  source_code_hash = data.archive_file.verifyproduct_parameters_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# FetchDL Lambda
resource "aws_lambda_function" "fetch_dl_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_fetch_dl.zip"
  function_name = "platform_fetch_dl"
  role          = var.role_arn
  handler       = "platform_fetch_dl.lambda_handler"
  source_code_hash = data.archive_file.fetch_dl_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Provision AF Lambda
resource "aws_lambda_function" "provision_child_account_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_provision_child_account.zip"
  function_name = "platform_provision_child_account"
  role          = var.role_arn
  handler       = "platform_provision_child_account.lambda_handler"
  source_code_hash = data.archive_file.provision_child_account_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Provision ProductStatus Lambda
resource "aws_lambda_function" "provision_product_status_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_provision_product_status.zip"
  function_name = "platform_provision_product_status"
  role          = var.role_arn
  handler       = "platform_provision_product_status.lambda_handler"
  source_code_hash = data.archive_file.provision_product_status_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Update DL Table Lambda
resource "aws_lambda_function" "update_dltable_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_update_dltable.zip"
  function_name = "platform_update_dltable"
  role          = var.role_arn
  handler       = "platform_update_dltable.lambda_handler"
  source_code_hash = data.archive_file.update_dltable_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Update Account Table SF Lambda
resource "aws_lambda_function" "update_account_table_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_update_account_table.zip"
  function_name = "platform_update_account_table"
  role          = var.role_arn
  handler       = "platform_update_account_table.lambda_handler"
  source_code_hash = data.archive_file.update_account_table_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Account Authorization Lambda
resource "aws_lambda_function" "account_authorization_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_child_account_roles.zip"
  function_name = "platform_child_account_roles"
  role          = var.role_arn
  handler       = "platform_child_account_roles.lambda_handler"
  source_code_hash = data.archive_file.account_authorization_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Account Access Management Lambda
resource "aws_lambda_function" "access_management_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_access_management.zip"
  function_name = "platform_access_management"
  role          = var.role_arn
  handler       = "platform_access_management.lambda_handler"
  source_code_hash = data.archive_file.access_management_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Add Stack Instance To Stack Lambda
resource "aws_lambda_function" "add_stackinstance_to_stackset_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_add_stackinstance_to_stackset.zip"
  function_name = "platform_add_stackinstance_to_stackset"
  role          = var.role_arn
  handler       = "platform_add_stackinstance_to_stackset.lambda_handler"
  source_code_hash = data.archive_file.add_stackinstance_to_stackset_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Set Budget In Child Account Lambda
resource "aws_lambda_function" "set_budget_in_childaccount_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_set_budget_in_childaccount.zip"
  function_name = "platform_set_budget_in_childaccount"
  role          = var.role_arn
  handler       = "platform_set_budget_in_childaccount.lambda_handler"
  source_code_hash = data.archive_file.set_budget_in_childaccount_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Enable Enterprise Support Lambda
resource "aws_lambda_function" "enable_enterprise_support_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_enable_enterprise_support.zip"
  function_name = "platform_enable_enterprise_support"
  role          = var.role_arn
  handler       = "platform_enable_enterprise_support.lambda_handler"
  source_code_hash = data.archive_file.enable_enterprise_support_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# IAMAnalyzer Enable Lambda
resource "aws_lambda_function" "analyzer_enable_child_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_analyzer_enable_child.zip"
  function_name = "platform_analyzer_enable_child"
  role          = var.role_arn
  handler       = "platform_analyzer_enable_child.lambda_handler"
  source_code_hash = data.archive_file.analyzer_enable_child_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Create SNS Topic Lambda
resource "aws_lambda_function" "security_sns_topic_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_security_sns_topic.zip"
  function_name = "platform_security_sns_topic"
  role          = var.role_arn
  handler       = "platform_security_sns_topic.lambda_handler"
  source_code_hash = data.archive_file.security_sns_topic_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Block S3 Public Access Lambda
resource "aws_lambda_function" "security_s3_block_public_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_security_s3_block_public.zip"
  function_name = "platform_security_s3_block_public"
  role          = var.role_arn
  handler       = "platform_security_s3_block_public.lambda_handler"
  source_code_hash = data.archive_file.security_s3_block_public_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Enable EBS Encryption Lambda
resource "aws_lambda_function" "security_enable_ebs_encryption_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_security_enable_ebs_encryption.zip"
  function_name = "platform_security_enable_ebs_encryption"
  role          = var.role_arn
  handler       = "platform_security_enable_ebs_encryption.lambda_handler"
  source_code_hash = data.archive_file.security_enable_ebs_encryption_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Block EMR Public Access Lambda
resource "aws_lambda_function" "security_emr_block_public_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_security_emr_block_public.zip"
  function_name = "platform_security_emr_block_public"
  role          = var.role_arn
  handler       = "platform_security_emr_block_public.lambda_handler"
  source_code_hash = data.archive_file.security_emr_block_public_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# BackUp Vault SetUp Lambda
resource "aws_lambda_function" "setup_backup_resource_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_setup_backup_resource.zip"
  function_name = "platform_setup_backup_resource"
  role          = var.role_arn
  handler       = "platform_setup_backup_resource.lambda_handler"
  source_code_hash = data.archive_file.setup_backup_resource_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# sendtemplatedmail Lambda
resource "aws_lambda_function" "send_templated_mail_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_send_templated_mail.zip"
  function_name = "platform_send_templated_mail"
  role          = var.role_arn
  handler       = "platform_send_templated_mail.lambda_handler"
  source_code_hash = data.archive_file.send_templated_mail_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platformInstallFalconLinux Lambda
resource "aws_lambda_function" "installfalcon_linux_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_installfalcon_linux.zip"
  function_name = "platform_installfalcon_linux"
  role          = var.role_arn
  handler       = "platform_installfalcon_linux.lambda_handler"
  source_code_hash = data.archive_file.installfalcon_linux_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 1600
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platformInstallFalconWindows Lambda
resource "aws_lambda_function" "installFalcon_windows_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_InstallFalcon_Windows.zip"
  function_name = "platform_InstallFalcon_Windows"
  role          = var.role_arn
  handler       = "platform_InstallFalcon_Windows.lambda_handler"
  source_code_hash = data.archive_file.installFalcon_windows_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 1408
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platformInstallFlexeraAgentLinux Lambda
resource "aws_lambda_function" "installFlexeraAgent_linux_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_InstallFlexeraAgent_Linux.zip"
  function_name = "platform_InstallFlexeraAgent_Linux"
  role          = var.role_arn
  handler       = "platform_InstallFlexeraAgent_Linux.lambda_handler"
  source_code_hash = data.archive_file.installFlexeraAgent_linux_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 1728
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platformInstallFlexeraAgentWindows Lambda
resource "aws_lambda_function" "installFlexeraAgent_Windows_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_InstallFlexeraAgent_Windows.zip"
  function_name = "platform_InstallFlexeraAgent_Windows"
  role          = var.role_arn
  handler       = "platform_InstallFlexeraAgent_Windows.lambda_handler"
  source_code_hash = data.archive_file.installFlexeraAgent_Windows_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platformInstallCloudHealthLinux Lambda
resource "aws_lambda_function" "installCloudHealth_Linux_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_InstallCloudHealth_Linux.zip"
  function_name = "platform_InstallCloudHealth_Linux"
  role          = var.role_arn
  handler       = "platform_InstallCloudHealth_Linux.lambda_handler"
  source_code_hash = data.archive_file.installCloudHealth_Linux_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 1024
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platformInstallCloudHealthWindows Lambda
resource "aws_lambda_function" "installCloudHealth_Windows_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_InstallCloudHealth_Windows.zip"
  function_name = "platform_InstallCloudHealth_Windows"
  role          = var.role_arn
  handler       = "platform_InstallCloudHealth_Windows.lambda_handler"
  source_code_hash = data.archive_file.installCloudHealth_Windows_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 1536
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platformInstallCloudWatchAgent Lambda
resource "aws_lambda_function" "installCloudWatchAgent_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_InstallCloudWatchAgent.zip"
  function_name = "platform_InstallCloudWatchAgent"
  role          = var.role_arn
  handler       = "platform_InstallCloudWatchAgent.lambda_handler"
  source_code_hash = data.archive_file.installCloudWatchAgent_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 1728
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platformInstallRapid7Lunix Lambda
resource "aws_lambda_function" "installRapid7_Linux_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_InstallRapid7_Linux.zip"
  function_name = "platform_InstallRapid7_Linux"
  role          = var.role_arn
  handler       = "platform_InstallRapid7_Linux.lambda_handler"
  source_code_hash = data.archive_file.installRapid7_Linux_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platformInstallRapid7Windows Lambda
resource "aws_lambda_function" "installRapid7_windows_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_InstallRapid7_windows.zip"
  function_name = "platform_InstallRapid7_windows"
  role          = var.role_arn
  handler       = "platform_InstallRapid7_windows.lambda_handler"
  source_code_hash = data.archive_file.installRapid7_windows_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

#platform linux association
resource "aws_lambda_function" "linus_association_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_linux_association.zip"
  function_name = "platform_linux_association"
  role          = var.role_arn
  handler       = "platform_linux_association.lambda_handler"
  source_code_hash = data.archive_file.platform_linux_association_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 1408
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

#platform windows association
resource "aws_lambda_function" "windows_association_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_windows_association.zip"
  function_name = "platform_windows_association"
  role          = var.role_arn
  handler       = "platform_windows_association.lambda_handler"
  source_code_hash = data.archive_file.platform_windows_association_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 1408
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# chargeableresourceinventory Lambda
resource "aws_lambda_function" "chargeable_resource_inventory_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_chargeable_resource_inventory.zip"
  function_name = "platform_chargeable_resource_inventory"
  role          = var.role_arn
  handler       = "platform_chargeable_resource_inventory.lambda_handler"
  source_code_hash = data.archive_file.chargeable_resource_inventory_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# decommail Lambda
resource "aws_lambda_function" "decom_mail_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_decom_mail.zip"
  function_name = "platform_decom_mail"
  role          = var.role_arn
  handler       = "platform_decom_mail.lambda_handler"
  source_code_hash = data.archive_file.decom_mail_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platformmovedecomou Lambda
resource "aws_lambda_function" "move_decom_ou_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_move_decom_ou.zip"
  function_name = "platform_move_decom_ou"
  role          = var.role_arn
  handler       = "platform_move_decom_ou.lambda_handler"
  source_code_hash = data.archive_file.move_decom_ou_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# PlatformDomainjoin Lambda
resource "aws_lambda_function" "SSM_Association_Domainjoin_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_SSM_Association_Domainjoin.zip"
  function_name = "platform_SSM_Association_Domainjoin"
  role          = var.role_arn
  handler       = "platform_SSM_Association_Domainjoin.lambda_handler"
  source_code_hash = data.archive_file.SSM_Association_Domainjoin_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# PlatformStackSetIaC Lambda
resource "aws_lambda_function" "stack_set_iac_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_stack_set_iac.zip"
  function_name = "platform_stack_set_iac"
  role          = var.role_arn
  handler       = "platform_stack_set_iac.lambda_handler"
  source_code_hash = data.archive_file.stack_set_iac_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# PlatformNetworkLaunch Lambda
resource "aws_lambda_function" "network_launch_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_network_launch.zip"
  function_name = "platform_network_launch"
  role          = var.role_arn
  handler       = "platform_network_launch.lambda_handler"
  source_code_hash = data.archive_file.network_launch_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# PlatformNetworkCustomResource Lambda
resource "aws_lambda_function" "network_custom_resource_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_network_custom_resource.zip"
  function_name = "platform_network_custom_resource"
  role          = var.role_arn
  handler       = "platform_network_custom_resource.lambda_handler"
  source_code_hash = data.archive_file.platform_network_custom_resource_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# PlatformNetworkFetchCIDR Lambda
resource "aws_lambda_function" "network_fetch_cidr_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_network_fetch_cidr.zip"
  function_name = "platform_network_fetch_cidr"
  role          = var.role_arn
  handler       = "platform_network_fetch_cidr.lambda_handler"
  source_code_hash = data.archive_file.network_fetch_cidr_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# PlatformNetworkVPCExtension Lambda
resource "aws_lambda_function" "network_vpc_extension_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_network_vpc_extension.zip"
  function_name = "platform_network_vpc_extension"
  role          = var.role_arn
  handler       = "platform_network_vpc_extension.lambda_handler"
  source_code_hash = data.archive_file.network_vpc_extension_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# PlatformNetworkVPCcreation Lambda
resource "aws_lambda_function" "network_vpc_creation_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_network_vpc_creation.zip"
  function_name = "platform_network_vpc_creation"
  role          = var.role_arn
  handler       = "platform_network_vpc_creation.lambda_handler"
  source_code_hash = data.archive_file.network_vpc_creation_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }

  environment {
    variables = {
      env = var.vpc_flow_bucket_env_type
    }
  }
}

# PlatformNetworkSubnetCreation Lambda
resource "aws_lambda_function" "network_subnet_creation_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_network_subnet_creation.zip"
  function_name = "platform_network_subnet_creation"
  role          = var.role_arn
  handler       = "platform_network_subnet_creation.lambda_handler"
  source_code_hash = data.archive_file.network_subnet_creation_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# PlatformNetworkUpdateTable Lambda
resource "aws_lambda_function" "network_update_table_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_network_update_table.zip"
  function_name = "platform_network_update_table"
  role          = var.role_arn
  handler       = "platform_network_update_table.lambda_handler"
  source_code_hash = data.archive_file.network_update_table_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# PlatformNetworkVPCAssociations Lambda
resource "aws_lambda_function" "network_vpc_associations_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_network_vpc_associations.zip"
  function_name = "platform_network_vpc_associations"
  role          = var.role_arn
  handler       = "platform_network_vpc_associations.lambda_handler"
  source_code_hash = data.archive_file.network_vpc_associations_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# PlatformNetworkcreateResolver Lambda
resource "aws_lambda_function" "network_create_resolver_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_network_create_resolver.zip"
  function_name = "platform_network_create_resolver"
  role          = var.role_arn
  handler       = "platform_network_create_resolver.lambda_handler"
  source_code_hash = data.archive_file.network_create_resolver_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# PlatformNetworkEnableIGW Lambda
resource "aws_lambda_function" "network_enable_igw_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_network_enable_igw.zip"
  function_name = "platform_network_enable_igw"
  role          = var.role_arn
  handler       = "platform_network_enable_igw.lambda_handler"
  source_code_hash = data.archive_file.network_enable_igw_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# PlatformSSMAgentAutoUpdate Lambda
resource "aws_lambda_function" "ssm_agent_autoupdate_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_ssm_agent_autoupdate.zip"
  function_name = "platform_ssm_agent_autoupdate"
  role          = var.role_arn
  handler       = "platform_ssm_agent_autoupdate.lambda_handler"
  source_code_hash = data.archive_file.ssm_agent_autoupdate_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# AccountUpdate Automation Lambda
resource "aws_lambda_function" "update_child_account_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_update_child_account.zip"
  function_name = "platform_update_child_account"
  role          = var.role_arn
  handler       = "platform_update_child_account.lambda_handler"
  source_code_hash = data.archive_file.update_child_account_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# PlatformOSDetails Lambda
resource "aws_lambda_function" "os_details_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_os_details.zip"
  function_name = "platform_os_details"
  role          = var.role_arn
  handler       = "platform_os_details.lambda_handler"
  source_code_hash = data.archive_file.os_detailst_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 1024
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# PlatformSGDetails Lambda
resource "aws_lambda_function" "sg_details_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_sg_details.zip"
  function_name = "platform_sg_details"
  role          = var.role_arn
  handler       = "platform_sg_details.lambda_handler"
  source_code_hash = data.archive_file.sg_details_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 1024
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SecurityHubRefinements Lambda
resource "aws_lambda_function" "securityhub_refinements_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_securityhub_refinements.zip"
  function_name = "platform_securityhub_refinements"
  role          = var.role_arn
  handler       = "platform_securityhub_refinements.lambda_handler"
  source_code_hash = data.archive_file.securityhub_refinements_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SecurityHubRefinements Lambda
resource "aws_lambda_function" "create_custom_insights_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_create_custom_insights.zip"
  function_name = "platform_create_custom_insights"
  role          = var.role_arn
  handler       = "platform_create_custom_insights.lambda_handler"
  source_code_hash = data.archive_file.create_custom_insights_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# PlatformNonRoutableVPCExtension Lambda
resource "aws_lambda_function" "non_routable_vpc_extension_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_non_routable_vpc_extension.zip"
  function_name = "platform_non_routable_vpc_extension"
  role          = var.role_arn
  handler       = "platform_non_routable_vpc_extension.lambda_handler"
  source_code_hash = data.archive_file.non_routable_vpc_extension_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# PlatformNonRoutableNetworkResources Lambda
resource "aws_lambda_function" "non_routable_network_resources_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_non_routable_network_resources.zip"
  function_name = "platform_non_routable_network_resources"
  role          = var.role_arn
  handler       = "platform_non_routable_network_resources.lambda_handler"
  source_code_hash = data.archive_file.non_routable_network_resources_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

#Platform lambda resource for running interactive user query
resource "aws_lambda_function" "platform_interactive_user_query" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_interactive_user_query.zip"
  function_name = "platform_interactive_user_query"
  role          = var.master_admin_role_arn
  handler       = "platform_interactive_user_query.lambda_handler"
  source_code_hash = data.archive_file.platform_interactive_user_query_zip.output_base64sha256

  runtime = "python3.9"
  timeout = 900
  memory_size = 128

  environment {
    variables = {
      BUCKET = "aws-cloudtrail-lake-query-results-${var.master_account}-us-east-1"
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

#Platform lambda resource for finding login profile of users
resource "aws_lambda_function" "platform_interactive_user_test" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_interactive_user_test.zip"
  function_name = "platform_interactive_user_test"
  role          = var.master_admin_role_arn
  handler       = "platform_interactive_user_test.lambda_handler"
  source_code_hash = data.archive_file.platform_interactive_user_test_zip.output_base64sha256

  runtime = "python3.9"
  timeout = 900
  memory_size = 128

  environment {
    variables = {
      BUCKET = "aws-cloudtrail-lake-query-results-${var.master_account}-us-east-1"
      MASTER_ACCOUNT_ID = var.master_account
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# RootActivity CloudWatch Event Lambda Rule Trigger
resource "aws_cloudwatch_event_rule" "platform_interactive_user_query_rule" {
  description = "Scheduled Rule for once a month"
  name = "platform_interactive_user_query_trigger"
  schedule_expression = "cron(0 12 ? * 1 *)"
  is_enabled = true
}

# RootActivity CloudWatch Event Lambda Rule Target
resource "aws_cloudwatch_event_target" "platform_interactive_user_query_target" {
  rule      = aws_cloudwatch_event_rule.platform_interactive_user_query_rule.name
  target_id = "platform_interactive_user_query"
  arn       = aws_lambda_function.platform_interactive_user_query.arn
}

## RootActivity CloudWatch Event Lambda Permissions
resource "aws_lambda_permission" "platform_interactive_user_query_rule_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.platform_interactive_user_query.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.platform_interactive_user_query_rule.arn
}

