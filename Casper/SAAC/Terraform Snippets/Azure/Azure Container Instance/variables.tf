#######################################
#Variables
#######################################

data "azurerm_client_config" "current" {}

data "azurerm_resource_group" "key_rg" {
  name = "Key-vault-RG"
}

data "azurerm_resource_group" "vnet_rg" {
  name = "Vnet_RG"
}

data "azurerm_resource_group" "network_watcher" {
  name = "Network_watcher_RG"
}

data "azurerm_resource_group" "law" {
  name = "Log_analytics_workspace_RG"
}

data "azurerm_key_vault" "kv" {
  name                = "KeyVaultforterraform"
  resource_group_name = data.azurerm_resource_group.key_rg.name
}

data "azurerm_key_vault_secret" "container_instance_pass" {
  name         = "ContainerInstancePass"
  key_vault_id = data.azurerm_key_vault.kv.id
}

data "azurerm_subnet" "subnet" {
  name                 = "subnet"
  virtual_network_name = "my_test_vnet"
  resource_group_name  = data.azurerm_resource_group.vnet_rg.name
}

data "azurerm_network_watcher" "network_watcher" {
  name                = "Network_watcher"
  resource_group_name = data.azurerm_resource_group.network_watcher.name
}

data "azurerm_log_analytics_workspace" "law" {
  name                = "Log_analytics_workspace"
  resource_group_name = data.azurerm_resource_group.law.name
}

data "azurerm_network_security_group" "nsg" {
  name                = "NSG"
  resource_group_name = data.azurerm_resource_group.vnet_rg.name
}

variable "resource_group" {
  type        = map(any)
  description = "Resource group settings"
}

variable "storage_account" {
  type        = map(any)
  description = "Storage account settings"
}

variable "container_group" {
  type        = map(any)
  description = "Container group settings"
}

variable "network_profile" {
  type        = map(any)
  description = "Network profile settings"
}

variable "user_assigned_identity_name" {
  type        = string
  description = "User ass identity name"
}

variable "network_watcher_flow_log_name" {
  type        = string
  description = "Network watcher flow log name"
}

variable "enable" {
  type = map(any)
}

variable "days" {
  type = number
}

variable "minutes" {
  type = number
}

variable "role_assignment" {
  type        = map(any)
  description = "Role assigment settings"
}

variable "common_tags" {
  type        = map(string)
  description = "Default tags attached to all resources. | Example: { Name = \"vpc_endpoint\", ... }"
}

variable "ACI_secure_environment_variables" {
  type        = map(any)
  description = "Container secure envirnment variables"
}


