variable "create_resource_group" {
  description = "Whether to create resource group and use it for all networking resources"
  default     = false
}

variable "resource_group_name" {
  description = "Name of the resource group to be imported."
  type        = string
}

variable "location" {
  description = "The location/region to keep all your network resources. To get the list of all locations with table format from azure cli, run 'az account list-locations -o table'"
  default     = "useast"
}

variable "enable_https_traffic_only" {
  description = "Boolean flag which forces HTTPS if enabled, see here for more information. Defaults to true."
  type        = bool
  default     = true
}

variable "allow_blob_public_access" {
  description = "Allow or disallow public access to all blobs or containers in the storage account. Defaults to false."
  type        = bool
  default     = false
}

variable "tags" {
  description = "value"
  type        = map(any)
  default = {
    Department  = "EYGDSSEC"
    Environment = "Dev"
  }
}

variable "datalake_name" {
  description = " The name of the Data Lake Gen2 File System which should be created within the Storage Account. Must be unique within the storage account the queue is located. Changing this forces a new resource to be created."
  type        = string
  default     = "storage-datalake"
}

variable "synapse_name" {

  description = "Specifies the name which should be used for this synapse Workspace. Changing this forces a new resource to be created."
  type        = string
  default     = "baseline-synapse"
}

variable "adminlogin" {
  description = "Specifies The Login Name of the SQL administrator. Changing this forces a new resource to be created."
  type        = string
  default     = "testadminuser"
}

variable "adminpassword" {
  description = "The Password associated with the sql_administrator_login for the SQL administrator."
  type        = string
  default     = "Admin@12345"
}

variable "managed_virtual_network_enabled" {
  description = "Is Virtual Network enabled for all computes in this workspace? Defaults to false."
  type = bool
  default = false
}

variable "sql_identity_control_enabled" {
  description = "Are pipelines (running as workspace's system assigned identity) allowed to access SQL pools? Defaults to false."
  type = bool
  default = false
}

variable "managed_resource_group_name" {
  description = "value"
  type = string
  default = ""
}

variable "aad_admin" {
  description = "AzureAD Admin block"
  type = map(string)
  default = null
}

variable "azure_devops_repo" {
  description = "azure_devops_repo configuration block."
  type = map(string)
  default = null
}

variable "github_repo" {
  description = "github_repo configuration block"
  type = map(string)
  default = null
}

variable "synapsesql" {
  description = "The name which should be used for this Synapse Sql Pool. Changing this forces a new synapse SqlPool to be created."
  type        = string
  default     = "synapsesqlpool"
}

# variable "sku_name" {
#   description = "Specifies the SKU Name for this Synapse Sql Pool. Possible values are DW100c, DW200c, DW300c, DW400c, DW500c, DW1000c, DW1500c, DW2000c, DW2500c, DW3000c, DW5000c, DW6000c, DW7500c, DW10000c, DW15000c or DW30000c."
#   type        = string
#   default     = "DW100c"
# }

# variable "create_mode" {
#   description = "pecifies how to create the Sql Pool. Valid values are: Default, Recovery or PointInTimeRestore. Must be Default to create a new database. Defaults to Default."
#   type        = string
#   default     = "Default"

# }

# variable "data_encrypted" {
#   description = "Is transparent data encryption enabled? Defaults to false."
#   type        = bool
#   default     = false
# }

variable "firewallrule" {
  description = "The Name of the firewall rule. Changing this forces a new resource to be created."
  type        = string
  default     = "AllowAzureServices"
}

variable "start_ip_address" {
  description = "The starting IP address to allow through the firewall for this rule."
  type        = string
  default     = "0.0.0.0"
}

variable "end_ip_address" {
  description = "The ending IP address to allow through the firewall for this rule."
  type        = string
  default     = "0.0.0.0"
}

variable "storage_account_name" {
  description = "Specifies the name which should be used for creating new storage account to be used as target resource for managed private endpoint."
  type        = string
  default     = ""
}

variable "account_tier" {
  description = "Defines the Tier to use for this storage account. Valid options are Standard and Premium. For BlockBlobStorage and FileStorage accounts only Premium is valid. Changing this forces a new resource to be created."
  type        = string
  default     = "Standard"
}

variable "account_replication_type" {
  description = "Defines the type of replication to use for this storage account. Valid options are LRS, GRS, RAGRS, ZRS, GZRS and RAGZRS."
  type        = string
  default     = "LRS"
}

variable "account_kind" {
  description = "Account_kind"
  type        = string
  default     = "StorageV2"
}

variable "endpoint_name" {
  description = "Specifies the name which should be used for this Managed Private Endpoint. Changing this forces a new resource to be created."
  type        = string
  default     = "test-endpoint"
}

variable "subresource_name" {
  description = "Specifies the sub resource name which the Synapse Private Endpoint is able to connect to. Changing this forces a new resource to be created."
  type        = string
  default     = "blob"
}

variable "synapse_role" {
  description = " The Role Name of the Synapse Built-In Role. Changing this forces a new resource to be created. Currently, the Synapse built-in roles are Workspace Admin, Apache Spark Admin and Sql Admin."
  type        = string
  default     = "Sql Admin"

}

variable "create_sto_acc" {
  description = "value"
  type        = bool
  default     = true

}

variable "storage_acc_id" {
  description = "Account ID for storage account to be created for private endpoint."
  type        = string
  default     = "/subscriptions/2deda99b-1d35-4ee1-a4ce-aa5a3875266a/resourceGroups/EYGDSSECbaseline-rg/providers/Microsoft.Storage/storageAccounts/eygdsbaseline"
}

variable "principal_id" {
  description = "The ID of the Principal (User, Group or Service Principal) to assign the Synapse Role Definition to. Changing this forces a new resource to be created."
  type        = string
  default     = ""
}

variable "synapse_sql_pool" {
  description = "describe your variable"
  default     = {}
    # Example
    # sql_pool_1 = {
    #   sku_name = "DW100c"
    #   create_mode = "PointInTimeRestore"
    #   data_encrypted = true
    #   restore = [{
    #     source_database_id = "string-value"
    #     point_in_time = "value"
    #   }]
    # }
}

variable "synapse_spark_pool" {
  description = "describe your variable"
  default     = {}
    # Example
  #   default     = {
  #     sparkpool1 = {
  #     node_size_family = "MemoryOptimized"
  #     node_size = "Small"

  #     auto_scale = [{
  #       max_node_count = 5
  #       min_node_count = 3
  #     }]

  #     auto_pause = [{
  #       delay_in_minutes = 5
  #     }]
  #   }
  # }
}

