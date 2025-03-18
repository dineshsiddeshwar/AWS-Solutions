######################################################################################################################################################################
############################################################       REQUIREMENTS SECTION        #######################################################################
######################################################################################################################################################################

# Ensure storage account is Protected using Private Endpoint
resource "azurerm_private_endpoint" "example" { #(NOTE: It is assumed the Private Endpoint resource DOES NOT exist in Azure environment.)
  name                = var.resource_prefix
  location            = var.resource_group_location
  resource_group_name = var.resource_group_name
  subnet_id           = var.subnet_id

  private_service_connection {
    name                           = var.resource_prefix
    is_manual_connection           = false                              # set to false, if no manual approval is required 
    private_connection_resource_id = azurerm_storage_account.example.id # resource ID of the Storage Account 
    subresource_names              = ["blob"]                           # in this example, it is Blob
  }
}

resource "azapi_update_resource" "example" {
  type        = "Microsoft.Storage/storageAccounts@2021-09-01"
  resource_id = azurerm_storage_account.example.id
  body = jsonencode({
    properties = {
      publicNetworkAccess          = "Disabled" #<------- Ensure Public network access is set to Disabled
      defaultToOAuthAuthentication = "true"     #<-------  Ensure that 'Default to Azure Active Directory authorization in the Azure portal' is set to 'Enabled'
    }
  })
}

######################################################################################################################################################################

resource "azurerm_storage_account" "example" {
  name                            = "ExampleStorageAccount"
  resource_group_name             = var.resource_group_name                # (Required) The name of the resource group in which to create the storage account. Changing this forces a new resource to be created.
  location                        = var.resource_group_location            # (Required) Specifies the supported Azure location where the resource exists.
  account_tier                    = "Standard"                         # (Required) Defines the Tier to use for this storage account.
  account_replication_type        = "LRS"                              # (Required) Defines the type of replication to use for this storage account.
  enable_https_traffic_only       = "true"                             # Boolean flag which forces HTTPS if enabled.
  allow_nested_items_to_be_public = "false"    #<------- Ensure that 'Public access level' is set to Private for blob containers
  shared_access_key_enabled       = "false"                            # Indicates whether the storage account permits requests to be authorized with the account access key via Shared Key.                                 

  blob_properties { #<------- Ensure Soft Delete is Enabled for Azure Storage
    delete_retention_policy {           
      days = 30 
    }
    container_delete_retention_policy { 
      days = 30 
    }
  }

  tags = { #<-------  Ensure that storage account uses standard organizational Resource tagging method
    usage-id            = var.usage_id
    site                = "Azure"
    cost-center         = var.cost_center
    ppmc-id             = var.ppmc_id
    toc                 = var.toc
    exp-date            = var.exp_date
    env-type            = var.env_type
    sd-period           = var.sd_period
  }
}

# Ensure Diagnostic logs are enabled for storage account
resource "azurerm_monitor_diagnostic_setting" "example" {
  name = "example"
  target_resource_id = azurerm_storage_account.example.id
  eventhub_authorization_rule_id = var.eventhub_authorization_rule_id #ID of the LAW where logs should be sent.

  log {
    category = "StorageRead" # (Required) The name of a Diagnostic Log Category for this Resource.
    enabled  = true          # Answers the question is Diagnostic Log enabled.

    retention_policy {
      enabled = false        # Answers the question is Retention Policy enabled.
    }
  }
  log {
    category = "StorageDelete"
    enabled  = true

    retention_policy {
      enabled = false
    }
  }
  log {
    category = "StorageWrite"
    enabled  = true

    retention_policy {
      enabled = false
    }
  }
}

# Ensure Storage for Critical Data are Encrypted with Customer Managed Keys
resource "azurerm_storage_account_customer_managed_key" "example" {
    storage_account_id = azurerm_storage_account.example.id # (Required)The ID of the Storage Account. Changing this forces a new resource to be created.
    key_vault_id       = var.keyvault_id                    # (Required) The ID of the Key Vault. Changing this forces a new resource to be created. 
    key_name           = var.keyvault_key_name              # (Required) The name of Key Vault Key.
}
