#######################################
#Variables
#######################################

data "azurerm_client_config" "current" {}

data "azurerm_resource_group" "rg" {
  name = "Key-vault-RG"
}

data "azurerm_key_vault" "kv" {
  name                = "Key-Vault-for-terraform"
  resource_group_name = data.azurerm_resource_group.rg.name
}

data "azurerm_key_vault_key" "key_vault_key" {
  name         = "cr-key"
  key_vault_id = data.azurerm_key_vault.kv.id
}

data "azurerm_subnet" "subnet" {
  name                 = "endpoint"
  virtual_network_name = "production"
  resource_group_name  = data.azurerm_resource_group.rg.name
}

variable "resource_group" {
  type        = map(any)
  description = "Resource group settings"
}

variable "user_assigned_identity_name" {
  type        = string
  description = "User ass identity name"
}

variable "storage_account" {
  type        = map(any)
  description = "Storage account settings"
}

variable "container_registry" {
  type        = map(any)
  description = "Container registry settings"
}

variable "monitor_diagnostic_setting" {
  type        = map(any)
  description = "Monitoring diagnostic settings name"
}

variable "private_endpoint" {
  type        = map(any)
  description = "Private endpoint settings"
}

variable "ns_rule" {
  type        = map(any)
  description = "Network sec rules"
}

variable "network_security_group_name" {
  type        = string
  description = "User ass identity name"
}

variable "role_assignment" {
  type        = map(any)
  description = "Role assigment"
}

variable "common_tags" {
  type = maps(string)
  description= "common tags used on all resource"  
}
