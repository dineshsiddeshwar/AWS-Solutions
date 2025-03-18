# AF product id SSM
resource "aws_ssm_parameter" "af_product_id_parameter" {
  name  = "AFproductid"
  type  = "String"
  value = var.af_product_id
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform contributor external role arn SSM
resource "aws_ssm_parameter" "platformcontributorexternalrolearn_parameter" {
  name  = "platform_contributorexternalrolearn"
  type  = "String"
  value = var.platformcontributorexternalrolearn
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform master contributor role arn SSM
resource "aws_ssm_parameter" "platformmastercontributorrolearn_parameter" {
  name  = "platform_mastercontributorrolearn"
  type  = "String"
  value = var.platformmastercontributorrolearn
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform datalake id SSM
resource "aws_ssm_parameter" "platformdatalakeid_parameter" {
  name  = "platform_datalakeid"
  type  = "String"
  value = var.platformdatalakeid
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Root Monitoring Exemption Days SSM
resource "aws_ssm_parameter" "RootMonitoringExemptionDays_parameter" {
  name  = "root_monitoring_exemption_days"
  type  = "String"
  value = var.RootMonitoringExemptionDays
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Relese S3 bucket Name SSM
resource "aws_ssm_parameter" "release_S3_bucket_parameter" {
  name  = "releses3bucket"
  type  = "String"
  value = var.release_S3_bucket
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Relese Folder Name SSM
resource "aws_ssm_parameter" "release_folder_parameter" {
  name  = "foldername"
  type  = "String"
  value = var.release_folder
  tags = {
    "platform_donotdelete" = "yes"
  }
}


# Release Integration Log SSM
resource "aws_ssm_parameter" "snow_integration_log_bucket_parameter" {
  name  = "SnowIntegrationLogBucket"
  type  = "String"
  value = "platform-snow-integration-logs-${var.env_type}"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Shared directoryId Us East1 SSM
resource "aws_ssm_parameter" "shared_directory_id_us_parameter" {
  name  = "directoryIduseast1"
  type  = "String"
  value = var.shared_directory_id_us
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Shared directoryName Us East1 SSM
resource "aws_ssm_parameter" "shared_directory_name_us_parameter" {
  name  = "directoryNameuseast1"
  type  = "String"
  value = var.shared_directory_name_us
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Shared directoryIpAddress Us East1 SSM
resource "aws_ssm_parameter" "shared_directory_ip_us_parameter" {
  name  = "dnsIpAddressesuseast1"
  type  = "String"
  value = var.shared_directory_ip_us
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Shared directoryId Eu West1 SSM
resource "aws_ssm_parameter" "shared_directory_id_eu_parameter" {
  name  = "directoryIdeuwest1"
  type  = "String"
  value = var.shared_directory_id_eu
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Shared directoryName Eu West1 SSM
resource "aws_ssm_parameter" "shared_directory_name_eu_parameter" {
  name  = "directoryNameeuwest1"
  type  = "String"
  value = var.shared_directory_name_eu
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Shared directoryIpAddress Eu West1 SSM
resource "aws_ssm_parameter" "shared_directory_ip_eu_parameter" {
  name  = "dnsIpAddresseseuwest1"
  type  = "String"
  value = var.shared_directory_ip_eu
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Shared directoryId AP Southest1  SSM
resource "aws_ssm_parameter" "shared_directory_id_singapore_parameter" {
  name  = "directoryIdapsoutheast1"
  type  = "String"
  value = var.shared_directory_id_singapore
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Shared directoryName AP Southest1  SSM
resource "aws_ssm_parameter" "shared_directory_name_singapore_parameter" {
  name  = "directoryNameapsoutheast1"
  type  = "String"
  value = var.shared_directory_name_singapore
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Shared directoryIpAddress AP Southest1  SSM
resource "aws_ssm_parameter" "shared_directory_ip_singapore_parameter" {
  name  = "dnsIpAddressesapsoutheast1"
  type  = "String"
  value = var.shared_directory_ip_singapore
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Account Update Bucket SSM
resource "aws_ssm_parameter" "account_update_bucket_parameter" {
  name  = "AccountUpdateBucket"
  type  = "String"
  value = var.account_update_bucket
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Private Production OU SSM
resource "aws_ssm_parameter" "private_production_ou_parameter" {
  name  = "Private-Production"
  type  = "String"
  value = var.private_production_ou
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Private Staging OU SSM
resource "aws_ssm_parameter" "private_staging_ou_parameter" {
  name  = "Private-Staging"
  type  = "String"
  value = var.private_staging_ou
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Private Exception OU SSM
resource "aws_ssm_parameter" "private_exception_ou_parameter" {
  name  = "Private-Exception"
  type  = "String"
  value = var.private_exception_ou
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Public Exception OU SSM
resource "aws_ssm_parameter" "public_exception_ou_parameter" {
  name  = "Public-Exception"
  type  = "String"
  value = var.public_exception_ou
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Public Staging OU SSM
resource "aws_ssm_parameter" "public_staging_ou_parameter" {
  name  = "Public-Staging"
  type  = "String"
  value = var.public_staging_ou
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Public Production OU SSM
resource "aws_ssm_parameter" "public_production_ou_parameter" {
  name  = "Public-Production"
  type  = "String"
  value = var.public_production_ou
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Managed Services BeAgile SSM
resource "aws_ssm_parameter" "managed_services_beagile_ou_parameter" {
  name  = "Managed-Services-BeAgile"
  type  = "String"
  value = var.managed_services_beagile_ou
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Data Management SSM
resource "aws_ssm_parameter" "data_management_ou_parameter" {
  name  = "Data-Management"
  type  = "String"
  value = var.data_management_ou
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Hybrid Account SSM
resource "aws_ssm_parameter" "hybrid_account_ou_parameter" {
  name  = "Hybrid-Account"
  type  = "String"
  value = var.hybrid_account_ou
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Migration Account SSM
resource "aws_ssm_parameter" "migration_account_ou_parameter" {
  name  = "Migration-Account"
  type  = "String"
  value = var.migration_account_ou
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Root OU Id SSM
resource "aws_ssm_parameter" "root_ou_parameter" {
  name  = "Root_OU_id"
  type  = "String"
  value = var.root_ou
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# account Detail Table Name
resource "aws_ssm_parameter" "account_details_table_parameter" {
  name  = "accountDetailTableName"
  type  = "String"
  value = var.account_details_table
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# exception Ami Table Name SSM
resource "aws_ssm_parameter" "exception_ami_table_parameter" {
  name  = "ExceptionAMIDynamoDBTableName"
  type  = "String"
  value = var.exception_ami_table
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# admin Account SSM
resource "aws_ssm_parameter" "admin_account_parameter" {
  name  = "admin_account"
  type  = "String"
  value = var.admin_account
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# admin dl SSM
resource "aws_ssm_parameter" "admin_dl_parameter" {
  name  = "admin_dl"
  type  = "String"
  value = var.admin_dl
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# audit account SSM
resource "aws_ssm_parameter" "audit_account_parameter" {
  name  = "audit_account"
  type  = "String"
  value = var.audit_account
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# audit account admin role arn SSM
resource "aws_ssm_parameter" "audit_account_admin_role_arn_parameter" {
  name  = "audit_admin_role_arn"
  type  = "String"
  value = var.audit_account_admin_role_arn
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# logging account SSM
resource "aws_ssm_parameter" "logging_account_parameter" {
  name  = "logging_account"
  type  = "String"
  value = var.logging_account
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# automation account dl SSM
resource "aws_ssm_parameter" "automation_account_dl_parameter" {
  name  = "automation_account_dl"
  type  = "String"
  value = var.automation_account_dl
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# cidr table index SSM
resource "aws_ssm_parameter" "cidr_table_index_parameter" {
  name  = "cidr_table_index"
  type  = "String"
  value = var.cidr_table_index
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# cidr table name SSM
resource "aws_ssm_parameter" "cidr_table_name_parameter" {
  name  = "cidr_table_name"
  type  = "String"
  value = var.cidr_table_name
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# create account parent id SSM
resource "aws_ssm_parameter" "create_account_parentid_parameter" {
  name  = "create_account_parentid"
  type  = "String"
  value = var.create_account_parentid
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# create case cc adress SSM
resource "aws_ssm_parameter" "create_case_ccadress_parameter" {
  name  = "create_case_ccadress"
  type  = "String"
  value = var.create_case_ccadress
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# dl Table Name SSM
resource "aws_ssm_parameter" "dl_table_name_parameter" {
  name  = "dlTableName"
  type  = "String"
  value = var.dl_table_name
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# failure operation dl SSM
resource "aws_ssm_parameter" "failure_operation_dl_parameter" {
  name  = "failure_operation_dl"
  type  = "String"
  value = var.failure_operation_dl
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# simaas operation dl SSM
resource "aws_ssm_parameter" "simaas_operation_dl_parameter" {
  name  = "simaas_operation_dl"
  type  = "String"
  value = var.simaas_operation_dl
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# iam mgmnt account SSM
resource "aws_ssm_parameter" "iam_mgmnt_account_parameter" {
  name  = "iam_mgmnt_account"
  type  = "String"
  value = var.iam_mgmnt_account
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# master account SSM
resource "aws_ssm_parameter" "master_account_parameter" {
  name  = "master_account"
  type  = "String"
  value = var.master_account
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# master admin role arn SSM
resource "aws_ssm_parameter" "master_admin_role_arn_parameter" {
  name  = "master_admin_role_arn"
  type  = "String"
  value = var.master_admin_role_arn
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# agent bucket SSM
resource "aws_ssm_parameter" "agent_bucket_parameter" {
  name  = "agent_bucket"
  type  = "String"
  value = var.agent_bucket
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# domain join linux pre URL SSM
resource "aws_ssm_parameter" "domainjoin_linux_pre_url_parameter" {
  name  = "domainjoin_linuxpreURL"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/domainjoin/linux/domain_join_pre_requisite.sh\""
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# domain join linux main URL SSM
resource "aws_ssm_parameter" "domainjoin_linux_main_url_parameter" {
  name  = "domainjoin_linuxmainURL"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/domainjoin/linux/master_domain_joinScript.sh\""
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# domain join linux path SSM
resource "aws_ssm_parameter" "domainjoin_linux_path_parameter" {
  name  = "domainjoin_linuxpath"
  type  = "String"
  value = "/tmp"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# domain join linux pre filename SSM
resource "aws_ssm_parameter" "domainjoin_linux_pre_filename_parameter" {
  name  = "domainjoin_linux_prefilename"
  type  = "String"
  value = "domain_join_pre_requisite.sh"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# domain join linux main filename SSM
resource "aws_ssm_parameter" "domainjoin_linux_main_filename_parameter" {
  name  = "domainjoin_linux_mainfilename"
  type  = "String"
  value = "master_domain_joinScript.sh"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# domain join windows URL US SSM
resource "aws_ssm_parameter" "domainjoin_windows_url_us_parameter" {
  name  = "domainjoin_windowsURL_us"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/domainjoin/windows/US/domain-join.ps1\""
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# domain join windows URL EU SSM
resource "aws_ssm_parameter" "domainjoin_windows_url_eu_parameter" {
  name  = "domainjoin_windowsURL_eu"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/domainjoin/windows/EU/domain-join.ps1\""
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# domain join windows URL SG SSM
resource "aws_ssm_parameter" "domainjoin_windows_url_sg_parameter" {
  name  = "domainjoin_windowsURL_sg"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/domainjoin/windows/SG/domain-join.ps1\""
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# domain join windows path SSM
resource "aws_ssm_parameter" "domainjoin_windows_path_parameter" {
  name  = "domainjoin_windows_path"
  type  = "String"
  value = "C:\\Windows\\Temp"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# domain join windows filename SSM
resource "aws_ssm_parameter" "domainjoin_windows_filename_parameter" {
  name  = "domainjoin_windows_filename"
  type  = "String"
  value = "domain-join.ps1"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform agent bucket SSM
resource "aws_ssm_parameter" "platform_agent_bucket_parameter" {
  name  = "platform_agent_bucket"
  type  = "String"
  value = var.agent_bucket
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform linux dir path SSM
resource "aws_ssm_parameter" "platform_linux_dirpath_parameter" {
  name  = "platform_linux_dirpath"
  type  = "String"
  value = "/var/tmp"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform win dir path SSM
resource "aws_ssm_parameter" "platform_win_dirpath_parameter" {
  name  = "platform_win_dirpath"
  type  = "String"
  value = "C:\\Windows\\Temp"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform execution timeout SSM
resource "aws_ssm_parameter" "platform_execution_timeout_parameter" {
  name  = "platform_execution_timeout"
  type  = "String"
  value = "3600"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform pub flexera linux path SSM
resource "aws_ssm_parameter" "platform_pub_flexera_linuxpath_parameter" {
  name  = "platform_pub_flexera_linuxpath"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/public-agent/flexera/linux/DownloadAndInstallFlexeraAgentLinux.sh\""
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform pvt flexera linux path US SSM
resource "aws_ssm_parameter" "platform_pvt_flexera_linuxpath_us_parameter" {
  name  = "platform_pvt_flexera_linuxpath_us"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/private-agent/flexera/linux/US/DownloadAndInstallFlexeraAgentLinux.sh\""
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform pvt flexera linux path EU SSM
resource "aws_ssm_parameter" "platform_pvt_flexera_linuxpath_eu_parameter" {
  name  = "platform_pvt_flexera_linuxpath_eu"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/private-agent/flexera/linux/EU/DownloadAndInstallFlexeraAgentLinux.sh\""
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform pvt flexera linux path SG SSM
resource "aws_ssm_parameter" "platform_pvt_flexera_linuxpath_sg_parameter" {
  name  = "platform_pvt_flexera_linuxpath_sg"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/private-agent/flexera/linux/SG/DownloadAndInstallFlexeraAgentLinux.sh\""
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform flexera linuxfilename SSM
resource "aws_ssm_parameter" "platform_flexera_linux_filename_parameter" {
  name  = "platform_flexera_linux_filename"
  type  = "String"
  value = "./DownloadAndInstallFlexeraAgentLinux.sh"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform pub flexera win path SSM
resource "aws_ssm_parameter" "platform_pub_flexera_winpath_parameter" {
  name  = "platform_pub_flexera_winpath"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/public-agent/flexera/windows/DownloadAndInstallFlexeraAgent.PS1\""
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform private flexera win path US SSM
resource "aws_ssm_parameter" "platform_pvt_flexera_winpath_us_parameter" {
  name  = "platform_pvt_flexera_winpath_us"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/private-agent/flexera/windows/US/DownloadAndInstallFlexeraAgent.PS1\""
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform private flexera win path EU SSM
resource "aws_ssm_parameter" "platform_pvt_flexera_winpath_eu_parameter" {
  name  = "platform_pvt_flexera_winpath_eu"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/private-agent/flexera/windows/EU/DownloadAndInstallFlexeraAgent.PS1\""
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform private flexera win path SG SSM
resource "aws_ssm_parameter" "platform_pvt_flexera_winpath_sg_parameter" {
  name  = "platform_pvt_flexera_winpath_sg"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/private-agent/flexera/windows/SG/DownloadAndInstallFlexeraAgent.PS1\""
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform flexera win filename SSM
resource "aws_ssm_parameter" "platform_flexera_win_filename_parameter" {
  name  = "platform_flexera_win_filename"
  type  = "String"
  value = ".\\DownloadAndInstallFlexeraAgent.PS1"
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# platform pub falcon linux path SSM
resource "aws_ssm_parameter" "platform_pub_falcon_linuxpath_parameter" {
  name  = "platform_pub_falcon_linuxpath"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/public-agent/falcon/linux/downloadandinstallfalcon.sh\""
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# platform pvt falcon linux path SSM
resource "aws_ssm_parameter" "platform_pvt_falcon_linuxpath_parameter" {
  name  = "platform_pvt_falcon_linuxpath"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/private-agent/falcon/linux/downloadandinstallfalcon.sh\""
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# platform falcon linux filename SSM
resource "aws_ssm_parameter" "platform_falcon_linux_filename_parameter" {
  name  = "platform_falcon_linux_filename"
  type  = "String"
  value = "./downloadandinstallfalcon.sh"
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# platform pub falcon win path SSM
resource "aws_ssm_parameter" "platform_pub_falcon_winpath_parameter" {
  name  = "platform_pub_falcon_winpath"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/public-agent/falcon/windows/downloadandinstallfalcon.ps1\""
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform pvt falcon win path SSM
resource "aws_ssm_parameter" "platform_pvt_falcon_winpath_parameter" {
  name  = "platform_pvt_falcon_winpath"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/private-agent/falcon/windows/downloadandinstallfalcon.ps1\""
} 

# platform falcon win filename SSM
resource "aws_ssm_parameter" "platform_falcon_win_filename_parameter" {
  name  = "platform_falcon_win_filename"
  type  = "String"
  value = ".\\downloadandinstallfalcon.ps1"
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# platform pub rapid7 linux path SSM
resource "aws_ssm_parameter" "platform_pub_rapid7_linuxpath_parameter" {
  name  = "platform_pub_rapid7_linuxpath"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/public-agent/rapid7/linux/DownloadAndInstallRapid7AgentLinux.sh\""
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# platform pvt rapid7 linux path SSM
resource "aws_ssm_parameter" "platform_pvt_rapid7_linuxpath_parameter" {
  name  = "platform_pvt_rapid7_linuxpath"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/private-agent/rapid7/linux/DownloadAndInstallRapid7AgentLinux.sh\""
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# platform rapid7 linux filename SSM
resource "aws_ssm_parameter" "platform_rapid7_linux_filename_parameter" {
  name  = "platform_rapid7_linux_filename"
  type  = "String"
  value = "./DownloadAndInstallRapid7AgentLinux.sh"
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# platform pub rapid7 win path SSM
resource "aws_ssm_parameter" "platform_pub_rapid7_winpath_parameter" {
  name  = "platform_pub_rapid7_winpath"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/public-agent/rapid7/windows/DownloadAndInstallRapid7Agent.PS1\""
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# platform pvt rapid7 win path SSM
resource "aws_ssm_parameter" "platform_pvt_rapid7_winpath_parameter" {
  name  = "platform_pvt_rapid7_winpath"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/private-agent/rapid7/windows/DownloadAndInstallRapid7Agent.PS1\""
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform rapid7 win filename SSM
resource "aws_ssm_parameter" "platform_rapid7_win_filename_parameter" {
  name  = "platform_rapid7_win_filename"
  type  = "String"
  value = ".\\DownloadAndInstallRapid7Agent.PS1"
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# platform pub cloudhealth linux path SSM
resource "aws_ssm_parameter" "platform_pub_ch_linuxpath_parameter" {
  name  = "platform_pub_ch_linuxpath"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/public-agent/cloudhealth/linux/downloadandinstallcloudhealth.sh\""
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# platform pvt cloudhealth linux path SSM
resource "aws_ssm_parameter" "platform_pvt_ch_linuxpath_parameter" {
  name  = "platform_pvt_ch_linuxpath"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/private-agent/cloudhealth/linux/downloadandinstallcloudhealth.sh\""
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# platform ch linux filename SSM
resource "aws_ssm_parameter" "platform_ch_linux_filename_parameter" {
  name  = "platform_ch_linux_filename"
  type  = "String"
  value = "./downloadandinstallcloudhealth.sh"
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# platform pub cloudhealth win path SSM
resource "aws_ssm_parameter" "platform_pub_ch_winpath_parameter" {
  name  = "platform_pub_ch_winpath"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/public-agent/cloudhealth/windows/downloadandinstallcloudhealth.ps1\""
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# platform pvt cloudhealth win path SSM
resource "aws_ssm_parameter" "platform_pvt_ch_winpath_parameter" {
  name  = "platform_pvt_ch_winpath"
  type  = "String"
  value = "\"https://${var.agent_bucket}.s3.amazonaws.com/private-agent/cloudhealth/windows/downloadandinstallcloudhealth.ps1\""
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# platform ch win filename SSM
resource "aws_ssm_parameter" "platform_ch_win_filename_parameter" {
  name  = "platform_ch_win_filename"
  type  = "String"
  value = ".\\downloadandinstallcloudhealth.ps1"
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# success operation dl SSM
resource "aws_ssm_parameter" "success_operation_dl_parameter" {
  name  = "success_operation_dl"
  type  = "String"
  value = var.success_operation_dl
  tags = {
    "platform_donotdelete" = "yes"
  }
} 

# whitelisted regions SSM
resource "aws_ssm_parameter" "whitelisted_regions_parameter" {
  name  = "whitelisted_regions"
  type  = "String"
  value = var.whitelisted_regions
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# whitelisted regions private SSM
resource "aws_ssm_parameter" "whitelisted_regions_private_parameter" {
  name  = "whitelisted_regions_private"
  type  = "String"
  value = var.whitelisted_regions_private
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# whitelisted regions public SSM
resource "aws_ssm_parameter" "whitelisted_regions_public_parameter" {
  name  = "whitelisted_regions_public"
  type  = "String"
  value = var.whitelisted_regions_public
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# whitelisted custom regions SSM
resource "aws_ssm_parameter" "whitelisted_custom_regions_parameter" {
  name  = "whitelisted_custom_regions"
  type  = "String"
  value = var.whitelisted_custom_regions
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Private whitelisted region SSM
resource "aws_ssm_parameter" "private_whitelisted_region_parameter" {
  name  = "Private_whitelisted_region"
  type  = "StringList"
  value = var.private_whitelisted_region
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Public whitelisted region SSM
resource "aws_ssm_parameter" "public_whitelisted_region_parameter" {
  name  = "Public_whitelisted_region"
  type  = "String"
  value = var.public_whitelisted_region
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# TOE Complaint OS Flavours SSM
resource "aws_ssm_parameter" "toe_compliant_os_parameter" {
  name  = "TOE_Complaint_OS_Flavours"
  type  = "StringList"
  value = var.toe_compliant_os
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# TOE Complaint OS Flavours SSM
resource "aws_ssm_parameter" "toe_compliant_os_private_parameter" {
  name  = "TOE_Complaint_OS_Flavours_Private"
  type  = "StringList"
  value = var.toe_compliant_os_private
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# TOE Complaint OS Flavours SSM
resource "aws_ssm_parameter" "toe_compliant_os_public_parameter" {
  name  = "TOE_Complaint_OS_Flavours_Public"
  type  = "StringList"
  value = var.toe_compliant_os_public
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Unit Test Approver SSM
resource "aws_ssm_parameter" "unit_test_approver_parameter" {
  name  = "UnitTestApprover"
  type  = "StringList"
  value = var.unit_test_approver
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# ami owner account SSM
resource "aws_ssm_parameter" "ami_owner_account_parameter" {
  name  = "ami_owner_account"
  type  = "StringList"
  value = var.ami_owner_account
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# ami tags SSM
resource "aws_ssm_parameter" "ami_tags_parameter" {
  name  = "ami_tags"
  type  = "StringList"
  value = var.ami_tags
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# sender id SSM
resource "aws_ssm_parameter" "sender_id_parameter" {
  name  = "sender_id"
  type  = "String"
  value = var.sender_id
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# execution timeout SSM
resource "aws_ssm_parameter" "execution_timeout_parameter" {
  name  = "execution_timeout"
  type  = "String"
  value = "3600"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# master account name SSM
resource "aws_ssm_parameter" "master_account_name_parameter" {
  name  = "master_account_name"
  type  = "String"
  value = var.master_account_name
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform cloudhealth externalid SSM
resource "aws_ssm_parameter" "platform_cloudhealth_external_id_parameter" {
  name  = "platform_cloudhealth_external_id"
  type  = "String"
  value = var.platform_cloudhealth_external_id
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform cloudhealth account SSM
resource "aws_ssm_parameter" "platform_cloudhealth_account_parameter" {
  name  = "platform_cloudhealth_account"
  type  = "String"
  value = var.platform_cloudhealth_account
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# platform ou decommission SSM
resource "aws_ssm_parameter" "platform_ou_decommission_parameter" {
  name  = "platform_ou_decommission"
  type  = "String"
  value = var.platform_ou_decommission
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Hosted zone Id US SSM
resource "aws_ssm_parameter" "hostedzone_id_us_parameter" {
  name  = "hostedzone_id_us"
  type  = "StringList"
  value = var.hostedzone_id_us
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Hosted zone Id EU SSM
resource "aws_ssm_parameter" "hostedzone_id_eu_parameter" {
  name  = "hostedzone_id_eu"
  type  = "StringList"
  value = var.hostedzone_id_eu
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Hosted zone Id SG SSM
resource "aws_ssm_parameter" "hostedzone_id_sg_parameter" {
  name  = "hostedzone_id_sg"
  type  = "StringList"
  value = var.hostedzone_id_sg  
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Shared Services ID SSM
resource "aws_ssm_parameter" "shared_services_account_id_parameter" {
  name  = "shared_services_account_id"
  type  = "String"
  value = var.shared_services_account_id
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Network Product SSM
resource "aws_ssm_parameter" "platform_network_product_id_parameter" {
  name  = "platform_network_product_id"
  type  = "String"
  value = var.platform_network_product_id
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# AVM Product id
resource "aws_ssm_parameter" "platform_avm_product_id_parameter" {
  name  = "AVMproductid"
  description = "AVMproductid"
  type  = "String"
  value = var.platform_avm_product_id
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Network Table SSM
resource "aws_ssm_parameter" "platform_network_table_name_parameter" {
  name  = "platform_network_table_name"
  type  = "String"
  value = var.platform_network_table_name
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# ATL TF Backend S3 Bucket
resource "aws_ssm_parameter" "platform_atl_tf_backends3bucket_parameter" {
  name  = "platform_atl_tf_backends3bucket"
  type  = "String"
  value = var.atl_terraform_backend_bucket_name
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# ATL TF Backend DynamoDB
resource "aws_ssm_parameter" "platform_atl_tf_backenddynamodb_parameter" {
  name  = "platform_atl_tf_backenddynamodb"
  type  = "String"
  value = var.atl_terraform_backend_dynamodb
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SSO Instnc Arn SSM
resource "aws_ssm_parameter" "sso_instance_arn_parameter" {
  name  = "sso_instance_arn"
  type  = "String"
  value = var.sso_instance_arn
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SSO IRM Access Arn
resource "aws_ssm_parameter" "irm_permission_set_parameter" {
  name  = "irm_permission_set"
  type  = "String"
  value = var.irm_permission_set
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SSO Admin ARN
resource "aws_ssm_parameter" "admin_permission_set_parameter" {
  name  = "admin_permission_set"
  type  = "String"
  value = var.admin_permission_set
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SSO ReadOnly Access Arn
resource "aws_ssm_parameter" "platform_readonly_permission_set_parameter" {
  name  = "platform_readonly_permission_set"
  type  = "String"
  value = var.platform_readonly_permission_set
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SSO BusinessCustom Access Arn
resource "aws_ssm_parameter" "Businesscustom_permission_set_parameter" {
  name  = "BusinessCustom_permission_set"
  type  = "String"
  value = var.BusinessCustom_permission_set
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SSO Platfrom Group Arn
resource "aws_ssm_parameter" "platform_readonly_group_parameter" {
  name  = "platform_readonly_group"
  type  = "String"
  value = var.platform_readonly_group
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SSO Permission Set Arn
resource "aws_ssm_parameter" "permission_set_arn_parameter" {
  name  = "permission_set_arn"
  type  = "String"
  value = var.permission_set_arn
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SSO Principal Id
resource "aws_ssm_parameter" "platform_irm_group_parameter" {
  name  = "platform_irm_group"
  type  = "String"
  value = var.platform_irm_group
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SSO Itom ReadOnly Group ARN
resource "aws_ssm_parameter" "itom_readonly_group_parameter" {
  name  = "itom_readonly_group"
  type  = "String"
  value = var.itom_readonly_group
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SSO Itom ReadOnly permission Set
resource "aws_ssm_parameter" "itom_readonly_permission_set_parameter" {
  name  = "itom_readonly_permission_set"
  type  = "String"
  value = var.itom_readonly_permission_set
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Non Routable CIDR
resource "aws_ssm_parameter" "non_routable_cidr_parameter" {
  name  = "NonRoutableCIDR"
  type  = "String"
  value = "10.175.128.0/18"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Non Routable subnet az1
resource "aws_ssm_parameter" "non_routable_subnet_az1_parameter" {
  name  = "NonRoutableSubnetAZ1"
  type  = "String"
  value = "10.175.128.0/19"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Non Routable subnet az2
resource "aws_ssm_parameter" "non_routable_subnet_az2_parameter" {
  name  = "NonRoutableSubnetAZ2"
  type  = "String"
  value = "10.175.160.0/19"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# team email dl
resource "aws_ssm_parameter" "team_email_dl_parameter" {
  name  = "team_email_dl"
  type  = "String"
  value = var.TeamEmailDL
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# iam rotation period
resource "aws_ssm_parameter" "iam_rotation_period_parameter" {
  name  = "iam_rotation_period"
  type  = "String"
  value = var.RotationPeriod
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# iam warn period
resource "aws_ssm_parameter" "iam_warn_period_parameter" {
  name  = "iam_warn_period"
  type  = "String"
  value = var.WarnPeriod
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# ContributorexternalroleSSM
resource "aws_ssm_parameter" "contributor_role_arn_parameter" {
  name  = "platform_contributorexternalrolearn"
  type  = "String"
  value = var.platformcontributorexternalrolearn
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# MastercontributorrolearnSSM
resource "aws_ssm_parameter" "master_contributor_role_arn_parameter" {
  name  = "platform_mastercontributorrolearn"
  type  = "String"
  value = var.platformmastercontributorrolearn
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# DatalakeidSSM
resource "aws_ssm_parameter" "datalakeid_parameter" {
  name  = "platform_datalakeid"
  type  = "String"
  value = var.platformdatalakeid
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# snow sgc account
resource "aws_ssm_parameter" "snow_sgc_account_parameter" {
  name  = "SNOW_SGC_Account"
  type  = "String"
  value = var.SNOWSGCAccountID
  tags = {
    "platform_donotdelete" = "yes"
  }
}

