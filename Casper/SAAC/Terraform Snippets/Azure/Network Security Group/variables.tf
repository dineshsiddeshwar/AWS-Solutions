######################################################################################################################################################################
############################################################       Define required variables   #######################################################################
######################################################################################################################################################################

variable "resource_group_name" {
  type = string
}

variable "resource_group_location" {
  type = string
}

variable "subnet_id" {
  type = string
}

variable "network_security_group_name1" {
  type = string
}

variable "application_security_group_name" {
  type = string
}

variable "network_interface_id" {
  type = string
}

variable "storage_account_id" {
  type = string
}

variable "vnet-diagsetting_name" {
  type = string
}

variable "log_dump_resource_id" {
  type = string
}

variable "workspace_id" {
  type = string
}

variable "workspace_region" {
  type = string
}

variable "workspace_resource_id" {
  type = string
}

variable "rbac_principal_id" {
  type = string
}

variable "role_definition_id" {
  type = string
}

variable "vnet_log_category" {
  type = string
}

variable "vnet_log_category1" {
  type = string
}

variable "log_retention_days" {
  type = number
}

variable "listen" {
  type = string
}

variable "send" {
  type = string
}

variable "manage" {
  type = string
}

variable "network_watcher_name" {
  type = string
}

variable "eventhub_namespace_authorization_rule_name" {
  type = string
}

variable "network_watcher_flow_log_name" {
  type = string
}

variable "eventhub_namespace_name" {
  type = string
}

variable "sku" {
  type = string
}

variable "capacity" {
  type = string
}

variable "interval_in_minutes" {
  type = number
}

variable "name_asg" {
  type = string
}

variable "priority_asg" {
  type = number
}
variable "direction_asg" {
  type = string
}

variable "access_asg" {
  type = string
}

variable "protocol_asg" {
  type = string
}

variable "source_port_range_asg" {
  type = string
}

variable "destination_port_range_asg" {
  type = string
}

variable "source_address_prefix_asg" {
  type = string
}

variable "nsg_rules" {
  type = list(object({
    name                       = string
    priority                   = number
    direction                  = string
    access                     = string
    protocol                   = string
    source_port_range          = string
    destination_port_range     = string
    source_address_prefix      = string
    destination_address_prefix = string
  }))
  description = "The values for each NSG rule "
}

# Ensure that NSG uses standard organizational Resource tagging method
variable "cost_center" {
}
variable "ppmc_id" {
}
variable "toc" {
}
variable "usage_id" {
}
variable "env_type" {
}
variable "exp_date" {
}
variable "endpoint" {
}
variable "sd_period" {
}

