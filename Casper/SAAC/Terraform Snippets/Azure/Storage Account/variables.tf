######################################################################################################################################################################
############################################################       Define required variables   #######################################################################
######################################################################################################################################################################

variable "resource_prefix" {
    description = "Prefix to use for resources created by stack"
    type        = string
}

variable "subnet_id" {
    description = "The subnet to deploy private endpoint to"
    type        = string
}

variable "resource_group_name" {
    description = "Existing resource group to deploy the storage account to"
    type        = string
}

variable "resource_group_location" {
    description = "Existing resource group location to deploy the storage account to"
    type        = string
}

variable "eventhub_authorization_rule_id" {
    description = "EventHUb authorization rule id for logs"
    type        = string
}

variable "keyvault_id" {
    description = "Existing KeyVault to be used for encryption"
    type        = string
}
variable "keyvault_key_name" {
    description = "Existing keyvault key to use for encryption"
    type        = string
}

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

