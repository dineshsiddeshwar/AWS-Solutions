######################################################################################################################################################################
############################################################       Define required variables   #######################################################################
######################################################################################################################################################################
data "azurerm_client_config" "current" {}

variable "keyvault_resource_group" {
  description = "Details for resource group"
  type        = map(any)
}
variable "keyvault_subnet_id" {
  description = "The subnet to deploy private endpoint to"
  type        = string
}

variable "key_vault_name" {
  description = "Name of your key vault"
  type        = string
}
variable "keyvault_kv_soft_delete_retention_days" {
  description = "The number of days that items should be retained for once soft-deleted"
  type        = number
}
variable "keyvault_kv_tags" {
  description = "Organization specific tags for Key vault"
  type        = map(string)
}
variable "keyvault_kv_enable_rbac_authorization" {
  description = "Boolean flag to specify whether Azure Key Vault uses Role Based Access Control (RBAC) for authorization of data action"
  type        = string
}
variable "keyvault_kv_purge_protection_enabled" {
  description = "Boolean flag to specify whether Azure Key Vault uses Role Based Access Control (RBAC) for authorization of data action"
  type        = string
}
variable "keyvault_kv_sku_name" {
  type = string
}

variable "keyvault_kv_private_endpoint_name" {
  description = "Name of the existing private endpoint"
  type        = string
}
variable "keyvault_kv_private_service_connection_name" {
  description = "Name of the existing private service connection"
  type        = string
}
variable "keyvault_subresource_names" {
  type = string
}

variable "keyvault_kv_ua_identity_name" {
  type = string
}
variable "keyvault_rbac_role_definition_id" {
  description = "The id of the role you like to assign to enable RBAC. Preferred roles are - Key vault admin, Key Vault Contributor, Key Vault Secrets User"
  type        = string
}

# Values for assigning policy for resource group of the applications accessing keyvaults 
variable "keyvault_kv_tls_policy_name" {
  type = string
}
variable "keyvault_kv_tls_policy_definition_id" {
  description = "Name of the policy definition for TLS encryption"
  type        = string
}
variable "keyvault_kv_key_expiration_policy_name" {
  description = "Name of the policy for setting expiration"
  type        = string
}
variable "keyvault_kv_expiration_policy_definition_id" {
  description = "ID of the policy for setting expiration"
  type        = string
}


variable "keyvault_kv_retention_days" {
  description = "The number of days for which the Retention Policy should apply"
  type        = number
}

variable "keyvault_kv_network_security_group_name" {
  description = "The name of the network security group"
  type        = string
}
variable "keyvault_kv_security_rule" {
  description = "The values required for enabling the rule for setting service tag for key vault"
  type        = map(any)
}

#Values for enabling Diagnostic setting
variable "keyvault_resource_id" {
  description = "The ID of the storage account to which the logs are collected"
  type        = string
}
variable "keyvault_kv_log_category" {
  type = string
}
variable "keyvault_kv_log_category1" {
  type = string
}
variable "keyvault_kv-diagsetting_name" {
  type = string

}
variable "keyvault_kv_private_dns_zone_name" {
  description = "The name of private dns zone"
  type        = string
}
variable "keyvault_kv_private_dns_zone_group_name" {
  type = string
}
