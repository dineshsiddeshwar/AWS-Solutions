######################################################################################################################################################################
############################################################       Define required variables   #######################################################################
######################################################################################################################################################################
variable "resource_group" {
  type = map 
}

variable "azurerm_sql_server" {
  type = map
}

variable "blob_endpoint" {
  type = string
}

variable "storage_Account_name" {
  type = string
}

variable "mssql_server_extended_auditing_policy" {
  type = map
}

data "azurerm_subscription" "primary" {
}

data "azurerm_storage_account" "example" {
  name                = var.storage_Account_name
  resource_group_name = var.resource_group.name
}

variable "subnet_name" {
  type = string
}

variable "vnet_name" {
  type = string
}

data "azurerm_subnet" "example" {
  name                 = var.subnet_name
  virtual_network_name = var.vnet_name
  resource_group_name  = var.resource_group.name
}

variable "keyVault_name" {
  type = string
}

data "azurerm_key_vault" "example" {
  name                = var.keyVault_name
  resource_group_name = var.resource_group.name
}

variable "cost_center" {
  type = string
}
variable "ppmc_id" {
  type = string
}
variable "toc" {
  type = string
}
variable "usage_id" {
  type = string
}
variable "env_type" {
  type = string
}
variable "exp_date" {
  type = string
}
variable "endpoint" {
  type = string
}
variable "sd_period" {
  type = string
}

variable "mssql_db_01" {
  type = map
}

data "azurerm_mssql_database" "existing" {
  name      = var.mssql_db_01.name
  server_id = var.mssql_db_01.server_id
}

variable "role_name" {
  type = string
}

variable "role_nam_02" {
  type = string
}

variable "security_principal_objectId" {
  type = string
}

variable "key_name" {
  type = string
}

variable "private_link_name" {
  type = string
}

variable "endpoint_name" {
  type = string
}
