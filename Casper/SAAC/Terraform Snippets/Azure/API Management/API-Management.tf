######################################################################################################################################################################
############################################################       Variables        #######################################################################
######################################################################################################################################################################

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default = {
    Owner       = "Nikola"
    Environment = "Dev"
  }
}

variable "location" {
  type        = string
  description = "Location of the resource"
  default     = "West Europe"
}

variable "storageacc_name" {
  type        = string
  description = "Storage account name"
  default     = "apimanagement123"
}

variable "api_management_name" {
  type        = string
  description = "API Management name"
  default     = "apimanagement123"
}

variable "rg_name" {
  type        = string
  description = "Resource group name"
  default     = "api-management-rg"
}

variable "mds_name" {
  type        = string
  description = "Monitoring diagnostic settings"
  default     = "monitoring-diagnostic-example"
}

variable "sku_name" {
  type        = string
  description = "describe your variable"
  default     = "Developer_1"
}

variable "create_resource_group" {
  description = "Whether to create resource group and use it for all networking resources"
  default     = "true"
}

variable "account_tier" {
  type        = string
  description = "Tier of storage account"
  default     = "Standard"
}

variable "account_replica_type" {
  type        = string
  description = "Storage account replica tier"
  default     = "GRS"
}

variable "pub_name" {
  type        = string
  description = "Publisher name"
  default     = "Company example"
}

variable "pub_email" {
  type        = string
  description = "Publisher email"
  default     = "example@email.com"
}

variable "vn_name" {
  type = string
  description = "Virtuan network name"
  default = "PostgreSQL-PN"
}

variable "vn_address_space" {
  type = string
  description = "Virtual network address space"
  default = "10.0.0.0/16"
}

variable "vn_type" {
  type = string
  description = "Virtual network type"
  default = "Internal"
}

variable "subnet_name" {
  type = string
  description = "Subnet name"
  default = "endpoint"
}

variable "subnet_address_prefix" {
  type = string
  description = "Subnet address prefix"
  default = "10.0.2.0/24"
}

variable "pe_name" {
  type = string
  description = "Private endpoint name"
  default = "API-endpoint"
}

variable "pe_location" {
  type = string
  description = "Private endpoint location"
  default = "West Europe"
}

variable "psc_name" {
  type = string
  description = "Private service connection name"
  default = "api-privateserviceconnection"
}

variable "ra_scope" {
  type = string
  description = "The scope at which the Role Assignment applies to the resource."
}

variable "ra_principal_id" {
  type = string
  description = "User or group ID"
}

######################################################################################################################################################################
############################################################       REQUIREMENTS SECTION        #######################################################################
######################################################################################################################################################################

resource "azurerm_resource_group" "example" {
  name     = var.rg_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_storage_account" "storageacc" {
  name                     = var.storageacc_name
  location                 = var.location
  resource_group_name      = azurerm_resource_group.example.name
  account_tier             = var.account_tier
  account_replication_type = var.account_replica_type
}

resource "azurerm_virtual_network" "example" {
  name                = var.vn_name
  address_space       = var.vn_address_space
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
}

resource "azurerm_subnet" "example" {
  name                 = var.subnet_name
  resource_group_name  = azurerm_resource_group.example.name
  virtual_network_name = azurerm_virtual_network.example.name
  address_prefixes     = var.subnet_address_prefix

  enforce_private_link_endpoint_network_policies = true
}

resource "azurerm_api_management" "api" {
  name                = var.api_management_name
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  publisher_name      = var.pub_name
  publisher_email     = var.pub_email
  sku_name            = var.sku_name #4.1.1 Deploy Premium SKU instance

    virtual_network_type = var.vn_type
    virtual_network_configuration {
      subnet_id = azurerm_subnet.example.id #4.4.1 Connect API Management to VNET
    }

  tags = var.tags #4.5.1 Ensure that service uses standard organizational Resource tagging method
}

resource "azurerm_monitor_diagnostic_setting" "example" {
  name               = var.mds_name
  target_resource_id = azurerm_api_management.api.id
  storage_account_id = azurerm_storage_account.storageacc.id

  log { #4.6.1 Enable audit logging
    category = "GatewayLogs"
    retention_policy {
      enabled = "true"
      days    = "30"
    }
  }
  metric {
    category = "AllMetrics"
  }
}

#resource "azurerm_role_assignment" "example" { #4.2.1 RBAC
#  scope                = var.ra_scope (Required) The scope at which the Role Assignment applies to the resource.
#  role_definition_name = "Viewer" #<------- Role for the user or group
#  principal_id         = var.ra_principal_id #<------- User or group ID
#}

resource "azurerm_private_endpoint" "example" { #4.4.3 Leverage private endpoint
  name                = var.pe_name
  location            = var.pe_location
  resource_group_name = azurerm_resource_group.example.name
  subnet_id           = azurerm_subnet.example.id

  private_service_connection {
    name                           = var.psc_name
    private_connection_resource_id = azurerm_api_management.api.id
    is_manual_connection           = false
  }
}
