variable "prefix" {
  description = "Name of the resource where the storage will be created"
  type        = string
  default     = "EY-GDS-demo"
}

variable "location" {
  description = "One of the Azure region for the resource provisioning"
  type        = string
  default     = "eastus"
}

# Azure Storage Account variables resource

variable "storage_account_name" {
  description = "The name of the azure storage account"
  default     = ""
  type        = string
}

variable "account_kind" {
  description = "Defines the Kind of account. Valid options are Storage, StorageV2 and BlobStorage. Changing this forces a new resource to be created."
  type        = string
  default     = "StorageV2"
}

variable "account_tier" {
  description = "Defines the Tier to use for this storage account. Valid options are Standard and Premium. Changing this forces a new resource to be created."
  type        = string
  default     = "Standard"
}

variable "account_replication_type" {
  description = "Defines the type of replication to use for this storage account. Valid options are LRS, GRS, RAGRS and ZRS."
  type        = string
  default     = "LRS"
}

variable "access_tier" {
  description = "Defines the access tier for BlobStorage accounts. Valid options are Hot and Cold, defaults to Hot."
  type        = string
  default     = "Hot"
}

variable "https_traffic" {
  description = "Boolean flag which forces HTTPS if enabled"
  type        = string
  default     = true
}

variable "network_rules" {
  description = "default_action - (Required) Specifies the default action of allow or deny when no other rules match. Valid options are Deny or Allow. bypass - (Optional) Specifies whether traffic is bypassed for Logging/Metrics/AzureServices. Valid options are any combination of Logging, Metrics, AzureServices, or None. ip_rules - (Optional) List of public IP or IP ranges in CIDR Format. Only IPV4 addresses are allowed. Private IP address ranges (as defined in RFC 1918) are not allowed. virtual_network_subnet_ids - (Optional) A list of resource ids for subnets."
  type = list(object({
    default_action                 = string
    bypass                         = list(string)
    ip_rules                       = list(string)
    virtual_network_subnet_ids     = list(string)
  }))
  default = []
}

variable "tags" {
  description = "Default tags to apply on the resource"
  type        = map

  default = {
    terraform = "true"
  }
}

variable "nested_items" {
  description = "Allow nested items to be public for the storage account"
  default     = false
  type        = bool
}


variable "min_tls_version" {
  description = "The minimum supported TLS version for the storage account"
  default     = "TLS1_2"
  type        = string
}

variable "enable_advanced_threat_protection" {
  description = "Boolean flag which controls if advanced threat protection is enabled."
  default     = true
  type        = bool
}
 
variable "infrastructure_encryption" {
  description = "Boolean flag which controls if infrastructure encryption is enabled."
  default     = true
  type        = bool

}

variable "blob_soft_delete_retention_days" {
  description = "Specifies the number of days that the blob should be retained, between `1` and `365` days. Defaults to `7`"
  default     = 7
  type        = number
}

variable "container_soft_delete_retention_days" {
  description = "Specifies the number of days that the blob should be retained, between `1` and `365` days. Defaults to `7`"
  default     = 7
  type        = number
}

variable "enable_versioning" {
  description = "Is versioning enabled? Default to `true`"
  default     = true
  type        = bool
}

variable "last_access_time_enabled" {
  description = "Is the last access time based tracking enabled? Default to `true`"
  default     = true
  type        = bool
}

variable "change_feed_enabled" {
  description = "Is the blob service properties for change feed events enabled?"
  default     = true
  type        = bool
}

variable "diagnostic_name" {
  description = "Name of the resource where the storage will be created"
  type        = string
  default     = "EY-GDS-demo-diagnostic"
}

variable "sa_account_id" {
  description = "Storage account ID"
  type        = string
  default     = "/subscriptions/2deda99b-1d35-4ee1-a4ce-aa5a3875266a/resourceGroups/EYGDS-sec-rg/providers/Microsoft.Storage/storageAccounts/mlsecops"
}


#variable "eventhub_id" {
#  description = "Event Hub ID"
#  type        = string
#  default     = ""
#}


#variable "loganalytics_workspace_id" {
#  description = "loganalytics workspace ID"
#  type        = string
#  default     = ""
#}



