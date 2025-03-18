variable "location" {
  type    = string
  default = "eastus"
}

variable "prefix" {
  type    = string
  default = "EYGDSSEC"
}

variable "subnet_names" {
  type    = list(string)
  default = ["subnet1", "subnet2", "subnet3", "app_gateway"]
}

variable "subnet_prefixes" {
  description = "The address prefix to use for the subnet."
  type        = list(string)
  default     = [ "172.19.1.0/24", "172.19.2.0/24", "172.19.3.0/24", "172.19.6.0/24" ]
}

variable "gateway_subnet_address_prefix" {
  description = "The address prefix to use for the gateway subnet"
  default     = ["172.19.4.0/24"]
}

variable "firewall_subnet_address_prefix" {
  description = "The address prefix to use for the Firewall subnet"
  default     = ["172.19.5.0/24"]
}
