variable "vault_name" {
  description = "The name of the vault. It will be sufixed by a ramdom number by the module."
  type = string
}

variable "resource_group_name" {
  description = "The resource group to which the vault must belong to"
  type = string
}

variable "enabled_for_disk_encryption" {
  description = "(Optional) Boolean flag to specify whether Azure Disk Encryption is permitted to retrieve secrets from the vault and unwrap keys."
  type = bool
  default = true
}

# variable "tenant_id" {
#   description = "The tenant id for the vault to be provisioned in"
#   type = string
# }

variable "soft_delete_retention_days" {
  description = "The number of days that items should be retained for once soft-deleted. This value can be between 7 and 90"
  type = number
  default = 7
}

variable "purge_protection_enabled" {
  description = "Boolean value of whether purge protection is enabled (Recommended)"
  type = bool
  default = true
}

variable "sku_name" {
  description = "The sku_name for the vault. Accepted values are 'standard' and 'premium'"
  type = string
  default = "standard"
}

variable "enabled_for_deployment" {
  description = "(Optional) Boolean flag to specify whether Azure Virtual Machines are permitted to retrieve certificates stored as secrets from the key vault."
  type = bool
  default = true
}

variable "enabled_for_template_deployment" {
  description = "(Optional) Boolean flag to specify whether Azure Resource Manager is permitted to retrieve secrets from the key vault."
  type = bool
  default = true
}

variable "enable_rbac_authorization" {
  description = "(Optional) Boolean flag to specify whether Azure Key Vault uses Role Based Access Control (RBAC) for authorization of data actions."
  type = bool
  default = true
}

variable "contact" {
  default = {}
}

variable "tags" {
  description = "The tags that are to be attached to the vault"
  default = {}
}

variable "access_policy" {
  description = " A list of up to 16 objects describing access policies "
  default = {}
}

variable "network_acls" {
  description = "Object with attributes: `bypass`, `default_action`, `ip_rules`, `virtual_network_subnet_ids`. See https://www.terraform.io/docs/providers/azurerm/r/key_vault.html#bypass for more informations."
  default     = null

  type = object({
    bypass                     = string,
    default_action             = string,
    ip_rules                   = list(string),
    virtual_network_subnet_ids = list(string),
  })
}

variable "admin_objects_ids" {
  description = "Ids of the objects that can do all operations on all keys, secrets and certificates"
  type        = list(string)
  default     = []
}

variable "reader_objects_ids" {
  description = "Ids of the objects that can read all keys, secrets and certificates"
  type        = list(string)
  default     = []
}

variable "tenant_id" {
  description = "The Azure Active Directory tenant ID that should be used for authenticating requests to the Key Vault. Default is the current one."
  type        = string
  default     = ""
}

