variable "tags" {
  description = "Standard tags to be attached to the repo"
  default = {
    Department  = "EYGDSSEC"
    Environment = "Dev"
  }
}

variable "vault_name" {
  description = "The name of the vault. It will be sufixed by a ramdom number by the module."
  type        = string
  default     = "baselinevault"
}

# variable "location" {
#   description = "The location of the vault"
#   type        = string
# }

# variable "resource_group_name" {
#   description = "The resource group to which the vault must belong to"
#   type        = string
# }

variable "enabled_for_disk_encryption" {
  description = "(Optional) Boolean flag to specify whether Azure Disk Encryption is permitted to retrieve secrets from the vault and unwrap keys."
  type        = bool
  default     = true
}

variable "soft_delete_retention_days" {
  description = "The number of days that items should be retained for once soft-deleted. This value can be between 7 and 90"
  type        = number
  default     = 7
}

variable "purge_protection_enabled" {
  description = "Boolean value of whether purge protection is enabled (Recommended)"
  type        = bool
  default     = true
}

variable "sku_name" {
  description = "The sku_name for the vault. Accepted values are 'standard' and 'premium'"
  type        = string
  default     = "standard"
}

variable "enabled_for_deployment" {
  description = "(Optional) Boolean flag to specify whether Azure Virtual Machines are permitted to retrieve certificates stored as secrets from the key vault."
  type        = bool
  default     = true
}

variable "enabled_for_template_deployment" {
  description = "(Optional) Boolean flag to specify whether Azure Resource Manager is permitted to retrieve secrets from the key vault."
  type        = bool
  default     = true
}

variable "enable_rbac_authorization" {
  description = "(Optional) Boolean flag to specify whether Azure Key Vault uses Role Based Access Control (RBAC) for authorization of data actions."
  type        = bool
  default     = true
}

variable "contact" {
  default = {}
}
