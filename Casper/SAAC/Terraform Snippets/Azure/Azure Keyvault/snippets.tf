######################################################################################################################################################################
############################################################       Requirements section   #######################################################################
######################################################################################################################################################################

#Creating Azure Key Vault
resource "azurerm_key_vault" "kv" {
  name                = var.key_vault_name
  location            = var.keyvault_resource_group.location
  resource_group_name = var.keyvault_resource_group.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days = var.keyvault_kv_soft_delete_retention_days #--->  Ensure purge protection is enabled and the number of days to retain the vault is configured as per organization policy
  purge_protection_enabled  = var.keyvault_kv_purge_protection_enabled  #---> Please refer above line
  enable_rbac_authorization  = var.keyvault_kv_enable_rbac_authorization 
  sku_name       = var.keyvault_kv_sku_name
  tags                       = var.keyvault_kv_tags   #--------->  Ensure Azure Key vault uses standard organizational Resource tagging method
  
  network_acls {                      #If you want to block access from public network then enable it
    bypass         = "AzureServices"
    default_action = "Deny"
  }
  }

#  Ensure the keys and Secrets in Key vault has expiration date set and rotated according to Organization policy
resource "azurerm_resource_policy_assignment" "kv_expiration_policy" {
  name                 = var.keyvault_kv_key_expiration_policy_name
  resource_id          = azurerm_key_vault.kv.id
  policy_definition_id = var.keyvault_kv_expiration_policy_definition_id
}

# Ensure that public access is disabled by implementing Private endpoints

resource "azurerm_private_dns_zone" "kv_private_dns_zone" {
  name                = var.keyvault_kv_private_dns_zone_name
  resource_group_name = var.keyvault_resource_group.name
}

resource "azurerm_private_endpoint" "kv_private_endpoint" {
  name                = var.keyvault_kv_private_endpoint_name
  location            = var.keyvault_resource_group.location
  resource_group_name = var.keyvault_resource_group.name
  subnet_id           = var.keyvault_subnet_id

  private_service_connection {
    name                           = var.keyvault_kv_private_service_connection_name
    private_connection_resource_id = azurerm_key_vault.kv.id
    is_manual_connection           = false
    subresource_names              = [var.keyvault_subresource_names]
  }
  private_dns_zone_group {
    name = var.keyvault_kv_private_dns_zone_group_name
    private_dns_zone_ids = [
      azurerm_private_dns_zone.kv_private_dns_zone.id,
    ]
  }
}
# Ensure key vault data plane access is granted only using Managed Identities

resource "azurerm_user_assigned_identity" "kv_ua_identity" {
  name                = var.keyvault_kv_ua_identity_name
  resource_group_name = var.keyvault_resource_group.name
  location            = var.keyvault_resource_group.location
}

# Ensure RBAC access control method used grant access to Key vault

resource "azurerm_role_assignment" "kv_role_assignment" {
  scope              = azurerm_key_vault.kv.id
  role_definition_id = var.keyvault_rbac_role_definition_id
  principal_id       = azurerm_user_assigned_identity.kv_ua_identity.principal_id # Object ID of the security principal to who should assume the role - This should be Object ID of the newly recreated VM if Trusted Launch subsequently set to 'True' through Terraform
}

# Ensure the application accessing Key vault service is running on a platform that supports TLS 1.2 or above

resource "azurerm_resource_group_policy_assignment" "kv_tls_policy" {
  name                 = var.keyvault_kv_tls_policy_name
  resource_group_id    = var.keyvault_resource_group.keyvault_resource_group_id
  policy_definition_id = var.keyvault_kv_tls_policy_definition_id
}

# Ensure Diagnostic logging is enabled for Azure Key vault

resource "azurerm_monitor_diagnostic_setting" "kv_diag_setting" {
  name               = var.keyvault_kv-diagsetting_name # Required argument
  target_resource_id = azurerm_key_vault.kv.id # Required argument (Source of log data)
  storage_account_id = var.keyvault_resource_id
  log {
    category = var.keyvault_kv_log_category

    retention_policy {
      enabled = true
      days    = var.keyvault_kv_retention_days # Retention duration only applies if log destination is of a type storage_account_id
    }
  }
  log {
    category = var.keyvault_kv_log_category1

    retention_policy {
      enabled = true
      days    = var.keyvault_kv_retention_days # Retention duration only applies if log destination is of a type storage_account_id
    }
  }
}

# Ensure Service tags are enabled for the Azure Key vaults

resource "azurerm_network_security_group" "kv_network_security_group" {
  name                = var.keyvault_kv_network_security_group_name
  location            = var.keyvault_resource_group.location
  resource_group_name = var.keyvault_resource_group.name

  security_rule {
    name                       = var.keyvault_kv_security_rule.name
    priority                   = var.keyvault_kv_security_rule.priority
    direction                  = var.keyvault_kv_security_rule.direction
    access                     = var.keyvault_kv_security_rule.access
    protocol                   = var.keyvault_kv_security_rule.protocol
    source_port_range          = var.keyvault_kv_security_rule.source_port_range
    destination_port_range     = var.keyvault_kv_security_rule.destination_port_range
    source_address_prefix      = var.keyvault_kv_security_rule.source_address_prefix
    destination_address_prefix = var.keyvault_kv_security_rule.destination_address_prefix
  }
}

#  Ensure administrative tasks are performed only in admin-e workstations ---> Not sure on how implement this using terraform
#  Ensure organizational Anti-malware and vulnerability tools are enabled for Azure Key vault---> Can we invalidate this as it should come under microsoft defender security baseline requirements
#  Ensure Activity logging is enabled for Azure Key vault-->needs to invalidated as it needs to be moved to subscription baseline requirement section.
