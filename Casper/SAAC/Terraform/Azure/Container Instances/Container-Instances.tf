#######################################
#Variables
#######################################

data "azurerm_client_config" "current" {}

data "azurerm_resource_group" "key-rg" {
  name = "Key-vault-RG"
}

data "azurerm_resource_group" "vnet-rg" {
  name = "Vnet_RG"
}

data "azurerm_key_vault" "kv" {
  name                = "Key-Vault-for-terraform"
  resource_group_name = data.azurerm_resource_group.key-rg.name
}

data "azurerm_key_vault_secret" "container-instance-pass" {
  name         = "container-instance-pass"
  key_vault_id = data.azurerm_key_vault.kv.id
}


data "azurerm_subnet" "example" {
  name                 = "subnet"
  virtual_network_name = "my-test-vnet"
  resource_group_name  = data.azurerm_resource_group.vnet-rg.name
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
  default     = "Container-Group-RG"

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
  default     = "MDS-for-CR"
}

variable "cg_name" {
  type        = string
  description = "User or group ID"
  default     = "Container-group-example"
}

variable "cg_ip_type" {
  type        = string
  description = "Ip address type"
  default     = "Private"
}

variable "cg_os_type" {
  type        = string
  description = "OS type"
  default     = "Linux"
}

variable "cg_ic_name" {
  type    = string
  default = "admin"
}

variable "cg_ic_server" {
  type        = string
  description = "User or group ID"
  default     = "key-vault-for-terraform.vault.azure.net"
}

variable "identity_type" {
  type        = string
  description = "User or group ID"
  default     = "UserAssigned"
}

variable "container_name" {
  type        = string
  description = "Container name"
  default     = "Hello-world"
}

variable "container_image" {
  type        = string
  description = "Image used for reg"
  default     = "mcr.microsoft.com/azuredocs/aci-helloworld:latest"
}

variable "container_cpu" {
  type        = string
  description = "CPU"
  default     = "0.5"
}

variable "container_memory" {
  type        = string
  description = "Memory"
  default     = "1.5"
}

variable "port" {
  type        = string
  description = "Ports for container use"
  default     = "443"
}

variable "protocol" {
  type        = string
  description = "Protocol for container use"
  default     = "TCP"
}

variable "np_name" {
  type        = string
  description = "Network profile name"
  default     = "ci-network-profile"
}

variable "cni_name" {
  type        = string
  description = "Container network insterface name"
  default     = "ci-nic"
}

variable "ip_conf_name" {
  type        = string
  description = "IP configuration name"
  default     = "ci-ip-config"
}

variable "uai_name" {
  type        = string
  description = "User assigned identity name"
  default     = "ci-example"
}

variable "nwfl_name" {
  type        = string
  description = "Network watcher log flow name"
  default     = "example-log"
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

resource "azurerm_container_group" "example" {
  name                = var.cg_name
  location            = var.rg_location
  resource_group_name = var.rg_name
  ip_address_type     = var.cg_ip_type
  os_type             = var.cg_os_type
  network_profile_id  = azurerm_network_profile.example.id
  depends_on          = [azurerm_storage_account.example]

  image_registry_credential { #7. Ensure container administrative credentials are vaulted using enterprise vaulting solutions.
    username = var.cg_ic_name
    password = data.azurerm_key_vault_secret.container-instance-pass.value
    server   = var.cg_ic_server
  }

  identity { #6. Ensure Azure container instance access is granted only using Managed Identities.
    type         = var.identity_type
    identity_ids = [azurerm_user_assigned_identity.example.id]
  }

  container {
    name   = var.container_name
    image  = var.container_image
    cpu    = var.container_cpu
    memory = var.container_memory

    ports {
      port     = var.port
      protocol = var.protocol
    }
  }

  tags = var.tags #11. Ensure Azure Container Instances use standard organizational Resource tagging method.

}

resource "azurerm_network_profile" "example" {
  name                = var.np_name
  location            = var.rg_location
  resource_group_name = var.rg_name

  container_network_interface { #1. Ensure Azure Container instance is deployed in the Virtual networks and Network Security Groups are used to protect network.
    name = var.cni_name

    ip_configuration {
      name      = var.ip_conf_name
      subnet_id = data.azurerm_subnet.example.id
    }
  }
}

resource "azurerm_user_assigned_identity" "example" {
  resource_group_name = var.rg_name
  location            = var.rg_location
  name                = var.uai_name
}


resource "azurerm_advanced_threat_protection" "example" {
  target_resource_id = azurerm_resource_group.example.id
  enabled            = true #Error: Azure Defender for Data Services settings are not supported on resources of type containerGroups.
}

resource "azurerm_network_watcher_flow_log" "test" { #10. Ensure NSG flow log data is enabled and encrypted using customer managed key.
  network_watcher_name = azurerm_network_watcher.test.name
  resource_group_name  = azurerm_resource_group.example.name
  name                 = var.nwfl_name

  network_security_group_id = azurerm_network_security_group.test.id
  storage_account_id        = azurerm_storage_account.example.id
  enabled                   = true

  retention_policy {
    enabled = true
    days    = 7
  }

  traffic_analytics {
    enabled               = true
    workspace_id          = azurerm_log_analytics_workspace.test.workspace_id
    workspace_region      = azurerm_log_analytics_workspace.test.location
    workspace_resource_id = azurerm_log_analytics_workspace.test.id
    interval_in_minutes   = 10
  }
}


resource "azurerm_role_assignment" "example" { #4. Ensure Azure container implements RBAC access control.
  scope                = var.ra_scope          #<------- (Required) The scope at which the Role Assignment applies to the resource.
  role_definition_name = "Viewer"              #<------- Role for the user or group
  principal_id         = var.ra_user           #<------- User or group ID
}