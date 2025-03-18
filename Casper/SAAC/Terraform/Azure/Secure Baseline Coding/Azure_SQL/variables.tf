variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(any)
  default = {
    Department  = "EYGDSSEC"
    Environment = "Dev"
  }
}

# variable "enable_auditing_policy" {
#   description = "Audit policy for SQL server and database"
#   default     = "false"
# }

# variable "enable_threat_detection_policy" {
#   description = "Threat Detection policy "
#   default     = "false"
# }

variable "storage_account_name" {
  description = "Name for the Storage Account"
  default     = "dbstoragetest1"
}

# variable "account_kind" {
#   default = "StorageV2"
# }

# variable "account_tier" {
#   default = "Standard"
# }

# variable "account_replication_type" {
#   default = "GRS"
# }

variable "sqlserver_name" {
  description = "SQL server Name"
  default     = "baseline-azuresql"

}

# variable "sql_server_version" {
#   default = "12.0"
# }

# variable "enable_failover_group" {
#   default = false
# }

variable "secondary_sql_server_location" {
  description = "Specifies the supported Azure location to create secondary sql server resource"
  default     = "westus"
}

variable "database_name" {
  default = "eygdssec-sqldb-test"
}

variable "sql_database_edition" {
  default = "Standard"
}

# # variable "email_addresses_for_alerts" {
# #     # default = "Sai.Santosh.Pavan.Lanka@gds.ey.com", "Sai.Santosh.Pavan.Lanka@gds.ey.com"

# # }

variable "firewall_rules" {
  description = "Range of IP addresses to allow firewall connections."
  type = list(object({
    name             = string
    start_ip_address = string
    end_ip_address   = string
  }))
  default = [{
    name             = "Allow access to Azure services"
    start_ip_address = "0.0.0.0"
    end_ip_address   = "0.0.0.0"
  }]
}

# variable "start_ip_address" {
#     default = "0.0.0.0"

# }

# variable "end_ip_address" {
#   default = "0.0.0.0"
# }

variable "enable_firewall_rules" {
  default = false
}

# variable "failover_group_name" {

# }

# variable "enable_private_endpoint" {
#   default = false
# }

# variable "private_subnet_address_prefix" {

# }
