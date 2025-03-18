######################################################################################################################################################################
############################################################       REQUIREMENTS SECTION        #######################################################################
######################################################################################################################################################################

########  Ensure that 'Auditing' is set to 'On' at server level and Retention is 'greater than 90 days'
resource "azurerm_mssql_server" "example" {
  name                         = var.azurerm_sql_server.name
  resource_group_name          = var.resource_group.name
  location                     = var.resource_group.location
  version                      = var.azurerm_sql_server.version
  minimum_tls_version          = "1.2"  ##<------- Ensure SQL Database connections are encrypted in transit using TLS1.2
  public_network_access_enabled = false ##<-------  Ensure server firewall and virtual networks are configured to deny access to traffic from all networks (including internet traffic)
  
  azuread_administrator {       ##<-------  Ensure that Azure SQL database access is granted using Azure Active Directory single sign-on (SSO) (AKA 'Enable Azure AD, not password-based authentication for access management')        
    azuread_authentication_only = true  
    login_username = var.azurerm_sql_server.adminusername
    object_id = var.azurerm_sql_server.adminobjectid
  }
  
  identity {
    type = "SystemAssigned" ##<------- Ensure application level access is granted using Managed Identities
  }

  tags = {      
    cost_center = var.cost_center
    ppmc_id = var.ppmc_id
    toc = var.toc
    usage_id = var.usage_id
    env_type = var.env_type
    exp_date = var.exp_date
    endpoint = var.endpoint
    sd_period = var.sd_period
  }
}

# Role Assignment for SQL server to access storage account
resource "azurerm_role_assignment" "example" {
  scope                = data.azurerm_storage_account.example.id
  role_definition_name = var.role_nam_02 #<---- custom role would be best here
  principal_id         = azurerm_mssql_server.example.identity.0.principal_id
}

# Auditing Policy ##<-------  nsure that 'Auditing' is set to 'On' at server level and Retention is 'greater than 90 days'
                  #If it already exist and needs to be managed by Terraform, run: terraform import azurerm_mssql_server_extended_auditing_policy.example /subscriptions/5985cb63-ac82-49b7-9eb1-db5d9016f454/resourceGroups/botest01-rg/providers/Microsoft.Sql/servers/dbserver01bo/extendedAuditingSettings/Default
                  # WARNING: Knows issue with policy timing out ! ! !
resource "azurerm_mssql_server_extended_auditing_policy" "example" {
  storage_endpoint       = var.mssql_server_extended_auditing_policy.blobendpoint
  server_id              = var.azurerm_sql_server.id
  retention_in_days      = var.mssql_server_extended_auditing_policy.retentiondays
  log_monitoring_enabled = false
  storage_account_subscription_id = data.azurerm_subscription.primary.subscription_id
  depends_on = [
    azurerm_role_assignment.example,
  ]
}


########  Ensure Azure SQL Server is protected using Private Endpoint
resource "azurerm_private_endpoint" "example" {
  name                = var.endpoint_name
  location            = var.resource_group.location
  resource_group_name = var.resource_group.name
  subnet_id           = data.azurerm_subnet.example.id
    private_service_connection {
        name                           = var.private_link_name
        is_manual_connection           =  false                              #<------- set to false, if no manual approval is required 
        private_connection_resource_id =  azurerm_mssql_server.example.id    #<------- resource ID of the Storage Account 
        subresource_names              = ["sqlServer"]                           #<------- in this example, it is Blob
    }
}


#######  Ensure that 'Transparent data encryption' is enabled using Organization's Managed keys (CMK) - assuming Key Vault is created but the key is not and AzureAD used for access instad of access policies 
#If it already exist and needs to be managed by Terraform, run: terraform import azurerm_key_vault_key.example "https://kvaultbo01.vault.azure.net/keys/byok/1ffe926c15fe4371a70ac9bb42dff97f"
resource "azurerm_key_vault_key" "example" {
  name         = var.key_name
  key_vault_id = data.azurerm_key_vault.example.id
  key_type     = "RSA"
  key_size     = 2048
  key_opts = [
    "unwrapKey",
    "wrapKey",
  ]
}

# Role Assignment for SQL server to access key
resource "azurerm_role_assignment" "key" {
  scope                = "${data.azurerm_key_vault.example.id}/keys/${azurerm_key_vault_key.example.name}"
  role_definition_name = "Key Vault Crypto Service Encryption User"
  principal_id         = azurerm_mssql_server.example.identity.0.principal_id
  depends_on = [
    azurerm_key_vault_key.example
  ]
}

resource "azurerm_mssql_server_transparent_data_encryption" "example" {
  server_id        = azurerm_mssql_server.example.id
  key_vault_key_id = azurerm_key_vault_key.example.id
  depends_on = [
    azurerm_role_assignment.key
  ]
}


###########  Ensure Microsoft Defender for Azure SQL Database is enabled at the subscription level to enable security alert and Vulnerability scanning - INVALIDATED (moved to MS Defender for Cloud requirements group)


########### Ensure File-snapshot backups of Azure SQL database are stored in private page blob - INVALIDATED (Not applicable for MS SQL database (DaaS))


###########  Ensure least privilege access method for SQL Server is implemented using Role-based access control (RBAC) 
resource "azurerm_role_assignment" "example02" {
  scope                = var.azurerm_sql_server.id 
  role_definition_name = var.role_name #<---- custom role would be best here
  principal_id         = var.security_principal_objectId
}


###########  Ensure SQL database secret is vaulted and rotated according to Organization policy - BLOCKED 



##########  Ensure that Azure SQL Database uses standard organizational Resource tagging method
resource "azurerm_mssql_database" "example" {
    collation                           = data.azurerm_mssql_database.existing.collation
    max_size_gb                         = data.azurerm_mssql_database.existing.max_size_gb
    name                                = data.azurerm_mssql_database.existing.name
    read_replica_count                  = data.azurerm_mssql_database.existing.read_replica_count
    read_scale                          = data.azurerm_mssql_database.existing.read_scale
    server_id                           = data.azurerm_mssql_database.existing.server_id
    sku_name                            = data.azurerm_mssql_database.existing.sku_name
    storage_account_type                = data.azurerm_mssql_database.existing.storage_account_type
    zone_redundant                      = data.azurerm_mssql_database.existing.zone_redundant

    timeouts {}

    tags = {      
      cost_center = var.cost_center
      ppmc_id = var.ppmc_id
      toc = var.toc
      usage_id = var.usage_id
      env_type = var.env_type
      exp_date = var.exp_date
      endpoint = var.endpoint
      sd_period = var.sd_period
  }

}





