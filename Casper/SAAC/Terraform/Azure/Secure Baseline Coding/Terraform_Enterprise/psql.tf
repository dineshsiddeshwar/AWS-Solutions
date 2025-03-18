data "azurerm_key_vault" "kv" {
  name                = "baselinevault-4vw1d"
  resource_group_name = data.azurerm_resource_group.rg.name
}

data "azurerm_key_vault_secret" "admin_name" {
  name         = "psql-admin-name"
  key_vault_id = data.azurerm_key_vault.kv.id
}

data "azurerm_key_vault_secret" "admin_pwd" {
  name         = "psql-admin-password"
  key_vault_id = data.azurerm_key_vault.kv.id
}

resource "azurerm_postgresql_server" "tfe" {
  name                = "eygdssec-tfe-psqlserver"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name

  administrator_login          = data.azurerm_key_vault_secret.admin_name.value
  administrator_login_password = data.azurerm_key_vault_secret.admin_pwd.value

  sku_name   = "GP_Gen5_4"
  version    = "11"
  storage_mb = 51200

  backup_retention_days        = 7
  geo_redundant_backup_enabled = true
  auto_grow_enabled            = true
  
  # infrastructure_encryption_enabled = true
  public_network_access_enabled    = true
  ssl_enforcement_enabled          = false
  ssl_minimal_tls_version_enforced = "TLSEnforcementDisabled"

  tags = merge( {"Name"="tfe-psql"}, var.tags)
}
