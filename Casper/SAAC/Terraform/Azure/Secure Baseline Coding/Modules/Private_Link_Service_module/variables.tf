variable "create_resource_group" {
  description = "Whether to create resource group and use it for private link service"
  type        = bool
  default     = false
}

variable "resource_group_name" {
  description = "Name of the resource group to be used."
  type        = string
}

variable "location" {
  description = "The location/region to keep your private link resource. To get the list of all locations with table format from azure cli, run 'az account list-locations -o table'"
  type        = string
  default     = "useast"
}

variable "plink_name" {
  description = "Specifies the name of this Private Link Service. Changing this forces a new resource to be created."
  type        = string
}

variable "auto_approval_subscription_ids" {
  description = "A list of Subscription UUID/GUID's that will be automatically be able to use this Private Link Service."
  type        = list(string)
}

variable "visibility_subscription_ids" {
  description = "A list of Subscription UUID/GUID's that will be able to see this Private Link Service."
  type        = list(string)
}

variable "load_balancer_frontend_ip_configuration_ids" {
  description = "vaA list of Frontend IP Configuration ID's from a Standard Load Balancer, where traffic from the Private Link Service should be routedlue"
  type        = list(string)
}

variable "enable_proxy_protocol" {
  description = " Should the Private Link Service support the Proxy Protocol? Defaults to false."
  type        = bool
  default     = false
}

variable "nat_ip_config" {
  description = "One or more (up to 8) nat_ip_configuration block"
  type        = list(any)
  /*
  nat_ip_config = [
    ["primary", "10.5.1.17", azurerm_subnet.example.id, true],
    ["secondary", "10.5.1.18", azurerm_subnet.example.id, false]
  ]
  */
}

variable "tags" {
  description = "A mapping of tags to assign to the resource"
  type        = map(any)
  default = {
    Department  = "EYGDSSEC"
    Environment = "Dev"
  }
}

# variable "operation_name" {
#   description = "Name of the operation need to be monitored to create alerts."
#   type        = string
#   default     = ""

# }
