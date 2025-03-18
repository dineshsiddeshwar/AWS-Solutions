module "business_LimitedOperatorExternal" {
  source = "./PermissionSetDefinitions/business_LimitedOperatorExternal"
}

module "business_IRMExternal" {
  source = "./PermissionSetDefinitions/business_IRMExternal"
}

module "platform_PIMCognitoAccess" {
  source = "./PermissionSetDefinitions/platform_PIMCognitoAccess"
}


module "platform_IRM" {
  source = "./PermissionSetDefinitions/platform_IRM"
}

module "business_LimitedOperatorPrivate" {
  source = "./PermissionSetDefinitions/business_LimitedOperatorPrivate"
}

module "business_ReadOnlyExternal" {
  source = "./PermissionSetDefinitions/business_ReadOnlyExternal"
}


module "business_Limejump_AssumeRole" {
  source = "./PermissionSetDefinitions/business_Limejump_AssumeRole"
}

module "business_SecurityPrivate" {
  source = "./PermissionSetDefinitions/business_SecurityPrivate"
}



module "business_IRMPrivate" {
  source = "./PermissionSetDefinitions/business_IRMPrivate"
}

module "business_ReadOnlyPrivate" {
  source = "./PermissionSetDefinitions/business_ReadOnlyPrivate"
}


module "business_OperatorExternal" {
  source = "./PermissionSetDefinitions/business_OperatorExternal"
}

module "platform_Operator" {
  source = "./PermissionSetDefinitions/platform_Operator"
  payer_account_id = var.payer_account_id
  audit_account_id = var.audit_account_id
  log_archive_account_id = var.log_archive_account_id
  shared_services_account_id = var.shared_services_account_id
  platform_DashboardExternal = var.platform_DashboardExternal
  platform_operator = var.platform_operator
  platform_PIMCognitoAccess = var.platform_PIMCognitoAccess
  platform_ContributorExternal = var.platform_ContributorExternal
}


module "business_ContributorExternal" {
  source = "./PermissionSetDefinitions/business_ContributorExternal"
}

module "business_OperatorPrivate" {
  source = "./PermissionSetDefinitions/business_OperatorPrivate"
}

module "business-Contributor-IOT" {
  source = "./PermissionSetDefinitions/business-Contributor-IOT"
}


module "platform_ContributorExternal" {
  source = "./PermissionSetDefinitions/platform_ContributorExternal"
}
module "business_Custom" {
  source = "./PermissionSetDefinitions/business_Custom"
}
module "bea-network-sre-iam-role" {
  source = "./PermissionSetDefinitions/bea-network-sre-iam-role"
}

module "platform-contributor-migration" {
  source = "./PermissionSetDefinitions/platform-contributor-migration"
  payer_account_id = var.payer_account_id
  audit_account_id = var.audit_account_id
  log_archive_account_id = var.log_archive_account_id
  shared_services_account_id = var.shared_services_account_id
  platform_DashboardExternal = var.platform_DashboardExternal
  platform_operator = var.platform_operator
  platform_PIMCognitoAccess = var.platform_PIMCognitoAccess
  platform_ContributorExternal = var.platform_ContributorExternal
  migration_ou_id = var.migration_ou_id
  ou_id = var.ou_id
  customer_managed_policy = var.customer_managed_policy
}

module "business_ContributorPrivateGeo" {
  source = "./PermissionSetDefinitions/business_ContributorPrivateGeo"
}

module "business_SecurityExternal" {
  source = "./PermissionSetDefinitions/business_SecurityExternal"
}




module "bea-platfrm-sre-iam-role" {
  source = "./PermissionSetDefinitions/bea-platfrm-sre-iam-role"
}

module "platform_MasterContributorAccess" {
  source = "./PermissionSetDefinitions/platform_MasterContributorAccess"
}


module "business_Renewable_Energy" {
  source = "./PermissionSetDefinitions/business_Renewable_Energy" 
}

module "business_ContributorExternaldigi" {
  source = "./PermissionSetDefinitions/business_ContributorExternaldigi"
}



module "platform_DashboardExternal" {
  source = "./PermissionSetDefinitions/platform_DashboardExternal"
  
}



module "business_sandbox_automation"{
  source = "./PermissionSetDefinitions/business_sandbox_automation"
}

module "business_ContributorPrivate" {
  source = "./PermissionSetDefinitions/business_ContributorPrivate"
}

module "business_ServiceNow_ITOM" {
  source = "./PermissionSetDefinitions/business_ServiceNow_ITOM"
}

module "Platform_ReadOnly" {
  source = "./PermissionSetDefinitions/Platform_ReadOnly"
}

module "Platform_SecurityIncident" {
  source = "./PermissionSetDefinitions/Platform_SecurityIncident"
}

module "Platform_SecurityReader" {
  source = "./PermissionSetDefinitions/Platform_SecurityReader"
}