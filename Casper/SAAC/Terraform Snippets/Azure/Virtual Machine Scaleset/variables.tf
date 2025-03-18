data "azurerm_client_config" "current" {}

data "azurerm_resource_group" "kvrg" {
  name = "kvresourcegroup"
}

data "azurerm_key_vault" "kv" {
  name                = "vmss-kv"
  resource_group_name = data.azurerm_resource_group.kvrg.name
}

data "azurerm_key_vault_secret" "user" {
  name         = "user"
  key_vault_id = data.azurerm_key_vault.kv.id
}

data "azurerm_key_vault_secret" "password" {
  name         = "password"
  key_vault_id = data.azurerm_key_vault.kv.id
}

variable "resource_group" {
  type = map(any)
}

variable "subnet_id" {
  type = string
}

variable "monitor_autoscale_setting_name" {
  type = string
}

variable "vm_scale_set" {
  type = map(any)
}

variable "capacity" {
  type = map(any)
}

variable "metric_trigger" {
  type = map(any)
}

variable "source_image_referenc_details" {
  type = map(any)
}

variable "os_disk_details" {
  type = map(any)
}

variable "profile_name" {
  type = string
}

variable "scale_action" {
  type = map(any)
}

variable "network_interface_name" {
  type = string
}

variable "ip_configuration_name" {
  type = string
}

variable "vss_tags " {
  description = "virtual machine scale set tags"
  type = map(string)
  
}
