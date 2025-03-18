#######################################
#Resources
#######################################

resource "azurerm_resource_group" "resource_group" {
  name     = var.resource_group.name
  location = var.resource_group.location
}

resource "azurerm_user_assigned_identity" "user_assigned_identity" {
  resource_group_name = var.resource_group.name
  location            = var.resource_group.location
  name                = var.user_assigned_identity_name
}

resource "azurerm_storage_account" "storage_account" {
  name                     = var.storage_account.name
  resource_group_name      = var.resource_group.name
  location                 = var.storage_account.location
  account_tier             = var.storage_account.tier
  account_replication_type = var.storage_account.replication
}

resource "azurerm_container_registry" "container_registry" {
  name                  = var.container_registry.name
  resource_group_name   = var.resource_group.name
  location              = var.resource_group.location
  sku                   = var.container_registry.sku
  admin_enabled         = false
  data_endpoint_enabled = var.container_registry.data_endpoint_enabled
  public_network_access_enabled = false # This is only supported on resources with the Standard or Premium SKU.
  anonymous_pull_enabled = false 
  export_policy_enabled = false # Ensure container images or repository is locked and exportPolicy is disabled for container registry

  georeplications {
    location                = var.container_registry.georeplication_location
    zone_redundancy_enabled = var.container_registry.zone_redundancy_enabled
  }


  trust_policy { # Ensure content trust is enabled in Azure Container Registry. Works only on Premium
    enabled = var.container_registry.trust_policy_enabled
  }

  identity { # Ensure Azure container Registry access is granted only using Managed Identities
    type         = var.container_registry.identity_type
    identity_ids = var.container_registry.identity_ids
  }

  encryption { # Ensure Container images in registry are Encrypted with Customer Managed Keys
    enabled            = var.container_registry.encryption_enabled
    key_vault_key_id   = data.azurerm_key_vault_key.key_vault_key.id
    identity_client_id = azurerm_user_assigned_identity.user_assigned_identity.client_id
  }

  tags =var.common_tags # Ensure Azure Container Registry use standard organizational Resource tagging method
    
}

resource "azurerm_container_registry_scope_map" "scope_map" {
  name                    = var.container_registry.scope_map_name
  container_registry_name = azurerm_container_registry.container_registry.name
  resource_group_name     = azurerm_resource_group.resource_group.name
  actions = [
    "repositories/repo1/content/read",
    "repositories/repo1/content/write"
  ]
}

resource "azurerm_container_registry_token" "token" { # Ensure token or service map is used to access the specific Repositories in Registry
  name                    = var.container_registry.token_name
  container_registry_name = azurerm_container_registry.container_registry.name
  resource_group_name     = azurerm_resource_group.resource_group.name
  scope_map_id            = azurerm_container_registry_scope_map.scope_map.id
}

resource "azurerm_monitor_diagnostic_setting" "mds" { # Ensure Diagnostic logs for 'ContainerRegistryRepositoryEvents' and 'ContainerRegistryLoginEvents' are enabled.
  name               = var.monitor_diagnostic_setting.name
  target_resource_id = azurerm_container_registry.container_registry.id
  storage_account_id = azurerm_storage_account.storage_account.id

  log {
    category = "ContainerRegistryRepositoryEvents"
    retention_policy {
      enabled = var.monitor_diagnostic_setting.retention_policy_enabled
      days    = var.monitor_diagnostic_setting.retention_policy_days
    }
  }
  log {
    category = "ContainerRegistryLoginEvents"
    retention_policy {
      enabled = var.monitor_diagnostic_setting.retention_policy_enabled
      days    = var.monitor_diagnostic_setting.retention_policy_days
    }
  }
  metric {
    category = var.monitor_diagnostic_setting.metric_catagory
  }
}

resource "azurerm_private_endpoint" "private_endpoint" {
  name                = var.private_endpoint.name
  location            = azurerm_resource_group.resource_group.location
  resource_group_name = azurerm_resource_group.resource_group.name
  subnet_id           = data.azurerm_subnet.subnet.id

  private_service_connection { # Ensure that Azure container registry is deployed using private Endpoint
    name                           = var.private_endpoint.private_service_connection_name
    is_manual_connection           = var.private_endpoint.private_service_connection_manual
    private_connection_resource_id = var.private_endpoint.private_service_connection_id
    subresource_names              = var.private_endpoint.private_service_connection_subresource_names
  }
}

resource "azurerm_network_security_rule" "nsg" { # Ensure Service tags are enabled for the Azure Container Registry.
  name                        = var.ns_rule.name
  priority                    = var.ns_rule.priority
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = var.ns_rule.source_port_range
  destination_port_range      = var.ns_rule.destination_port_range
  source_address_prefix       = var.ns_rule.source_address_prefix
  destination_address_prefix  = "AzureContainerRegistry"
  resource_group_name         = azurerm_resource_group.resource_group.name
  network_security_group_name = var.network_security_group_name
}

resource "azurerm_role_assignment" "role_assignment" {                    #  Ensure ACR utilizes access controls to enforce least privilage using Role based access control.
  name                 = var.role_assignment.name 
  scope                = azurerm_container_registry.container_registry.id  #<------- (Required) The scope at which the Role Assignment applies to the resource.
  role_definition_name = var.role_assignment.role_definition_name #<------- Role for the user or group
  principal_id         = var.role_assignment.user                 #<------- User or group ID
}

#  Ensure ACR data is encrypted in transit protocol TLS1.2 to protect data in transit in ACR is enabled by using latest docker client version - is implemented when latest docker client is used
#  Ensure administrative tasks are performed only in admin-r workstations - Implemented as part of organization deplyment and monitored using detective rule
#  Ensure that Container Registry authentication is disabled and uses Azure Active Directory (Azure AD) service principal for Admin Authentication - access tokens implementation is not provided such that access tokens are not deployed
#  Ensure CI pipeline is integrated with security scanning before pushing to private registry - will be implemented in application using ACR example ACR intigration to AKS
#  Ensure Activity logging is enabled for Azure Container Registry - Implemented in organixzational runbook at subscription level


