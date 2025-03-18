
variable "key_vault_name" {
  type        = string
  description = "Name of the existing key vault"
}

data "azurerm_key_vault" "kv" {
  name                = var.key_vault_name
  resource_group_name = var.resource_group.name
}

variable "key_vault_secret_name" {
  type        = string
  description = "Name of the existing database admin"
}

data "azurerm_key_vault_secret" "user" { # Referencing existing database admin details
  name         = var.key_vault_secret_name
  key_vault_id = data.azurerm_key_vault.kv.id
}

variable "key_vault_secret_password" {
  type        = string
  description = "Existing password details of database"
}

data "azurerm_key_vault_secret" "password" { # Referencing existing password details of database
  name         = var.key_vault_secret_password
  key_vault_id = data.azurerm_key_vault.kv.id
}

variable "nsg_name" {
  type        = string
  description = "Name of the existing network security group"
}

data "azurerm_network_security_group" "nsg" {
  name                = var.nsg_name
  resource_group_name = var.resource_group.name
}

variable "sql_subnet_name" {
  type        = string
  description = "Name of the existing subnet"
}

variable "sql_virtual_network_name" {
  type        = string
  description = "Name of the existing Vnet"
}

data "azurerm_subnet" "subnet" { # Referencing existing subnet
  name                 = var.sql_subnet_name
  virtual_network_name = var.sql_virtual_network_name
  resource_group_name  = var.resource_group.name
}

variable "sql_server_role_definition_id" {
  type = string
}

variable "resource_group" {
  type = map(any)
}

variable "ns_rule" {
  type = map(any)
}

/*
variable "policy" 
  type = map
}
*/
variable "nic" {
  type = map(any)
}

variable "vmstorage_image_reference_details" {
  type = map(any)
}

variable "storage_os_disk_details" {
  type = map(any)
}

variable "os_profile_details" {
  type = map(any)
}

variable "virtual_machine" {
  description = "Required details for creating VM"
  type = map(any)
}

variable "mssql_server" {
  description = "Required details for creating MSSQL server"
  type = map(any)
}

variable "os_profile_windows_config_details" {
  type = map(any)
}

variable "mssql_vm" {
  description = "Required details for creating MSSQL VM"
  type = map(any)
}

variable "mssql_vm_key_vault_credential" {
  type = map(any)
}

variable "mssql_database_name" {
  type = string
}

variable "sql_vm_tags" {
  type = map(any)
}
