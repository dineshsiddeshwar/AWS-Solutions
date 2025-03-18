#######################################
#Resources
#######################################

resource "azurerm_resource_group" "resource_group" {
  name     = var.resource_group.name
  location = var.resource_group.location
}

resource "azurerm_storage_account" "storage_account" {
  name                     = var.storage_account.name
  resource_group_name      = var.resource_group.name
  location                 = var.storage_account.location
  account_tier             = var.storage_account.tier
  account_replication_type = var.storage_account.replication
}

resource "azurerm_container_group" "container_group" {
  name                = var.container_group.name
  location            = var.resource_group.location
  resource_group_name = var.resource_group.name
  ip_address_type     = var.container_group.ip_address_type
  os_type             = var.container_group.os_type
  network_profile_id  = azurerm_network_profile.network_profile.id

  depends_on = [azurerm_storage_account.storage_account]

  image_registry_credential { # Ensure container administrative credentials are vaulted using enterprise vaulting solutions.
    username = var.container_group.image_reg_user
    password = data.azurerm_key_vault_secret.container_instance_pass.value
    server   = var.container_group.image_reg_server # Ensure only organization approved container images are used for deployment in production 
  }

  identity { # Ensure Azure container instance access is granted only using Managed Identities.
    type         = var.container_group.identity_type
    identity_ids = [azurerm_user_assigned_identity.user_assigned_identity.id]
  }

  container {
    name   = var.container_group.container_name
    image  = var.container_group.container_image # Ensure only organization approved container images are used for deployment in production. [Add location to your apporoved images]
    cpu    = var.container_group.container_cpu
    memory = var.container_group.container_memory

    ports {
      port     = var.container_group.port
      protocol = var.container_group.protocol
    }
  }
# Ensure that Sensitive data is protected by using Secure Environment variables or Secret volumes in Azure Container Instance
  init_container {
    name   = var.container_group.container_name
    image  = var.container_group.container_image 
    secure_environment_variables = var.ACI_secure_environment_variables
  }

  tags =var.common_tags # Ensure Azure Container Instances use standard organizational Resource tagging method
}

resource "azurerm_network_profile" "network_profile" {
  name                = var.network_profile.name
  location            = var.resource_group.location
  resource_group_name = var.resource_group.name

  container_network_interface { # Ensure Azure Container instance is deployed in Private Endpoint 
    name = var.network_profile.container_network_interface_name
    ip_configuration {
      name      = var.network_profile.ip_configuration_name
      subnet_id = data.azurerm_subnet.subnet.id
    }
  }
}

resource "azurerm_user_assigned_identity" "user_assigned_identity" {
  resource_group_name = var.resource_group.name
  location            = var.resource_group.location
  name                = var.user_assigned_identity_name
}


resource "azurerm_advanced_threat_protection" "advanced_threat_protection" {
  target_resource_id = azurerm_resource_group.resource_group.id
  enabled            = var.enable.true #Error: Azure Defender for Data Services settings are not supported on resources of type containerGroups.
}

resource "azurerm_role_assignment" "example" {                    # Ensure Azure container implements RBAC access control.
  scope                = var.role_assignment.scope                #<------- (Required) The scope at which the Role Assignment applies to the resource.
  role_definition_name = var.role_assignment.role_definition_name #<------- Role for the user or group
  principal_id         = var.role_assignment.user                 #<------- User or group ID
}

#  Ensure that private container registry is used to store the container images - this is implemented in ACR Runbook
#  Ensure the application accessing the Azure container instances is running on a platform that supports TLS 1.2 or above 
#  Ensure administrative tasks are performed only on admin-e workstations - Not part of terraform code
#  Ensure that Container Instance are integrated with Malware and Vulnerability Scanner tools  
#  Ensure organizational CI/CD pipeline is integrated with Container vulnerability scanner to scan container images - Can not be implemented as part of Terraform, Implemented as org deployment standard
#  Ensure Activity logging is enabled for Azure Container Instance  - Implemented at Organizational runbook in Subscription level




