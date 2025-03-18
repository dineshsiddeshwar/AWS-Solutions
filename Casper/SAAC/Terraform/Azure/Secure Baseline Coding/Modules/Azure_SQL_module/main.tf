locals {
  resource_group_name                 = element(coalescelist(data.azurerm_resource_group.rgrp.*.name, azurerm_resource_group.rg.*.name, [""]), 0)
  location                            = element(coalescelist(data.azurerm_resource_group.rgrp.*.location, azurerm_resource_group.rg.*.location, [""]), 0)
  if_threat_detection_policy_enabled  = var.enable_threat_detection_policy ? [{}] : []
  if_extended_auditing_policy_enabled = var.enable_auditing_policy ? [{}] : []
  if_create_database                  = var.database_name != "" ? true : false
}

#---------------------------------------------------------
# Resource Group Creation or selection - Default is "false"
#----------------------------------------------------------

data "azurerm_resource_group" "rgrp" {
  count = var.create_resource_group ? 0 : 1
  name  = var.resource_group_name
}

resource "azurerm_resource_group" "rg" {
  count    = var.create_resource_group ? 1 : 0
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

#---------------------------------------------------------
# Storage Account to keep Audit logs - Default is "false"
#----------------------------------------------------------

resource "random_string" "random-name" {
  length  = 5
  upper   = false
  lower   = true
  number  = true
  special = false
}

resource "azurerm_storage_account" "storeacc" {
  count                    = var.enable_threat_detection_policy || var.enable_auditing_policy ? 1 : 0
  name                     = lower("${var.storage_account_name}${random_string.random-name.result}")
  resource_group_name      = local.resource_group_name
  location                 = local.location
  account_kind             = var.account_kind
  account_tier             = var.account_tier
  account_replication_type = var.account_replication_type
  tags                     = var.tags
}

resource "azurerm_storage_account" "secondarystoreacc" {
  count                    = var.enable_threat_detection_policy || var.enable_auditing_policy ? 1 : 0
  name                     = lower("${var.storage_account_name}${random_string.random-name.result}sec")
  resource_group_name      = local.resource_group_name
  location                 = var.secondary_sql_server_location
  account_kind             = var.account_kind
  account_tier             = var.account_tier
  account_replication_type = var.account_replication_type
  tags                     = var.tags
}

#-------------------------------------------------------------
# SQL servers - Secondary server is depends_on Failover Group
#-------------------------------------------------------------



resource "azurerm_sql_server" "primary" {
  name                         = format("%s-primary", var.sqlserver_name)
  resource_group_name          = local.resource_group_name
  location                     = local.location
  version                      = var.sql_server_version
  administrator_login          = var.admin_login
  administrator_login_password = var.admin_password
  tags                         = var.tags

  # dynamic "extended_auditing_policy" {
  #   for_each = local.if_extended_auditing_policy_enabled
  #   content {
  #     storage_account_access_key = azurerm_storage_account.storeacc.0.primary_access_key
  #     storage_endpoint           = azurerm_storage_account.storeacc.0.primary_blob_endpoint
  #     retention_in_days          = var.log_retention_days
  #   }
  # }
}

resource "azurerm_sql_server" "secondary" {
  count                        = var.enable_failover_group ? 1 : 0
  name                         = format("%s-secondary", var.sqlserver_name)
  resource_group_name          = local.resource_group_name
  location                     = var.secondary_sql_server_location
  version                      = var.sql_server_version
  administrator_login          = var.admin_login
  administrator_login_password = var.admin_password
  tags                         = var.tags

  # dynamic "extended_auditing_policy" {
  #   for_each = local.if_extended_auditing_policy_enabled
  #   content {
  #     storage_account_access_key = azurerm_storage_account.secondarystoreacc.0.primary_access_key
  #     storage_endpoint           = azurerm_storage_account.secondarystoreacc.0.primary_blob_endpoint
  #     retention_in_days          = var.log_retention_days
  #   }
  # }
}

# #--------------------------------------------------------------------
# # SQL Database creation - Default edition:"Standard" and objective:"S1"
# #--------------------------------------------------------------------

resource "azurerm_sql_database" "db" {
  for_each                         = var.database_name != "" ? toset(["true"]) : []
  name                             = var.database_name
  resource_group_name              = local.resource_group_name
  location                         = local.location
  server_name                      = azurerm_sql_server.primary.name
  edition                          = var.sql_database_edition
#   requested_service_objective_name = var.sqldb_service_objective_name
  tags                             = var.tags

  dynamic "threat_detection_policy" {
    for_each = local.if_threat_detection_policy_enabled
    content {
      state                      = "Enabled"
      storage_endpoint           = azurerm_storage_account.storeacc.0.primary_blob_endpoint
      storage_account_access_key = azurerm_storage_account.storeacc.0.primary_access_key
      retention_days             = var.log_retention_days
      email_addresses            = var.email_addresses_for_alerts
    }
  }

  # dynamic "extended_auditing_policy" {
  #   for_each = local.if_extended_auditing_policy_enabled
  #   content {
  #     storage_account_access_key = azurerm_storage_account.storeacc.0.primary_access_key
  #     storage_endpoint           = azurerm_storage_account.storeacc.0.primary_blob_endpoint
  #     retention_in_days          = var.log_retention_days
  #   }
  # }
}

# #---------------------------------------------------------
# # Azure SQL Firewall Rule - Default is "false"
# #---------------------------------------------------------

resource "azurerm_sql_firewall_rule" "fw01" {
  count               = var.enable_firewall_rules && length(var.firewall_rules) > 0 ? length(var.firewall_rules) : 0
  name                = element(var.firewall_rules, count.index).name
  resource_group_name = local.resource_group_name
  server_name         = azurerm_sql_server.primary.name
  start_ip_address    = element(var.firewall_rules, count.index).start_ip_address
  end_ip_address      = element(var.firewall_rules, count.index).end_ip_address
}

resource "azurerm_sql_firewall_rule" "fw02" {
  count               = var.enable_failover_group && var.enable_firewall_rules && length(var.firewall_rules) > 0 ? length(var.firewall_rules) : 0
  name                = element(var.firewall_rules, count.index).name
  resource_group_name = local.resource_group_name
  server_name         = azurerm_sql_server.secondary.0.name
  start_ip_address    = element(var.firewall_rules, count.index).start_ip_address
  end_ip_address      = element(var.firewall_rules, count.index).end_ip_address
}

# #---------------------------------------------------------
# # Azure SQL Failover Group - Default is "false" 
# #---------------------------------------------------------

resource "azurerm_sql_failover_group" "fog" {
  count               = var.enable_failover_group && local.if_create_database ? 1 : 0
  name                = lower("${var.failover_group_name}${random_string.random-name.result}")
  resource_group_name = local.resource_group_name
  server_name         = azurerm_sql_server.primary.name
  databases           = [azurerm_sql_database.db["true"].id]
  tags                = var.tags

  partner_servers {
    id = azurerm_sql_server.secondary.0.id
  }

  read_write_endpoint_failover_policy {
    mode          = "Automatic"
    grace_minutes = 60
  }

  readonly_endpoint_failover_policy {
    mode = "Enabled"
  }
}








































# module "primary_diagnostic" {
#   source                     = "../Diagnostic_module"
#   name                       = "eygdssecazuresqlprimary"
#   resource_id                = azurerm_sql_server.primary.id
#   storage_account_id = azurerm_storage_account.storeacc.0.id
#   # log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
# } 

# module "secondary_diagnostic" {
#   source                     = "../Diagnostic_module"
#   name                       = "eygdssecazuresqlsecondary"
#   resource_id                = azurerm_sql_server.secondary.0.id
#   storage_account_id = azurerm_storage_account.secondarystoreacc.0.id
#   # log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
# } 


