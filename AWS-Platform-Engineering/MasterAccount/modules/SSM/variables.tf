variable env_type {
    type = string
    description = "environment name"
}


variable af_product_id {
    type = string
    description = "af product id"
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

variable RootMonitoringExemptionDays {
    type = string
    description = "Root Monitoring Exemption Days"
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

variable account_update_bucket {
    type = string
    description = "account update bucket"
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

variable failure_operation_dl {
    type = string
    description = "failure operation dl"
}

variable simaas_operation_dl {
    type = string
    description = "simaas operation dl"
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

variable whitelisted_custom_regions {
    type = string
    description = "whitelisted regions custom"
}

variable private_whitelisted_region {
    type = string
    description = "whitelisted regions private"
}

variable public_whitelisted_region {
    type = string
    description = "whitelisted regions public"
}

variable unit_test_approver {
    type = string
    description = "unit test approver"
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

variable platform_cloudhealth_external_id {
    type = string
    description = "platform cloudhealth external id"
}

variable platform_cloudhealth_account {
    type = string
    description = "platform cloudhealth account"
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

variable atl_terraform_backend_bucket_name {
    type = string
    description = "platform atl tf backend s3bucket"
}

variable atl_terraform_backend_dynamodb {
    type = string
    description = "platform atl tf backend dynamodb"
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

variable master_account {
    type = string
    description = "master account"
}

variable platform_avm_product_id {
    type = string
    description = "avm product id"
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










