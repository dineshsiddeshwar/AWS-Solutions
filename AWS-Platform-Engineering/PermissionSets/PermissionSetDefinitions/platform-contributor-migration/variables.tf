variable "payer_account_id" {
    type = string
    description = "dev_payer_account_id "
}

variable "shared_services_account_id" {
    type = string
    description = "shared_services_account_id "
}

variable "log_archive_account_id" {
    type = string
    description = "log_archive_account_id"
}

variable "audit_account_id" {
    type = string
    description = "audit_account_id"
}

variable "platform_DashboardExternal"{
    type = string
    description = "permission set id for platform_DashboardExternal "
}

variable "platform_operator"{
    type = string
    description = "permission set id for platform_operator "
}
variable "platform_PIMCognitoAccess"{
    type = string
    description = "permission set id for platform_readonly "
}
variable "platform_ContributorExternal"{
    type = string
    description = "permission set id for platform_ContributorExternal "
}

variable "ou_id" {
    type = string
    description = "ou id used in platform_contributor_migration "
  
}

variable "migration_ou_id" {
    type = string
    description = "migration ou id "
  
}

variable "customer_managed_policy" {
    type = number
}