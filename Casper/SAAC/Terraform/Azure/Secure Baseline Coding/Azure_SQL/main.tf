data "terraform_remote_state" "vpc" {
  backend = "azurerm"
  config = {
    resource_group_name  = "EYGDSSEC-rg"
    storage_account_name = "eygdssecterraformstate"
    container_name       = "terraform-state"
    key                  = "baseline/network/terraform.tfstate"
  }
}

data "azurerm_client_config" "current" {}

data "azurerm_resource_group" "rg" {
  name = "EYGDSSECbaseline-rg"
}

data "azurerm_key_vault" "kv" {
  name                = "baselinevault-4vw1d"
  resource_group_name = data.azurerm_resource_group.rg.name
}

data "azurerm_key_vault_secret" "admin_name" {
  name         = "azure-sql-admin-name"
  key_vault_id = data.azurerm_key_vault.kv.id
}

data "azurerm_key_vault_secret" "admin_pwd" {
  name         = "azure-sql-admin-password"
  key_vault_id = data.azurerm_key_vault.kv.id
}

module "sqlserver" {

  source              = "../Modules/Azure_SQL_module"
  resource_group_name = "EYGDSSECbaseline-rg"
  tags                = var.tags

  sqlserver_name                = var.sqlserver_name
  admin_login                   = data.azurerm_key_vault_secret.admin_name.value
  admin_password                = data.azurerm_key_vault_secret.admin_pwd.value
  enable_failover_group         = true
  secondary_sql_server_location = var.secondary_sql_server_location

  database_name          = var.database_name
  enable_firewall_rules  = true
  firewall_rules         = var.firewall_rules
  enable_auditing_policy = true

  storage_account_name = var.storage_account_name
}

module "firstendpoint" {
  source                = "../Modules/Private_Endpoint_module"
  resource_group_name   = "EYGDSSECbaseline-rg"
  name                  = module.sqlserver.primarysql_server_name
  resource_id           = module.sqlserver.primary_sql_server_id
  subresource_names     = ["sqlserver"]
  private_dns_zone_name = "privatelink.sqlcore.azure.net"
  vnet_id               = data.terraform_remote_state.vpc.outputs.vnet_id
  tags                  = var.tags
}

# Need to Update Private Endpoint to point to the same DNS Zone

module "secondendpoint" {
  source                  = "../Modules/Private_Endpoint_module"
  resource_group_name     = "EYGDSSECbaseline-rg"
  name                    = module.sqlserver.secondarysql_server_name
  resource_id             = module.sqlserver.secondary_sql_server_id
  subresource_names       = ["sqlserver"]
  private_dns_zone_name   = "privatelink.sqlcore.azure.net"
  create_private_dns_zone = false
  tags                    = var.tags
}
