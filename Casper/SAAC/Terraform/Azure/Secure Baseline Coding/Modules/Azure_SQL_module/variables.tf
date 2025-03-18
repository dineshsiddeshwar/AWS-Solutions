variable "create_resource_group" {
  description = "Whether to create resource group and use it for all networking resources"
  default     = "false"
}

variable "resource_group_name" {
  description = "A container that holds related resources for an Azure solution"
}

variable "location" {
  description = "The location/region to keep all your network resources. To get the list of all locations with table format from azure cli, run 'az account list-locations -o table'"
  default = ""
}


variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = { enviornment = "dev", owner = "Santosh" }
}

variable "enable_auditing_policy" {
  description = "Audit policy for SQL server and database"
  default     = false

}

variable "enable_threat_detection_policy" {
  description = "Threat Detection policy "
  default     = false
}

variable "log_retention_days" {
  description = "The number of days to retain the log"
  type        = number
  default     = 10
}

################
# Storage account variables
###############
variable "storage_account_name" {
  description = "Name for the Storage Account"
  default     = ""
}

variable "account_kind" {
  description = "Defines the Kind of account. Valid options are BlobStorage, BlockBlobStorage, FileStorage, Storage and StorageV2"
  default     = "StorageV2"
}

variable "account_tier" {
  description = "Defines the Tier to use for this storage account. Valid options are Standard and Premium. For BlockBlobStorage and FileStorage accounts only Premium is valid. "
  default     = "Standard"
}

variable "account_replication_type" {
  description = "Defines the type of replication to use for this storage account. Valid options are LRS, GRS, RAGRS, ZRS, GZRS and RAGZRS"
  default     = "LRS"
}

############
# SQL Server
############

variable "sqlserver_name" {
  description = "SQL server Name"
  type        = string
}

variable "sql_server_version" {
  description = "The version for the new server. Valid values are: 2.0 (for v11 server) and 12.0 (for v12 server)"
  type        = string
  default     = "12.0"
}

variable "admin_login" {
  description = "The administrator login name for the new server."
  type        = string
}

variable "admin_password" {
  description = "The password associated with the administrator_login user. Needs to comply with Azure's Password Policy"
  type        = string
}

variable "enable_failover_group" {
  description = "value"
  default     = false
}

variable "secondary_sql_server_location" {
  description = "Specifies the supported Azure location to create secondary sql server resource"
  default     = "westus"
}

##########
# Database
##########

variable "database_name" {
  description = "The name of the database"
  default     = ""
}

variable "failover_group_name" {
  description = "Name for the Storage Account"
  default     = "sqldb-failover-group"
}

variable "sql_database_edition" {
  description = " The edition of the database to be created. Valid values are: Basic, Standard, Premium, DataWarehouse, Business, BusinessCritical, Free, GeneralPurpose, Hyperscale, Premium, PremiumRS, Standard, Stretch, System, System2, or Web"
  type        = string
  default     = "Standard"
}

variable "sqldb_service_objective_name" {
  description = " A GUID/UUID corresponding to a configured Service Level Objective for the Azure SQL database which can be used to configure a performance level."
  type        = string
  default     = ""
}

variable "email_addresses_for_alerts" {
  description = "A list of email addresses which alerts should be sent to"
  default     = []

}

variable "firewall_rules" {
  description = "Range of IP addresses to allow firewall connections."
  type = list(object({
    name             = string
    start_ip_address = string
    end_ip_address   = string
  }))
  default = []
}

variable "start_ip_address" {
  default = ""
}

variable "end_ip_address" {
  default = ""
}

variable "enable_firewall_rules" {
  description = "Boolean value that will enable or disable creation of the firewall rules"
  type        = bool
  default     = false
}

# variable "virtual_network_name" {
#   default = ""
# }

# variable "enable_private_endpoint" {
#   default=false
# }

# variable "private_subnet_address_prefix" {

# }
