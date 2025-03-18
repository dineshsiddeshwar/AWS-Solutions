#######################################
#Variables
#######################################

data "azurerm_resource_group" "rg" {
  name = "Key-vault-RG"
}

data "azurerm_key_vault" "kv" {
  name                = "Key-Vault-for-terraform"
  resource_group_name = data.azurerm_resource_group.rg.name
}

data "azurerm_key_vault_key" "example" {
  name         = "cr-key"
  key_vault_id = data.azurerm_key_vault.kv.id
}

data "azurerm_virtual_network" "example" {
  name                = "vn-example"
  resource_group_name = azurerm_resource_group.rg.name
}

data "azurerm_subnet" "example" {
  name                 = "endpoint"
  virtual_network_name = "production"
  resource_group_name  = azurerm_resource_group.rg.name
}

data "azurerm_network_security_group" "example" {
  name                = "acceptanceTestSecurityGroup1"
  resource_group_name = azurerm_resource_group.rg.name
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
  default     = "Container-Reg-RG"

}

variable "rg_location" {
  type        = string
  description = "RG location"
  default     = "West Europe"
}

variable "uai_name" {
  type        = string
  description = "User assinged identity name"
}

variable "sa_name" {
  type        = string
  description = "Storage account name"
  default     = "containerregtest123"
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

variable "cr_name" {
  type        = string
  description = "Container registry name"
  default     = "examplecgfortesting123"
}

variable "cr_sku" {
  type        = string
  description = "Container registry SKU"
  default     = "Premium"
}

variable "georeplication" {
  type        = string
  description = "Georeplication location"
  default     = "East US"
}

variable "identity_type" {
  type        = string
  description = "Identity type for container registry"
  default     = "UserAssigned"
}

variable "identity_ids" {
  type        = string
  description = "IDS of Managed identity"
}

variable "cr_sm_name" {
  type        = string
  description = "Container Reg scope name"
  default     = "example-scope-map"
}

variable "cr_t_name" {
  type        = string
  description = "Container Reg token name"
  default     = "exampletoken"
}

variable "mds_name" {
  type        = string
  description = "Monitoring diagnostic settings"
  default     = "MDS-for-CR"
}

variable "pe_name" {
  type        = string
  description = "Private endpoint name"
  default     = "example-endpoint"
}

variable "psc_name" {
  type        = string
  description = "Private service connection name"
  default     = "private_service_for_cr"
}

variable "psc_id" {
  type        = string
  description = "ID of container registry"
}

variable "ra_scope" {
  type        = string
  description = "The scope at which the Role Assignment applies to the resource."
}

variable "ra_user" {
  type        = string
  description = "User or group ID"
}

variable "log_retention_days" {
  type = string
  description = "Retention policy for logs"
  default = "30"
}

#######################################
#Resources
#######################################

resource "azurerm_resource_group" "example" {
  name     = var.rg_name
  location = var.rg_location
}

resource "azurerm_user_assigned_identity" "example" {
  resource_group_name = var.rg_name
  location            = var.rg_location
  name                = var.uai_name
}


resource "azurerm_storage_account" "example" {
  name                     = var.sa_name
  resource_group_name      = var.rg_name
  location                 = var.sa_location
  account_tier             = var.sa_tier
  account_replication_type = var.sa_replication
}

resource "azurerm_container_registry" "example" {
  name                  = var.cr_name
  resource_group_name   = var.rg_name
  location              = var.sa_location
  sku                   = var.cr_sku
  admin_enabled         = false
  data_endpoint_enabled = true

  georeplications {
    location                = var.georeplication
    zone_redundancy_enabled = true
  }

  public_network_access_enabled = false

  trust_policy { #10. Ensure content trust is enabled in Azure Container Registry. Works only on Premium
    enabled = true
  }

  identity { #5. Ensure Azure container Registry access is granted only using Managed Identities
    type         = var.identity_type
    identity_ids = var.identity_ids
  }

  encryption { #13. Ensure Container images in registry are Encrypted with Customer Managed Keys
    enabled            = true
    key_vault_key_id   = data.azurerm_key_vault_key.example.id
    identity_client_id = azurerm_user_assigned_identity.example.client_id
  }

  tags = var.tags #8. Ensure Azure Container Registry use standard organizational Resource tagging method
}

resource "azurerm_container_registry_scope_map" "example" {
  name                    = var.cr_sm_name
  container_registry_name = azurerm_container_registry.example.name
  resource_group_name     = azurerm_resource_group.example.name
  actions = [
    "repositories/repo1/content/read",
    "repositories/repo1/content/write"
  ]
}

resource "azurerm_container_registry_token" "example" { #14. Ensure token or service map is used to access the specific Repositories in Registry
  name                    = var.cr_t_name
  container_registry_name = azurerm_container_registry.example.name
  resource_group_name     = azurerm_resource_group.example.name
  scope_map_id            = azurerm_container_registry_scope_map.example.id
}

resource "azurerm_monitor_diagnostic_setting" "example" { #7. Ensure Diagnostic logs for 'ContainerRegistryRepositoryEvents' and 'ContainerRegistryLoginEvents' are enabled and are forwarded to Splunk
  name               = var.mds_name
  target_resource_id = azurerm_container_registry.example.id
  storage_account_id = azurerm_storage_account.example.id

  log {
    category = "ContainerRegistryRepositoryEvents"
    retention_policy {
      enabled = "true"
      days    = var.log_retention_days
    }
  }
  log {
    category = "ContainerRegistryLoginEvents"
    retention_policy {
      enabled = "true"
      days    = var.log_retention_days
    }
  }
  metric {
    category = "AllMetrics"
  }
}

resource "azurerm_private_endpoint" "example" {
  name                = var.pe_name
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  subnet_id           = azurerm_subnet.example.id

  private_service_connection { #1. Ensure that Azure container registry is deployed using private Endpoint
    name                           = var.psc_name
    is_manual_connection           = false
    private_connection_resource_id = var.psc_id
    subresource_names              = ["registry"]
  }
}

resource "azurerm_network_security_rule" "example" { #12. Ensure Service tags are enabled for the Azure Container Registry. NOT SURE THAT WE NEED TO ENABLE IT BUT HERE IS HOW ITS IMPLEMENTED.
  name                        = "Service-tags"
  priority                    = 100
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "*"
  source_address_prefix       = "*"
  destination_address_prefix  = "AzureContainerRegistry"
  resource_group_name         = azurerm_resource_group.example.name
  network_security_group_name = azurerm_network_security_group.example.name
}

# resource "azurerm_role_assignment" "example" { #3. Ensure Azure container Registry implements Role Based Access Control
#  scope                = var.ra_scope
#  role_definition_name = "Viewer" #<------- Role for the user or group
#  principal_id         = var.ra_user
#}
