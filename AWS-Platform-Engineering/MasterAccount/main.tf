module "ami_tagging" {
  source = "./modules/AMITagging"

  role_arn = module.iam_master_account.platform_admin_role_arn
 
  providers = {
    aws = aws.us-east-1
   }

  depends_on = [module.iam_master_account]
}

module "backup_jobs" {
  source = "./modules/BackupJobs"

  backup_jobs_report_event_rule_name = var.backup_jobs_report_event_rule_name
  failed_backup_jobs_report_event_rule_name = var.failed_backup_jobs_report_event_rule_name
  role_arn = module.iam_master_account.platform_admin_role_arn
  master_account = var.master_account
  org_id =  var.org_id
  
  providers = {
    aws = aws.us-east-1
   }

  depends_on = [module.iam_master_account]
}

module "cis_report_latest_ami" {
  source = "./modules/CISReportLatestAMI"

  env_type = var.env_type
  cis_pro_tools = var.cis_pro_tools
  cis_ami_reports = var.cis_ami_reports
  role_arn = module.iam_master_account.platform_admin_role_arn
  master_account = var.master_account
  vpc_flow_bucket_env_type = var.vpc_flow_bucket_env_type

  providers = {
    aws = aws.us-east-1
   }

  depends_on = [module.iam_master_account]
}

module "cloudwatch_event_rules_us-east-1" {
  source = "./modules/CloudWatchEventRules"

  irm_account_id = var.irm_account_id
  irm_environment = var.irm_environment
  master_account = var.master_account

  providers = {
    aws = aws.us-east-1
   }
}

module "cloudwatch_event_rules_eu-west-1" {
  source = "./modules/CloudWatchEventRules" 

  irm_account_id = var.irm_account_id
  irm_environment = var.irm_environment
  master_account = var.master_account

  providers = {
    aws = aws.eu-west-1
   }
}

module "cloudwatch_event_rules_us-east-2" {
  source = "./modules/CloudWatchEventRules"

  irm_account_id = var.irm_account_id
  irm_environment = var.irm_environment
  master_account = var.master_account

  providers = {
    aws = aws.us-east-2
   }
}

module "cloudwatch_event_rules_us-west-1" {
  source = "./modules/CloudWatchEventRules" 

  irm_account_id = var.irm_account_id
  irm_environment = var.irm_environment
  master_account = var.master_account

  providers = {
    aws = aws.us-west-1
   }
}

module "cloudwatch_event_rules_us-west-2" {
  source = "./modules/CloudWatchEventRules"

  irm_account_id = var.irm_account_id
  irm_environment = var.irm_environment
  master_account = var.master_account

  providers = {
    aws = aws.us-west-2
   }
}

module "cloudwatch_event_rules_ap-south-1" {
  source = "./modules/CloudWatchEventRules"

  irm_account_id = var.irm_account_id
  irm_environment = var.irm_environment
  master_account = var.master_account

  providers = {
    aws = aws.ap-south-1
   }
}

module "cloudwatch_event_rules_ap-southeast-2" {
  source = "./modules/CloudWatchEventRules"

  irm_account_id = var.irm_account_id
  irm_environment = var.irm_environment
  master_account = var.master_account

  providers = {
    aws = aws.ap-southeast-2
   }
}

module "cloudwatch_event_rules_ap-southeast-1" {
  source = "./modules/CloudWatchEventRules"

  irm_account_id = var.irm_account_id
  irm_environment = var.irm_environment
  master_account = var.master_account

  providers = {
    aws = aws.ap-southeast-1
   }
}

module "cloudwatch_event_rules_eu-central-1" {
  source = "./modules/CloudWatchEventRules"

  irm_account_id = var.irm_account_id
  irm_environment = var.irm_environment
  master_account = var.master_account

  providers = {
    aws = aws.eu-central-1
   }
}

module "cloudwatch_event_rules_eu-west-2" {
  source = "./modules/CloudWatchEventRules"

  irm_account_id = var.irm_account_id
  irm_environment = var.irm_environment
  master_account = var.master_account

  providers = {
    aws = aws.eu-west-2
   }
}

module "cloudwatch_event_rules_eu-north-1" {
  source = "./modules/CloudWatchEventRules"

  irm_account_id = var.irm_account_id
  irm_environment = var.irm_environment
  master_account = var.master_account

  providers = {
    aws = aws.eu-north-1
   }
}

module "cloudwatch_event_rules_ap-northeast-1" {
  source = "./modules/CloudWatchEventRules"

  irm_account_id = var.irm_account_id
  irm_environment = var.irm_environment
  master_account = var.master_account

  providers = {
    aws = aws.ap-northeast-1
   }
}

module "cloudwatch_event_rules_ca-central-1" {
  source = "./modules/CloudWatchEventRules" 

  irm_account_id = var.irm_account_id
  irm_environment = var.irm_environment
  master_account = var.master_account

  providers = {
    aws = aws.ca-central-1
   }
}

module "cloudwatch_event_rules_ap-northeast-2" {
  source = "./modules/CloudWatchEventRules"

  irm_account_id = var.irm_account_id
  irm_environment = var.irm_environment
  master_account = var.master_account

  providers = {
    aws = aws.ap-northeast-2
   }
}

module "dynamodb_tables" {
  source = "./modules/DynamoDB"

  atl_terraform_backend_dynamodb = var.atl_terraform_backend_dynamodb
  
  providers = {
    aws = aws.us-east-1
   }
}

module "daily_instance_details_and_cost_report" {
  source = "./modules/DailyInstanceCostReport"

  master_account = var.master_account
  master_admin_role_arn = var.master_admin_role_arn

  providers = {
    aws = aws.us-east-1
   }
}

module "iam_master_account" {
  source = "./modules/IAM"

  wiz_external_id = var.wiz_external_id
  wiz_orchestrator_account_id = var.wiz_orchestrator_account_id
  wiz_access_account_id = var.wiz_access_account_id
  snow_itom_prod_account = var.snow_itom_prod_account
  irm_account_id = var.irm_account_id
  irm_environment = var.irm_environment
  cloudhelth_bucket_name = var.cloudhelth_bucket_name
  atl_terraform_backend_bucket_name = var.atl_terraform_backend_bucket_name
  atl_terraform_backend_dynamodb = var.atl_terraform_backend_dynamodb
  platform_cloudhealth_account = var.platform_cloudhealth_account
  platform_cloudhealth_external_id = var.platform_cloudhealth_external_id
  wiz_env_type = var.wiz_env_type
  env_type = var.env_type
  master_account = var.master_account
  DynatraceRoleNameMaster = var.DynatraceRoleNameMaster
  DynatraceAccountID = var.DynatraceAccountID
  SNOWSGCAccountID = var.SNOWSGCAccountID
  billing_bucket_name = var.billing_bucket_name
  
  providers = {
    aws = aws.us-east-1
   }
}

module "iam_change_notifications" {
  source = "./modules/IAMChangesNotifications"

  subscription_email = var.subscription_email
  cloudtrail_log_group_name = var.cloudtrail_log_group_name 
  iam_change_sns_topic_name = var.iam_change_sns_topic_name
  iam_changes_metric_filter_name = var.iam_changes_metric_filter_name
  master_account = var.master_account
  org_id = var.org_id
  env_type = var.env_type

  providers = {
    aws = aws.us-east-1
   }
}

module "instance_scheduler" {
  source = "./modules/InstanceScheduler"
  
  instancescheduler_template_version = var.instancescheduler_template_version
  role_arn = module.iam_master_account.platform_admin_role_arn
  requests_layer = module.lambda_layers.requests_lambda_layer_arn

  providers = {
    aws = aws.us-east-1
   }

  depends_on = [module.iam_master_account]
}

module "ipaws_automation" {
  source = "./modules/IPAWS"

  env_type = var.env_type
  ipaws_vpc_cidr = var.ipaws_vpc_cidr
  ipaws_pvt_subnet_cidr_1 = var.ipaws_pvt_subnet_cidr_1
  ipaws_pvt_subnet_cidr_2 = var.ipaws_pvt_subnet_cidr_2
  ipaws_pub_subnet_cidr_1 = var.ipaws_pub_subnet_cidr_1
  ipaws_pub_subnet_cidr_2 = var.ipaws_pub_subnet_cidr_2 
  role_arn = module.iam_master_account.platform_admin_role_arn
  requests_layer = module.lambda_layers.requests_lambda_layer_arn
  cryptography_layer = module.lambda_layers.cryptography_lambda_layer_arn
  msal_layer = module.lambda_layers.msal_lambda_layer_arn
  pyjwt_layer = module.lambda_layers.pyjwt_lambda_layer_arn
  cffi_layer = module.lambda_layers.cffi_lambda_layer_arn

  providers = {
    aws = aws.us-east-1
   }

  depends_on = [module.iam_master_account, module.lambda_layers]
}

module "lambda_functions" {
  source = "./modules/LambdaFunctions"
 
  env_type = var.env_type
  master_account = var.master_account
  role_arn = module.iam_master_account.platform_admin_role_arn
  requests_layer = module.lambda_layers.requests_lambda_layer_arn
  vpc_flow_bucket_env_type = var.vpc_flow_bucket_env_type
  master_admin_role_arn = var.master_admin_role_arn


  providers = {
    aws = aws.us-east-1
   }

  depends_on = [module.iam_master_account, module.lambda_layers]
}

module "lambda_layers" {
  source = "./modules/LambdaLayers"
 
  providers = {
    aws = aws.us-east-1
   }
}

module "patching" {
  source = "./modules/Patching"

  patching_template_version = var.patching_template_version
  patching_report_sns_topic_name = var.patching_report_sns_topic_name
  platform_patch_report_monthly_event_rule_name = var.platform_patch_report_monthly_event_rule_name
  master_inventory_state_machine_event_rule_name = var.master_inventory_state_machine_event_rule_name
  account_details_event_rule_name = var.account_details_event_rule_name
  subscription_email_1 = var.subscription_email_1
  subscription_email_2 = var.subscription_email_2
  subscription_email_3 = var.subscription_email_3
  role_arn = module.iam_master_account.platform_admin_role_arn
  master_account = var.master_account
  org_id =  var.org_id
  release_bucket_name =  var.release_bucket_name
  env_type = var.env_type
  
  providers = {
    aws = aws.us-east-1
  }

  depends_on = [module.iam_master_account]
}

module "pitr_notifications" {
  source = "./modules/PITRDynamoDBNotifications"

  subscription_email_1 = var.subscription_email_1
  subscription_email_2 = var.subscription_email_2
  subscription_email_3 = var.subscription_email_3
  dynamodb_pitr_event_rule_name = var.dynamodb_pitr_event_rule_name
  pitr_change_sns_topic_name = var.pitr_change_sns_topic_name
  master_account = var.master_account
  org_id =  var.org_id
  env_type = var.env_type
  
  providers = {
    aws = aws.us-east-1
  }
}

module "s3_buckets" {
  source = "./modules/S3Buckets"

  env_type = var.env_type

  providers = {
    aws = aws.us-east-1
   }
}

module "scim_sso_assigner" {
  source = "./modules/SCIMSSOAssigner"

  role_arn = module.iam_master_account.platform_admin_role_arn
  requests_layer = module.lambda_layers.requests_lambda_layer_arn
  
  providers = {
    aws = aws.us-east-1
   }

  depends_on = [module.iam_master_account, module.lambda_layers]
}

module "service_catalog" {
  source = "./modules/ServiceCatalog"

  AVMTemplateVersion = var.AVMTemplateVersion
  NewAVMTemplateVersion = var.NewAVMTemplateVersion
  AVMServiceCatalogRoleARN = var.AVMServiceCatalogRoleARN
  AVMServiceCatalogServiceRoleARN = var.AVMServiceCatalogServiceRoleARN
  AVMServiceCatalogOperatorRoleARN = var.AVMServiceCatalogOperatorRoleARN
  ControlTowerPortfolioARN = var.ControlTowerPortfolioARN
  NetworkTemplateVersion = var.NetworkTemplateVersion
  release_bucket_name = var.release_bucket_name
  
  providers = {
    aws = aws.us-east-1
   }
}

module "snow_to_aws_at_shell_integration" {
  source = "./modules/SnowToAWSAtShellIntegration"

  env_type = var.env_type

  role_arn = module.iam_master_account.platform_admin_role_arn
  master_account = var.master_account
  vpc_flow_bucket_env_type = var.vpc_flow_bucket_env_type


  providers = {
    aws = aws.us-east-1
   }

  depends_on = [module.iam_master_account]
}

module "snow_trb_automation" { 
  source = "./modules/SnowTRBAutomation"

  trb_env_type = var.trb_env_type
  role_arn = module.iam_master_account.platform_admin_role_arn
  master_account = var.master_account
  
  providers = {
    aws = aws.us-east-1
   }

  depends_on = [module.iam_master_account]
}

module "ssm" {
  source = "./modules/SSM"
  env_type = var.env_type
  af_product_id = var.af_product_id
  release_S3_bucket = var.release_S3_bucket
  release_folder = var.release_folder
  shared_directory_id_us = var.shared_directory_id_us
  shared_directory_name_us = var.shared_directory_name_us
  shared_directory_ip_us = var.shared_directory_ip_us
  shared_directory_id_eu = var.shared_directory_id_eu
  shared_directory_name_eu = var.shared_directory_name_eu
  shared_directory_ip_eu = var.shared_directory_ip_eu
  shared_directory_id_singapore = var.shared_directory_id_singapore
  shared_directory_name_singapore = var.shared_directory_name_singapore
  shared_directory_ip_singapore = var.shared_directory_ip_singapore
  private_production_ou = var.private_production_ou
  private_staging_ou = var.private_staging_ou
  private_exception_ou = var.private_exception_ou
  public_staging_ou = var.public_staging_ou
  public_production_ou = var.public_production_ou
  public_exception_ou = var.public_exception_ou
  managed_services_beagile_ou = var.managed_services_beagile_ou
  data_management_ou = var.data_management_ou
  hybrid_account_ou = var.hybrid_account_ou
  migration_account_ou = var.migration_account_ou
  root_ou = var.root_ou
  audit_account = var.audit_account
  audit_account_admin_role_arn = var.audit_account_admin_role_arn
  logging_account = var.logging_account
  automation_account_dl = var.automation_account_dl
  cidr_table_index = var.cidr_table_index
  cidr_table_name = var.cidr_table_name
  create_account_parentid = var.create_account_parentid
  create_case_ccadress = var.create_case_ccadress
  dl_table_name = var.dl_table_name
  iam_mgmnt_account = var.iam_mgmnt_account
  master_admin_role_arn = var.master_admin_role_arn
  agent_bucket = var.agent_bucket
  success_operation_dl = var.success_operation_dl
  unit_test_approver = var.unit_test_approver
  master_account_name = var.master_account_name
  platform_ou_decommission = var.platform_ou_decommission
  hostedzone_id_us = var.hostedzone_id_us
  hostedzone_id_eu = var.hostedzone_id_eu
  hostedzone_id_sg = var.hostedzone_id_sg
  shared_services_account_id = var.shared_services_account_id
  platform_network_product_id = var.platform_network_product_id
  platform_network_table_name = var.platform_network_table_name
  atl_terraform_backend_bucket_name = var.atl_terraform_backend_bucket_name
  atl_terraform_backend_dynamodb = var.atl_terraform_backend_dynamodb
  sso_instance_arn = var.sso_instance_arn
  irm_permission_set = var.irm_permission_set
  admin_permission_set = var.admin_permission_set
  platform_readonly_permission_set = var.platform_readonly_permission_set
  BusinessCustom_permission_set = var.BusinessCustom_permission_set
  platform_readonly_group = var.platform_readonly_group
  permission_set_arn = var.permission_set_arn
  platform_irm_group = var.platform_irm_group
  itom_readonly_group = var.itom_readonly_group
  itom_readonly_permission_set = var.itom_readonly_permission_set
  account_update_bucket = var.account_update_bucket
  account_details_table = var.account_details_table
  exception_ami_table = var.exception_ami_table
  admin_account = var.admin_account
  admin_dl = var.admin_dl
  failure_operation_dl = var.failure_operation_dl
  simaas_operation_dl = var.simaas_operation_dl
  master_account = var.master_account
  whitelisted_regions = var.whitelisted_regions
  whitelisted_regions_private = var.whitelisted_regions_private
  whitelisted_regions_public = var.whitelisted_regions_public
  whitelisted_custom_regions = var.whitelisted_custom_regions
  private_whitelisted_region = var.private_whitelisted_region
  public_whitelisted_region = var.public_whitelisted_region
  toe_compliant_os_private = var.toe_compliant_os_private
  toe_compliant_os_public = var.toe_compliant_os_public
  toe_compliant_os = var.toe_compliant_os
  ami_owner_account = var.ami_owner_account
  ami_tags = var.ami_tags
  sender_id = var.sender_id
  platform_cloudhealth_external_id = var.platform_cloudhealth_external_id
  platform_cloudhealth_account = var.platform_cloudhealth_account
  platform_avm_product_id = var.platform_avm_product_id
  TeamEmailDL = var.TeamEmailDL
  RotationPeriod = var.RotationPeriod
  WarnPeriod = var.WarnPeriod
  SNOWSGCAccountID = var.SNOWSGCAccountID
  platformcontributorexternalrolearn = var.platformcontributorexternalrolearn
  platformmastercontributorrolearn = var.platformmastercontributorrolearn
  platformdatalakeid = var.platformdatalakeid
  RootMonitoringExemptionDays = var.RootMonitoringExemptionDays
  providers = {
    aws = aws.us-east-1
   }
}

module "step_functions" {
  source = "./modules/StepFunctions"

  role_arn = module.iam_master_account.platform_admin_role_arn
  master_account = var.master_account

  providers = {
    aws = aws.us-east-1
   }

  depends_on = [module.iam_master_account]
}

module "transitgateway_automation" {
  source = "./modules/TGW"

  env_type = var.env_type
  tgw_vpc_cidr = var.tgw_vpc_cidr
  tgw_table = var.tgw_table
  tgw_id = var.tgw_id
  role_arn = module.iam_master_account.platform_admin_role_arn
  requests_layer = module.lambda_layers.requests_lambda_layer_arn
  tgw_pvt_sub_cidr_1 = var.tgw_pvt_sub_cidr_1
  tgw_pvt_sub_cidr_2 = var.tgw_pvt_sub_cidr_2
  tgw_pub_sub_cidr_1 = var.tgw_pub_sub_cidr_1
  tgw_pub_sub_cidr_2 = var.tgw_pub_sub_cidr_2
  master_account = var.master_account
  
  providers = {
    aws = aws.us-east-1
   }

  depends_on = [module.iam_master_account, module.lambda_layers]
}

module "update_dl_ddb" {
  source = "./modules/UpdateDLDDB"

  master_account = var.master_account

  providers = {
    aws = aws.us-east-1
   }
}

module "cloudwatch_alarms" {
  source = "./modules/CloudWatchAlarms"
  
  role_arn = module.iam_master_account.platform_admin_role_arn
  master_account = var.master_account

  providers = {
    aws = aws.us-east-1
   }

  depends_on = [module.iam_master_account]
}

module "cfn_ss_monitoring" {
  source = "./modules/CFNStackSetMonitoringDashboard"

  master_account = var.master_account

  providers = {
    aws = aws.us-east-1
   }
}

module "account_closure" {
  source = "./modules/AccountClosure"

  master_account = var.master_account
  admin_dl = var.admin_dl
  close_account_metric_filter_name = var.close_account_metric_filter_name

  providers = {
    aws = aws.us-east-1
   }
}

module "alt_contact_update" {
  source = "./modules/AltContactUpdate"

  master_account = var.master_account
  SecurityContactEmail = var.SecurityContactEmail
  SecurityContactName = var.SecurityContactName
  SecurityContactTitle = var.SecurityContactTitle
  SecurityContactPhone =  var.SecurityContactPhone
  OperationsContactEmail = var.OperationsContactEmail
  OperationsContactName = var.OperationsContactName
  OperationsContactTitle =  var.OperationsContactTitle
  OperationsContactPhone = var.OperationsContactPhone
  role_arn = var.master_admin_role_arn
  requests_layer = module.lambda_layers.requests_lambda_layer_arn

  providers = {
    aws = aws.us-east-1
   }

  depends_on = [module.lambda_layers]
}

module "iam_key_rotation_notifier" {
  source = "./modules/IAMKeyRotationNotifierSolution"

  master_account = var.master_account
  org_id = var.org_id
  sender_id = var.sender_id
  TeamEmailDL = var.TeamEmailDL
  RotationPeriod =  var.RotationPeriod
  WarnPeriod = var.WarnPeriod
  accountDetailTableName = var.accountDetailTableName

  providers = {
    aws = aws.us-east-1
   }
}

module "backup_monitoring" {
  source = "./modules/BackupMonitoring"

  master_account = var.master_account
  private_production_ou = var.private_production_ou
  private_staging_ou = var.private_staging_ou
  private_exception_ou = var.private_exception_ou
  public_staging_ou =  var.public_staging_ou
  public_production_ou = var.public_production_ou
  public_exception_ou = var.public_exception_ou
  managed_services_beagile_ou =  var.managed_services_beagile_ou
  data_management_ou = var.data_management_ou
  hybrid_account_ou = var.hybrid_account_ou
  migration_account_ou = var.migration_account_ou

  providers = {
    aws = aws.us-east-1
   }
}

module "root_activity_monitoring" {
  source = "./modules/RootActivityMonitoring"

  master_account = var.master_account
  RootMonitoringExemptionDays = var.RootMonitoringExemptionDays

  providers = {
    aws = aws.us-east-1
   }
}

module "cloud_intelligence_dashboard" {
  source = "./modules/CloudIntelligenceDashboard"

  master_account = var.master_account
  CIDashboardQuickSightUserName = var.CIDashboardQuickSightUserName
  cid_stack_name = var.cid_stack_name
  master_admin_role_arn =  var.master_admin_role_arn
  release_bucket_name = var.release_bucket_name
  
  providers = {
    aws = aws.us-east-1
   }
}

module "non_pim_role_report" {
  source = "./modules/NonPIMRoleReport"

  master_account = var.master_account
  audit_account = var.audit_account
  shared_services_account_id = var.shared_services_account_id
  logging_account = var.logging_account
  master_admin_role_arn = var.master_admin_role_arn

  providers = {
    aws = aws.us-east-1
   }
}

module "pim_role_report" {
  source = "./modules/PIMRolesReport"

  master_account = var.master_account
  audit_account = var.audit_account
  shared_services_account_id = var.shared_services_account_id
  logging_account = var.logging_account
  master_admin_role_arn = var.master_admin_role_arn
  request_dynamodb_table = var.request_dynamodb_table

  providers = {
    aws = aws.us-east-1
   }
}

module "non_flexera_report" {
  source = "./modules/FlexeraReport"

  master_account = var.master_account
  master_admin_role_arn = var.master_admin_role_arn
  providers = {
    aws = aws.us-east-1
   }
}

module "platform_lambda_automation_report" {
  source = "./modules/PlatformLambdaAutomationReport"

  master_account = var.master_account
  audit_account = var.audit_account
  shared_services_account_id = var.shared_services_account_id
  logging_account = var.logging_account
  master_admin_role_arn = var.master_admin_role_arn

  providers = {
    aws = aws.us-east-1
   }
}

module "vpc_cidr_nrs_exception_mgmnt" {
  source = "./modules/VPC-CIDR-NRS-ExceptionManagement"

  master_account = var.master_account
  SnowNerworkVPCIntegrationLogBucket = var.SnowNerworkVPCIntegrationLogBucket
  vpc_flow_bucket_env_type = var.vpc_flow_bucket_env_type
  role_arn = var.master_admin_role_arn

  providers = {
    aws = aws.us-east-1
   }
}

module "scp_exception_mgmnt" {
  source = "./modules/SCPExceptionManagement"
  
  master_account = var.master_account
  scp_env_type = var.scp_env_type
  role_arn = var.master_admin_role_arn
  private_production_ou = var.private_production_ou
  private_exception_ou = var.private_exception_ou
  public_production_ou = var.public_production_ou
  public_exception_ou = var.public_exception_ou
  hybrid_account_ou = var.hybrid_account_ou
  main_policy_id_private = var.main_policy_id_private
  main_policy_id_public = var.main_policy_id_public
  main_policy_id_hybrid = var.main_policy_id_hybrid
  titan_team_dl = var.titan_team_dl

  providers = {
    aws = aws.us-east-1
   }
}

module "sharr_master" {
  source = "./modules/SHARR"
  
  audit_account = var.audit_account

  providers = {
    aws = aws.us-east-1
   }
}

module "db_controls" {
  source = "./modules/DBControls"
  
  master_account = var.master_account
  env_type = var.env_type
  ScoreCardBucketName = var.ScoreCardBucketName
  DPSOMDL = var.DPSOMDL
  ScoreCardDBTableName = var.ScoreCardDBTableName
  ConfigAggregatorName = var.ConfigAggregatorName

  providers = {
    aws = aws.us-east-1
   }
}

module "Non_Interactive_Users" {
  source = "./modules/NonInteractiveUsers"

  api_stage = var.api_stage
  NonInteractiveUser_Lambda_ApiAuth_permission_statement_id = var.NonInteractiveUser_Lambda_ApiAuth_permission_statement_id
  NonInteractiveUser_Lambda_Invoker_permission_statement_id = var.NonInteractiveUser_Lambda_Invoker_permission_statement_id
  NonInteractiveUser_Lambda_Receiver_permission_statement_id = var.NonInteractiveUser_Lambda_Receiver_permission_statement_id
  cloudwatch_event_target_id = var.cloudwatch_event_target_id
  master_admin_role_arn = var.master_admin_role_arn

   providers = {
    aws = aws.us-east-1
   }
}

module "control_tower_iamrole_gaurdrail_dashboard" {
  source = "./modules/ControlTowerIAMRoleGaurdrails"

  control_tower_gaurdrails_stack_name = var.control_tower_gaurdrails_stack_name
  master_admin_role_arn =  var.master_admin_role_arn
  release_bucket_name = var.release_bucket_name
  
  providers = {
    aws = aws.us-east-1
   }
}

module "dns_zone_delegation" {
  source = "./modules/DNSZoneDelegationResources"

  master_account = var.master_account
  org_id =  var.org_id
  
  providers = {
    aws = aws.us-east-1
   }
}

module "amplify_url_redirect" {
  source = "./modules/AmplifyURLRedirect"
  env_type = var.env_type
}

module "monthly_innersource_tag_based_report" {
  source = "./modules/InnersourceTagsMonthlyReport"

  master_account = var.master_account
  master_admin_role_arn = var.master_admin_role_arn

  providers = {
    aws = aws.us-east-1
   }
}
