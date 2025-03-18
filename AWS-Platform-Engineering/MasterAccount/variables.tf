variable env_type {
    type = string
    description = "environment type dev/uat/prod"
}

variable trb_env_type {
    type = string
    description = "environment type dev/acceptance/prod"
} 

variable "tgw_id" {
  type = string
  description = "Enter tgw id"
}

variable wiz_env_type {
    type = string
    description = "environment type DEV/UAT/PROD"
}

variable cis_pro_tools {
    type = string
    description = "cis pro tools"
}

variable cis_ami_reports {
    type = string
    description = "cis ami reports"
}

variable platform_cloudhealth_account {
    type = string
    description = "platform cloudhealth account"
}

variable platform_cloudhealth_external_id {
    type = string
    description = "platform cloudhealth external id"
}

variable wiz_external_id {
    type = string
    description = "wiz external id"
}

variable wiz_orchestrator_account_id {
    type = string
    description = "wiz orchestrator account id"
}

variable wiz_access_account_id {
    type = string
    description = "wiz access account id"
}

variable snow_itom_prod_account {
    type = string
    description = "snow itom prod account"
}

variable irm_account_id {
    type = string
    description = "irm account id"
}

variable irm_environment {
    type = string
    description = "irm environment"
}

variable cloudhelth_bucket_name {
    type = string
    description = "cloudhelth bucket name"
}

variable atl_terraform_backend_bucket_name {
    type = string
    description = "atl terraform backend bucket name"
}

variable atl_terraform_backend_dynamodb {
    type = string
    description = "atl terraform backend dynamodb"
}

variable "subscription_email" {
  type    = string
  default = "GXSOMWIPROCLOUDAWSDA2-Operations@shell.com"
}

variable "cloudtrail_log_group_name" {
  type    = string
  default = "enter cloudtrail log group name"
}

variable "iam_change_sns_topic_name" {
  type    = string
  description = "iam change sns topic name"
}

variable "iam_changes_metric_filter_name" {
  type    = string
  description = "iam change metric filter name"
}

variable "ipaws_vpc_cidr" {
  type = string
  description = "IPAWS VPC cidr range"
}

variable "ipaws_pvt_subnet_cidr_1" {
  type = string
  description = "IPAWS Private subnet 1 CIDR range"
}

variable "ipaws_pvt_subnet_cidr_2" {
  type = string
  description = "IPAWS Private subnet 2 CIDR range"
}

variable "ipaws_pub_subnet_cidr_1" {
  type = string
  description = "IPAWS Public subnet 1 CIDR range"
}

variable "ipaws_pub_subnet_cidr_2" {
  type = string
  description = "IPAWS Public subnet 2 CIDR range"
}

variable "tgw_vpc_cidr" {
  type = string
  description = "Enter tgw vpc cidr range"
}

variable "tgw_pvt_sub_cidr_1" {
  type = string
  description = "Enter tgw pvt subnet cidr range"
}

variable "tgw_pvt_sub_cidr_2" {
  type = string
  description = "Enter tgw pvt subnet cidr range"
}

variable "tgw_pub_sub_cidr_1" {
  type = string
  description = "Enter tgw pub subnet cidr range"
}

variable "tgw_pub_sub_cidr_2" {
  type = string
  description = "Enter tgw pub subnet cidr range"
}

variable "tgw_table" {
  type = string
  description = "tgw table name"
}

variable patching_template_version {
    type = string
    description = "example v1.0"
}

variable patching_report_sns_topic_name {
    type = string
    description = "patching report sns topic name"
}

variable platform_patch_report_monthly_event_rule_name {
    type = string
    description = "platform patch report monthly event rule name"
}

variable master_inventory_state_machine_event_rule_name {
    type = string
    description = "master inventory state machine event rule name"
}

variable account_details_event_rule_name {
    type = string
    description = "account details event rule name"
}

variable "subscription_email_1" {
  type    = string
  description  = "subscription email"
}

variable "subscription_email_2" {
  type    = string
  description  = "subscription email"
}

variable "subscription_email_3" {
  type    = string
  description  = "subscription email"
}

variable "backup_jobs_report_event_rule_name" {
  type    = string
  description = "backup jobs report event rule name"
}

variable "failed_backup_jobs_report_event_rule_name" {
  type    = string
  description = "failed backup jobs report event rule name"
}

variable "dynamodb_pitr_event_rule_name" {
  type    = string
  description = "enter rule name"
}

variable "pitr_change_sns_topic_name" {
  type    = string
  description  = "sns topic name"
}

variable account_update_bucket {
    type = string
    description = "account update bucket"
}

variable account_details_table {
    type = string
    description = "account details table"
}

variable exception_ami_table {
    type = string
    description = "exception ami table"
}

variable admin_account {
    type = string
    description = "admin account"
}

variable admin_dl {
    type = string
    description = "admin dl"
}

variable failure_operation_dl {
    type = string
    description = "failure operation dl"
}

variable simaas_operation_dl {
    type = string
    description = "simaas operation dl"
}

variable master_account {
    type = string
    description = "master account"
}

variable org_id {
    type = string
    description = "organization id"
}

variable whitelisted_regions {
    type = string
    description = "whitelisted regions"
}

variable whitelisted_regions_private {
    type = string
    description = "whitelisted regions private"
}

variable whitelisted_regions_public {
    type = string
    description = "whitelisted regions public"
}

variable private_whitelisted_region {
    type = string
    description = "whitelisted regions private"
}

variable whitelisted_custom_regions {
    type = string
    description = "whitelisted regions custom"
}

variable identity_store_id {
    type = string
    description = "identity store id"
}

variable public_whitelisted_region {
    type = string
    description = "whitelisted regions public"
}

variable toe_compliant_os_private {
    type = string
    description = "toe compliant os flavours private"
}

variable toe_compliant_os_public {
    type = string
    description = "toe compliant os flavours public"
}

variable toe_compliant_os {
    type = string
    description = "toe compliant os flavours"
}

variable ami_owner_account {
    type = string
    description = "ami owner account"
}

variable ami_tags {
    type = string
    description = "ami tags"
}

variable sender_id {
    type = string
    description = "sender id"
}

variable instancescheduler_template_version {
    type = string
    description = "example v1.0"
}

variable source_email {
    type = string
    description = "source email"
}

variable approver_email {
    type = string
    description = "approver email"
}

variable pim_template_version {
    type = string
    description = "example v1.0"
}

variable af_product_id {
    type = string
    description = "af product id"
}

variable release_S3_bucket {
    type = string
    description = "release S3 bucket"
}

variable release_folder {
    type = string
    description = "release folder"
}

variable shared_directory_id_us {
    type = string
    description = "shared directory id us"
}

variable shared_directory_name_us {
    type = string
    description = "shared directory name us"
}

variable shared_directory_ip_us {
    type = string
    description = "shared directory ip address us"
}

variable shared_directory_id_eu {
    type = string
    description = "shared directory id eu"
}

variable shared_directory_name_eu {
    type = string
    description = "shared directory name eu"
}

variable shared_directory_ip_eu {
    type = string
    description = "shared directory ip address eu"
}

variable shared_directory_id_singapore {
    type = string
    description = "shared directory id singapore"
}

variable shared_directory_name_singapore {
    type = string
    description = "shared directory name singapore"
}

variable shared_directory_ip_singapore {
    type = string
    description = "shared directory ip address singapore"
}

variable private_production_ou {
    type = string
    description = "private production ou id"
}

variable private_staging_ou {
    type = string
    description = "private staging ou id"
}

variable private_exception_ou {
    type = string
    description = "private exception ou id"
}

variable public_staging_ou {
    type = string
    description = "public staging ou id"
}

variable public_production_ou {
    type = string
    description = "public production ou id"
}

variable public_exception_ou {
    type = string
    description = "public exception ou id"
}

variable managed_services_beagile_ou {
    type = string
    description = "managed services beagile ou id"
}

variable data_management_ou {
    type = string
    description = "data management ou id"
}

variable hybrid_account_ou {
    type = string
    description = "hybrid account ou id"
}

variable migration_account_ou {
    type = string
    description = "migration account ou id"
}

variable root_ou {
    type = string
    description = "root ou id"
}

variable audit_account {
    type = string
    description = "audit account"
}

variable audit_account_admin_role_arn {
    type = string
    description = "audit account admin role arn"
}

variable logging_account {
    type = string
    description = "logging account"
}

variable automation_account_dl {
    type = string
    description = "automation account dl"
}

variable cidr_table_index {
    type = string
    description = "cidr table index"
}

variable cidr_table_name {
    type = string
    description = "cidr table name"
}

variable create_account_parentid {
    type = string
    description = "create account parentid"
}

variable create_case_ccadress {
    type = string
    description = "create case ccadress"
}

variable dl_table_name {
    type = string
    description = "dl table name"
}

variable iam_mgmnt_account {
    type = string
    description = "iam mgmnt account"
}

variable master_admin_role_arn {
    type = string
    description = "master admin role arn"
}

variable agent_bucket {
    type = string
    description = "agent bucket"
}

variable success_operation_dl {
    type = string
    description = "success operation dl"
}

variable unit_test_approver {
    type = string
    description = "unit test approver"
}

variable master_account_name {
    type = string
    description = "master account name"
}

variable platform_ou_decommission {
    type = string
    description = "platform ou decommission"
}

variable hostedzone_id_us {
    type = string
    description = "hostedzone id us"
}

variable hostedzone_id_eu {
    type = string
    description = "hostedzone id eu"
}

variable hostedzone_id_sg {
    type = string
    description = "hostedzone id eu"
}

variable shared_services_account_id {
    type = string
    description = "shared services account id"
}

variable platform_network_product_id {
    type = string
    description = "platform network product id"
}

variable platform_network_table_name {
    type = string
    description = "platform network table name"
}

variable sso_instance_arn {
    type = string
    description = "sso instance arn"
}

variable irm_permission_set {
    type = string
    description = "irm permission set"
}

variable admin_permission_set {
    type = string
    description = "admin permission set"
}

variable platform_readonly_permission_set {
    type = string
    description = "platform readonly permission set"
}

variable BusinessCustom_permission_set {
    type = string
    description = "Business Custom permission set"
}

variable platform_readonly_group {
    type = string
    description = "platform readonly group"
}

variable permission_set_arn {
    type = string
    description = "permission set arn"
}

variable platform_irm_group {
    type = string
    description = "platform irm group"
}

variable itom_readonly_group {
    type = string
    description = "itom readonly group"
}

variable itom_readonly_permission_set {
    type = string
    description = "itom readonly permission set"
}

variable AVMTemplateVersion {
    type = string
    description = "AVMTemplateVersion"
}

variable NewAVMTemplateVersion {
    type = string
    description = "NewAVMTemplateVersion"
}

variable AVMServiceCatalogRoleARN {
    type = string
    description = "AVMServiceCatalogRoleARN"
}

variable AVMServiceCatalogServiceRoleARN {
    type = string
    description = "AVMServiceCatalogServiceRoleARN"
}

variable AVMServiceCatalogOperatorRoleARN {
    type = string
    description = "AVMServiceCatalogOperatorRoleARN"
}

variable ControlTowerPortfolioARN {
    type = string
    description = "ControlTowerPortfolioARN"
}

variable NetworkTemplateVersion {
    type = string
    description = "NetworkTemplateVersion"
}

variable "role_arn" {
  type    = string
  default = "platform admin role arn"
}

variable "requests_layer" {
  type    = string
  default = "requests layer"
}

variable "cryptography_layer" {
  type    = string
  default = "cryptography layer"
}

variable "msal_layer" {
  type    = string
  default = "msal layer"
}

variable "pyjwt_layer" {
  type    = string
  default = "pyjwt layer"
}

variable platform_avm_product_id {
    type = string
    description = "avm product id"
}

variable vpc_flow_bucket_env_type {
    type = string
    description = "dev, acceptance, prod"
}

variable scp_env_type {
    type = string
    description = "Dev, acceptance, prod"
}

variable release_bucket_name {
    type = string
    description = "enter the release bucket name"
}

variable TeamEmailDL {
    type = string
    description = "team email dl"
}

variable RotationPeriod {
    type = string
    description = "iam rotation period"
}

variable WarnPeriod {
    type = string
    description = "iam warn period"
}

variable SNOWSGCAccountID {
    type = string
    description = "snow sgc account"
}

variable accountDetailTableName {
    type = string
    description = "account Details Table Name"
}

variable SecurityContactEmail {
    type = string
    description = "Security Contact Email"
}

variable SecurityContactName {
    type = string
    description = "Security Contact Name"
}

variable SecurityContactTitle {
    type = string
    description = "Security Contact Title"
}

variable SecurityContactPhone {
    type = string
    description = "Security Contact Phone"
}

variable OperationsContactEmail {
    type = string
    description = "Operations Contact Email"
}

variable OperationsContactName {
    type = string
    description = "Operations Contact Name"
}

variable OperationsContactTitle {
    type = string
    description = "Operations Contact Title"
}

variable OperationsContactPhone {
    type = string
    description = "Operations Contact Phone"
}

variable RootMonitoringExemptionDays {
    type = string
    description = "Root Monitoring Exemption Days"
}

variable DynatraceRoleNameMaster {
    type = string
    description = "Dynatrace Role Name Master"
}

variable DynatraceAccountID {
    type = string
    description = "Dynatrace Account ID"
}

variable CIDashboardQuickSightUserName {
    type = string
    description = "CI Dashboard QuickSight UserName"
}

variable platformcontributorexternalrolearn {
    type = string
    description = "platform contributor external role arn"
}

variable platformmastercontributorrolearn {
    type = string
    description = "platform master contributor role arn"
}

variable platformdatalakeid {
    type = string
    description = "platform datalake id"
}

variable "cffi_layer" {
  type    = string
  default = "cffi layer"
}

variable close_account_metric_filter_name {
    type = string
    description = "close account metric filter name"
}

variable cid_stack_name {
    type = string
    description = "cid stack name"
}

variable SnowNerworkVPCIntegrationLogBucket {
    type = string
    description = "Snow Nerwork VPC Integration Log Bucket"
}

variable main_policy_id_private {
    type = string
    description = "main policy id private"
}

variable main_policy_id_public {
    type = string
    description = "main policy id public"
}

variable main_policy_id_hybrid {
    type = string
    description = "main policy id hybrid"
}

variable titan_team_dl {
    type = string
    description = "titan team dl"
}

variable ScoreCardBucketName {
    type = string
    description = "ScoreCardBucketName"
}

variable DPSOMDL {
    type = string
    description = "DPSOMDL"
}

variable ScoreCardDBTableName {
    type = string
    description = "ScoreCardDBTableName"
}

variable ConfigAggregatorName {
    type = string
    description = "ConfigAggregatorName"
}

variable "api_stage" {
  type    = string
}

variable "NonInteractiveUser_Lambda_ApiAuth_permission_statement_id" {
  type    = string
}

variable "NonInteractiveUser_Lambda_Invoker_permission_statement_id" {
  type    = string
}

variable "NonInteractiveUser_Lambda_Receiver_permission_statement_id" {
  type    = string
}

variable "cloudwatch_event_target_id" {
 type    = string 
}

variable control_tower_gaurdrails_stack_name {
    type = string
    description = "control tower iam role gaurdrails stack name"
}

variable billing_bucket_name {
    type = string
    description = "billing bucket name"
}

variable request_dynamodb_table {
    type = string
    description = "dynamo db table variable"
}
