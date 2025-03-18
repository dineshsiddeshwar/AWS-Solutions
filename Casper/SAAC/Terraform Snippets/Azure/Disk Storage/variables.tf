######################################################################################################################################################################
############################################################       Define required variables   #######################################################################
######################################################################################################################################################################
variable "resource_group" {
  type = map
  }

# Ensure that Managed disks can be accessed only through Private link for disk export
variable "managed_disk_name" {
  type = string
}

variable "private_endpoint_name" {
  type = string
}

variable "vnet_info" {
  type = map
}

data "azurerm_managed_disk" "sample" { # Reading the properties of existing Azure resource but NOT needing to modify it through Terraform ! 
  name                = var.managed_disk_name
  resource_group_name = var.resource_group.name
}

data "azurerm_subnet" "example" { # Reading the properties of existing Azure resource but NOT needing to modify it through Terraform ! 
  name                 = var.vnet_info.subnetName
  virtual_network_name = var.vnet_info.name
  resource_group_name  = var.resource_group.name
}

variable "disk_access_resource" {
  type = string
}

variable "private_connection" {
  type = string
}

# Ensure that least privilege access method is implemented using Role-based access control (RBAC)
variable "rbac_role_assignment" {
  type = map
 }

# Ensure managed disk is Encrypted with Customer Managed Keys
variable "key_vault_key" {
  type = map
 }

variable "key_encryption_set" {
  type = string
}

variable "role_name" {
  type = string
}

#variable "disk_encryption_set_objectId" {
 # type = string
#}

variable "disk_encryption_set_id" {
  type = string
}

# Ensure that Managed disk uses standard organizational Resource tagging method
variable "cost_center" {}
variable "ppmc_id" {}
variable "toc" {}
variable "usage_id" {}
variable "env_type" {}
variable "exp_date" {
  default = "01/01/9999"
}
variable "endpoint" {}
variable "sd_period" {}
