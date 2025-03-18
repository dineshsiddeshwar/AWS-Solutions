########################################
#Variables
#######################################

data "azurerm_client_config" "current" {}

data "azurerm_subnet" "node-subnet" {
  name                 = "node-subnet"
  virtual_network_name = "my-test-vnet"
  resource_group_name  = data.azurerm_resource_group.vnet-rg.name
}

data "azurerm_subnet" "pod-subnet" {
  name                 = "pod-subnet"
  virtual_network_name = "my-test-vnet"
  resource_group_name  = data.azurerm_resource_group.vnet-rg.name
}

data "azurerm_resource_group" "vnet-rg" {
  name = "Vnet_RG"
}

data "azurerm_resource_group" "key-rg" {
  name = "Key-vault-RG"
}

data "azurerm_resource_group" "nw-rg" {
  name = "NetworkWatcherRG"
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

data "azurerm_network_watcher" "example" {
  name                = "NetworkWatcher_westeurope"
  resource_group_name = data.azurerm_resource_group.nw-rg.name
}

data "azurerm_log_analytics_workspace" "example" {
  name                = "Log-Analytics"
  resource_group_name = data.azurerm_resource_group.nw-rg.name
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
  default     = "k8n-RG"
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
  default     = "MDS-for-k8n"
}

variable "kc_name" {
  type        = string
  description = "Kubernetes cluster name"
  default     = "k8n-cluster"
}

variable "dns_prefix" {
  type        = string
  description = "DNS prefix name"
  default     = "exampleaks1"
}

variable "kc_acu" {
  type        = string
  description = "Automatic channel upgrade"
  default     = "stable"
}

variable "kc_private_dns" {
  type        = string
  description = "Private DNS zone id"
  default     = "System"
}

variable "np_name" {
  type        = string
  description = "Node pool name"
  default     = "nodepool"
}

variable "np_max" {
  type        = string
  description = "Maximum number of pods"
  default     = "50"
}

variable "np_count" {
  type        = string
  description = "Number of nodes"
  default     = "2"
}

variable "vm_size" {
  type        = string
  description = "VM size"
  default     = "Standard_D2_v2"
}

variable "np_plugin" {
  type        = string
  description = "Network plugin"
  default     = "azure"
}

variable "np_service_cidr" {
  type        = string
  description = "Service CIDR"
  default     = "10.0.4.0/24"
}

variable "np_docker_cidr" {
  type        = string
  description = "Docker CIDR"
  default     = "172.17.0.1/16"
}

variable "np_dns_ip" {
  type        = string
  description = "DNS service IP"
  default     = "10.0.4.10"
}

variable "k_identity" {
  type        = string
  description = "Identity"
  default     = "SystemAssigned"
}

variable "ad_tenant_id" {
  type        = string
  description = "ID of the AD you want to connect"
  default     = "733b821a-403c-4bb9-88f0-563536721468"
}

variable "ad_admin_group_ids" {
  type        = list(any)
  description = "Admin group IDS"
  default     = ["f1a498af-cf10-49ed-a8e0-5abd39e8316f"]
}

variable "kv_sri" {
  type        = string
  description = "Secret rotation interval"
  default     = "2m"
}

variable "nwfl_name" {
  type        = string
  description = "Network watcher flow log name"
  default     = "Flow-log-example"
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

resource "azurerm_kubernetes_cluster" "example" {
  name                          = var.kc_name
  location                      = var.rg_location
  resource_group_name           = var.rg_name
  dns_prefix                    = var.dns_prefix
  automatic_channel_upgrade     = var.kc_acu #12. Ensure node pools are always updated to the latest Kubernetes version
  local_account_disabled        = true
  public_network_access_enabled = true
  private_cluster_enabled       = true #1. Ensure Private AKS Cluster is implemented
  private_dns_zone_id           = var.kc_private_dns
  enable_pod_security_policy    = false #18. Error: The AKS API has removed support for this field on 2020-10-15 and is no longer possible to configure this the Pod Security Policy - as such you'll need to set `enable_pod_security_policy` to `false`

  default_node_pool {
    name           = var.np_name
    max_pods       = var.np_max
    node_count     = var.np_count
    vm_size        = var.vm_size
    vnet_subnet_id = data.azurerm_subnet.node-subnet.id #2. Ensure Azure Kubernetes Service is deployed in the Virtual network
    pod_subnet_id  = data.azurerm_subnet.pod-subnet.id
  }

  network_profile {
    network_plugin     = var.np_plugin #4. Ensure Azure CNI network configuration is selected
    service_cidr       = var.np_service_cidr
    docker_bridge_cidr = var.np_docker_cidr
    dns_service_ip     = var.np_dns_ip
  }

  microsoft_defender {
    log_analytics_workspace_id = data.azurerm_log_analytics_workspace.example.id
  }

  identity {
    type = var.k_identity
  }


  azure_active_directory_role_based_access_control { #15. Azure AD
    managed                = true
    tenant_id              = var.ad_tenant_id
    admin_group_object_ids = var.ad_admin_group_ids
    azure_rbac_enabled     = true
  }

  key_vault_secrets_provider { #8. Ensure Container Storage Interface (CSI) drivers are enabled on Azure Kubernetes Service
    secret_rotation_enabled  = true
    secret_rotation_interval = var.kv_sri
  }

  tags = var.tags #13. Ensure Azure Kubernetes service uses standard organizational Resource tagging method
}


resource "azurerm_monitor_diagnostic_setting" "example" { #9. Ensure Activity logging is enabled for Azure Kubernetes service
  name               = var.mds_name
  target_resource_id = azurerm_kubernetes_cluster.example.id
  storage_account_id = azurerm_storage_account.example.id

  log { #11. Ensure Diagnostic logs for 'Kubeapi' and 'Kubeaudit' are enabled and are forwarded to Splunk
    category = "kube-audit"
  }

  log {
    category = "kube-apiserver"
  }

  metric {
    category = "AllMetrics"
  }
}


resource "azurerm_network_watcher_flow_log" "example" { #10. Ensure NSG flow log data is enabled for AKS Cluster Subnet
  network_watcher_name = data.azurerm_network_watcher.example.name
  resource_group_name  = data.azurerm_resource_group.nw-rg.name
  name                 = var.nwfl_name

  network_security_group_id = data.azurerm_network_security_group.example.id
  storage_account_id        = azurerm_storage_account.example.id
  enabled                   = true

  retention_policy {
    enabled = true
    days    = 7
  }

  traffic_analytics {
    enabled               = true
    workspace_id          = data.azurerm_log_analytics_workspace.example.workspace_id
    workspace_region      = data.azurerm_log_analytics_workspace.example.location
    workspace_resource_id = data.azurerm_log_analytics_workspace.example.id
    interval_in_minutes   = 10
  }
}

/*
resource "azurerm_role_assignment" "example" { #5. Ensure least privilege access method is implemented using Role-based access control (RBAC)
  scope                = var.ra_scope #<------- (Required) The scope at which the Role Assignment applies to the resource.
  role_definition_name = "Viewer" #<------- Role for the user or group
  principal_id         = var.ra_user #<------- User or group ID
}
*/
