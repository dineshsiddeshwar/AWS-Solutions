#######################################
#Variables
#######################################

data "azurerm_client_config" "current" {}

data "azurerm_subnet" "example" {
  name                 = "subnet1"
  virtual_network_name = "my-test-vnet"
  resource_group_name  = data.azurerm_resource_group.vnet-rg.name
}

data "azurerm_resource_group" "vnet-rg" {
  name = "Vnet_RG"
}

data "azurerm_resource_group" "key-rg" {
  name = "Key-vault-RG"
}

data "azurerm_key_vault" "kv" {
  name                = "Key-Vault-for-terraform"
  resource_group_name = data.azurerm_resource_group.key-rg.name
}

data "azurerm_key_vault_secret" "container-instance-pass" {
  name         = "container-instance-pass"
  key_vault_id = data.azurerm_key_vault.kv.id
}

data "azurerm_network_security_group" "example" {
  name                = "NSG"
  resource_group_name = data.azurerm_resource_group.vnet-rg.name
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default = {
    Owner       = "Nikola"
    Environment = "Dev"
  }
}

variable "rg_name" {
  type        = string
  description = "RG name"
  default     = "Data-Factory-RG"
}

variable "rg_location" {
  type        = string
  description = "RG location"
  default     = "West Europe"
}

variable "sa_name" {
  type        = string
  description = "Storage account name"
  default     = "containergrouptest123"
}

variable "sa_location" {
  type        = string
  description = "Storage account name"
  default     = "West Europe"
}

variable "sa_tier" {
  type        = string
  description = "Storage account tier"
  default     = "Standard"
}

variable "sa_replication" {
  type        = string
  description = "Storage account tier"
  default     = "GRS"
}

variable "mds_name" {
  type        = string
  description = "Monitoring diagnostic settings"
  default     = "MDS-for-DF"
}

variable "df_name" {
  type        = string
  description = "Data Factory name"
  default     = "df-for-test"
}

variable "df_identity_ids" {
  type        = string
  description = "Identity IDS for user assigned access"
  default     = "/subscriptions/9a61192b-45f5-48c9-a34f-c62ff730fc73/resourceGroups/Data-Factory-RG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/DF-managed-identity"
}

variable "df_irshn" {
  type        = string
  description = "Data Factory integration runtime self hosted name"
  default     = "self-hosted"
}

variable "df_ira" {
  type        = string
  description = "Data Factory integration runtime Azure"
  default     = "runtime-azure"
}

variable "df_ira_location" {
  type        = string
  description = "Data Factory integration runtime Azure location"
  default     = "AutoResolve"
}

variable "p_endpoint_name" {
  type        = string
  description = "Private endpoint name"
  default     = "data-factory-endpoint"
}

variable "p_endpoint_sub_name" {
  type        = string
  description = "Private endpoint name"
  default     = "/subscriptions/9a61192b-45f5-48c9-a34f-c62ff730fc73/resourceGroups/Data-Factory-RG/providers/Microsoft.DataFactory/factories/df-example123123"
}

#variable "ra_scope" {
#  type = string
#  description = "The scope at which the Role Assignment applies to the resource."
#}

#variable "ra_user" {
#  type = string
#  description = "User or group ID"
#}

#######################################
#Resources
#######################################

resource "azurerm_resource_group" "example" {
  name     = var.rg_name
  location = var.rg_location
}

resource "azurerm_storage_account" "example" {
  name                     = var.sa_name
  resource_group_name      = var.rg_name
  location                 = var.sa_location
  account_tier             = var.sa_tier
  account_replication_type = var.sa_replication
}

resource "azurerm_data_factory" "example" {
  name                = var.df_name
  location            = var.rg_location
  resource_group_name = var.rg_name

  managed_virtual_network_enabled = true
  public_network_enabled          = false

  identity { #7. Ensure application access to Azure Data factory from other azure services is granted using Managed Identities
    type         = "UserAssigned"
    identity_ids = [var.df_identity_ids]
  }

  tags = var.tags #5. Ensure Azure data factory uses standard organizational Resource tagging method
}

resource "azurerm_data_factory_linked_service_key_vault" "example" {
  name            = "key-vault-linked-service"
  data_factory_id = azurerm_data_factory.example.id
  key_vault_id    = data.azurerm_key_vault.kv.id
}

resource "azurerm_data_factory_linked_service_azure_file_storage" "example" { #3. File data encryption using Key Vault
  name              = "example"
  data_factory_id   = azurerm_data_factory.example.id
  connection_string = azurerm_storage_account.example.primary_connection_string

  key_vault_password {
    linked_service_name = azurerm_data_factory_linked_service_key_vault.example.name
    secret_name         = data.azurerm_key_vault_secret.container-instance-pass.value
  }
}

#resource "azurerm_data_factory_integration_runtime_self_hosted" "example" { #2.
#  name            = var.df_irshn
#  data_factory_id = azurerm_data_factory.example.id
#}

resource "azurerm_data_factory_integration_runtime_azure" "example" { #2.
  name                    = var.df_ira
  data_factory_id         = azurerm_data_factory.example.id
  location                = var.df_ira_location
  virtual_network_enabled = true
}

resource "azurerm_private_endpoint" "example" {
  name                = var.p_endpoint_name
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  subnet_id           = data.azurerm_subnet.example.id

  private_service_connection { #1. Ensure that Azure Data factory is accessed only using private Endpoint
    name                           = var.p_endpoint_name
    is_manual_connection           = false
    private_connection_resource_id = var.p_endpoint_sub_name
    subresource_names              = ["dataFactory"]
  }
}

resource "azurerm_monitor_diagnostic_setting" "example" { #4. Ensure Diagnostic log for 'AllMetrics' is enabled for Azure Data factory
  name               = var.mds_name
  target_resource_id = azurerm_data_factory.example.id
  storage_account_id = azurerm_storage_account.example.id

  metric {
    category = "AllMetrics"
  }
}

/*
resource "azurerm_role_assignment" "example" { #6. Ensure Azure Data Factory implements Role Based Access Control
  scope                = var.ra_scope #<------- (Required) The scope at which the Role Assignment applies to the resource.
  role_definition_name = "Viewer" #<------- Role for the user or group
  principal_id         = var.ra_user #<------- User or group ID
}
*/
