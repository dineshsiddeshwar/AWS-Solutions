######################################################################################################################################################################
############################################################       REQUIREMENTS SECTION        #######################################################################
######################################################################################################################################################################

# if already the postgresql server exists and needs to be managed by Terraform, please run: terraform import azurerm_postgresql_server.example /subscriptions/5985cb63-ac82-49b7-9eb1-db5d9016f454/resourceGroups/botest01-rg/providers/Azuredatabaseforpostgresqlserver (just an example)

resource "azurerm_postgresql_server" "postgresql_server" {
  name                             = var.postgresql_postgre_name
  location                         = var.postgresql_resource_group.location
  resource_group_name              = var.postgresql_resource_group.name
  administrator_login              = data.azurerm_key_vault_secret.key_vault_secret.value
  administrator_login_password     = data.azurerm_key_vault_secret.key_vault_secret_password.value
  sku_name                         = var.postgresql_postgre_sku
  version                          = var.postgresql_postgre_version
  storage_mb                       = var.postgresql_storage_mb
  public_network_access_enabled    = false
  ssl_enforcement_enabled          = true
  ssl_minimal_tls_version_enforced = var.postgresql_ssl_minimal # Ensure Azure Database for PostgreSQL connections are encrypted in transit using TLS1.2

  identity {
    type = "SystemAssigned"
  }
  threat_detection_policy { # Ensure organizational Anti-malware and vulnerability tools are enabled for azure database for postreSQL. Microsoft Defender for Azure Database for PostgreSQL is enabled at the subscription level to enable security alert and Vulnerability scanning
    enabled                    = true
    storage_account_access_key = var.postgresql_storage_account_id
  }
 
  tags = var.postgresql_pg_server_tags #<------ # Ensure that Azure Database for PostgreSQL uses standard organizational Resource tagging method
}

resource "azurerm_postgresql_database" "postgresql_database" {
  name                = var.postgresql_database_name
  resource_group_name = var.postgresql_resource_group.name
  server_name         = azurerm_postgresql_server.postgresql_server.name
  charset             = var.postgresql_charset
  collation           = var.postgresql_collation
}

resource "azurerm_private_endpoint" "private_endpoint" {
  name                = var.postgresql_pe_name
  location            = var.postgresql_resource_group.location
  resource_group_name = var.postgresql_resource_group.name
  subnet_id           = data.azurerm_subnet.subnet.id

  private_service_connection { # Ensure Azure Database for PostgreSQL is protected using Private Endpoint
    name                           = var.postgresql_ps_name
    private_connection_resource_id = azurerm_postgresql_server.postgresql_server.id
    subresource_names              = var.postgresql_pg_private_endpoint_subresource_names
    is_manual_connection           = false
  }
}


# Ensure that Azure Database for PostgreSQL is encrypted using Organization's Manged keys (CMK)

resource "azurerm_key_vault_access_policy" "pg_keyvault_access_policy_server" {
  key_vault_id       = var.postgresql_key_vault_id
  tenant_id          = data.azurerm_client_config.current.tenant_id
  object_id          = azurerm_postgresql_server.postgresql_server.identity.0.principal_id
  key_permissions    = var.postgresql_key_vault_access_policy_key_permissions #  ["Get", "UnwrapKey", "WrapKey"]
  secret_permissions = ["Get"]
}

resource "azurerm_key_vault_access_policy" "pg_keyvault_access_policy_client" {
  key_vault_id       = var.postgresql_key_vault_id
  tenant_id          = data.azurerm_client_config.current.tenant_id
  object_id          = azurerm_postgresql_server.postgresql_server.identity.0.principal_id
  key_permissions    = var.postgresql_key_vault_access_policy_key_permissions # ["Get", "Create", "Delete", "List", "Restore", "Recover", "UnwrapKey", "WrapKey", "Purge", "Encrypt", "Decrypt", "Sign", "Verify"]
  secret_permissions = ["Get"]
}

resource "azurerm_key_vault_key" "pg_key_vault_key" {
  name         = var.postgresql_key_vault_key_name
  key_vault_id = var.postgresql_key_vault_id
  key_type     = var.pg_kv_key_type
  key_size     = var.pg_kv_key_size
  key_opts     = ["decrypt", "encrypt", "sign", "unwrapKey", "verify", "wrapKey"]

  depends_on = [
    azurerm_key_vault_access_policy.pg_keyvault_access_policy_client,
    azurerm_key_vault_access_policy.pg_keyvault_access_policy_server,
  ]
}

resource "azurerm_postgresql_server_key" "postgresql_server_key" {
  server_id        = azurerm_postgresql_server.postgresql_server.id
  key_vault_key_id = azurerm_key_vault_key.pg_key_vault_key.id
}


# Ensure least privilege access method for Azure Database for PostgreSQL is implemented using Role-based access control (RBAC)

resource "azurerm_role_assignment" "role_assignment" {
  scope              = azurerm_postgresql_server.postgresql_server.id
  role_definition_id = var.postgresql_role_definition_id
  principal_id       = azurerm_postgresql_server.postgresql_server.identity.0.principal_id
}

# Ensure tha Azure Database for PostgreSQL access is granted using Azure active directory
resource "azurerm_postgresql_active_directory_administrator" "example" {
  server_name         = azurerm_postgresql_server.postgresql_server.name
  resource_group_name = var.postgresql_resource_group.name
  login               = "sqladmin"
  tenant_id           = data.azurerm_client_config.current.tenant_id
  object_id           = data.azurerm_client_config.current.object_id
}

# Ensure Diagnostic logs for 'PostgreSQLLogs' is Enabled

resource "azurerm_eventhub_namespace" "eventhub_namespace" {         # Using the existing eventhub namespace
  name                = data.azurerm_eventhub_namespace.eventhub_namespace.name # Your value
  location            = var.postgresql_resource_group.location
  resource_group_name = var.postgresql_resource_group.name
  sku                 = data.azurerm_eventhub_namespace.eventhub_namespace.sku
  capacity            = data.azurerm_eventhub_namespace.eventhub_namespace.capacity
}

resource "azurerm_eventhub_namespace_authorization_rule" "eventhub_namespace_authorization_rule" { # Using the existing eventhub namespace authorization_rule
  name                = data.azurerm_eventhub_namespace_authorization_rule.eventhub_namespace_authorization_rule.name
  namespace_name      = data.azurerm_eventhub_namespace.eventhub_namespace.name
  resource_group_name = var.postgresql_resource_group.name
  listen              = data.azurerm_eventhub_namespace_authorization_rule.eventhub_namespace_authorization_rule.listen
  send                = data.azurerm_eventhub_namespace_authorization_rule.eventhub_namespace_authorization_rule.send
  manage              = data.azurerm_eventhub_namespace_authorization_rule.eventhub_namespace_authorization_rule.manage
}

resource "azurerm_monitor_diagnostic_setting" "monitor_diagnostic_setting" {
  name                           = var.postgresql_mds_name
  target_resource_id             = azurerm_postgresql_server.postgresql_server.id
  eventhub_authorization_rule_id = data.azurerm_eventhub_namespace_authorization_rule.eventhub_namespace_authorization_rule.id

  log {
    category = var.log_category1
  }
  metric {
    category = var.log_category2
}
}
#  Ensure Activity logging is enabled for azure database for PostgreSQL - Implemented in Organizational runbook at subscription level
#  Ensure azure database for PostgreSQL administrative credentials are vaulted using enterprise vaulting solutions - Terraform implementation not available as POstgreSQL does not natvely supports, should be implemented via script.
