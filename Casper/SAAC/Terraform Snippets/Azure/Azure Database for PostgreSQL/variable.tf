######################################################################################################################################################################
############################################################       Variables        #######################################################################
######################################################################################################################################################################

data "azurerm_client_config" "current" {}

variable "postgresql_resource_group" {
  type = map(any)
}

data "azurerm_eventhub_namespace" "eventhub_namespace" { # The referencing the existing eventhub namespace
  name                = var.postgresql_eventhub_namespace_name
  resource_group_name = var.postgresql_resource_group.name
}

data "azurerm_eventhub_namespace_authorization_rule" "eventhub_namespace_authorization_rule" { # The referencing the existing eventhub namespace authorization_rule
  name                = var.postgresql_eventhub_namespace_authorization_rule_name
  resource_group_name = var.postgresql_resource_group.name
  namespace_name      = var.postgresql_eventhub_namespace_name
}

variable "postgresql_vnet_name" {
  type = string
}

variable "postgresql_principal_id" {
  type = string
}

variable "postgresql_subnet_name" {
  type        = string
  description = "Name of your subnet"
}

variable "postgresql_storage_account_id" {
  type        = string
  description = "Name of your storage account"
}

variable "postgresql_pg_private_endpoint_subresource_names" {
  type        = list(string)
  description = "Name of the subresources"
}

data "azurerm_subnet" "subnet" { # Referencing existing subnet
  name                 = var.postgresql_subnet_name
  virtual_network_name = var.postgresql_vnet_name
  resource_group_name  = var.postgresql_resource_group.name
}

variable "postgresql_key_vault_id" {
  type        = string
  description = "Your Key vault id"
}

variable "postgresql_key_vault_access_policy_key_permissions" {
  type        = list(string)
  description = "values which is to be declared"
}

variable "postgresql_key_vault_key_name" {
  type = string
}

variable "pg_kv_key_type" {
  type = string 
}

variable "pg_kv_key_size" {
  type = number 
}

variable "postgresql_administrator_login" {
  type = string
}

variable "postgresql_administrator_login_password" {
  type = string
}

data "azurerm_key_vault_secret" "key_vault_secret" { # Referencing existing database admin details
  name         = var.postgresql_administrator_login
  key_vault_id = var.postgresql_key_vault_id
}

data "azurerm_key_vault_secret" "key_vault_secret_password" { # Referencing existing password details of database
  name         = var.postgresql_administrator_login_password
  key_vault_id = var.postgresql_key_vault_id
}

variable "postgresql_eventhub_namespace_name" {
  type = string
}

variable "postgresql_eventhub_namespace_authorization_rule_name" {
  type = string
}

variable "postgresql_storage_mb" {
  type = number
}

variable "log_category1" { 
 type = string
}

variable "log_category2" {
 type = string
}

variable "postgresql_charset" {
  type = string
}

variable "postgresql_collation" {
  type = string
}

variable "postgresql_pe_name" {
  type        = string
  description = "Private endpoint name"
}

variable "postgresql_ps_name" {
  type        = string
  description = "Private service connection name"
}

variable "postgresql_postgre_name" {
  type        = string
  description = "PostgreSQL server name"
}

variable "postgresql_database_name" {
  type = string
}

variable "postgresql_postgre_sku" {
  type        = string
  description = "PostgreSQL SKU type"
}

variable "postgresql_postgre_version" {
  type        = string
  description = "PostgreSQL version"
}

variable "postgresql_ssl_minimal" {
  type        = string
  description = "SSL minimal TLS version"
}

variable "postgresql_mds_name" {
  type        = string
  description = "Monitoring Diagnostic Settings name"
}

variable "postgresql_role_definition_id" {
  type        = string
  description = "To assign RBAC"
}

variable "postgresql_pg_server_tags" {
  description = "Various common tags to be declared"
  type        = map(string)
}
