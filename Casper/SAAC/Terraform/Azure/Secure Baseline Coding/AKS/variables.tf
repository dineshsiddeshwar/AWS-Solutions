
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

variable "nodes_count" {
  default     = "2"
  description = "No. of nodes count for AKS cluster"
}

variable "vmss_min_count" {
  default     = "2"
  description = "Minimum no. of nodes count for vmss"
}

variable "vmss_max_count" {
  default     = "4"
  description = "Maximum no. of nodes count for vmss"
}

variable "environment" {
  default     = "Development"
  description = "Environment Tag name"
}

variable "authorized_ip_range" {
  default     = [ "172.19.1.0/24", "172.19.2.0/24", "172.19.3.0/24", "172.19.6.0/24" ]
  description = "authorized Ip range"
}
# variable "client_app_id" {
#   description = "The Client app ID of the AKS client application"
# }

# variable "server_app_id" {
#   description = "The Server app ID of  the AKS server application"
# }

# variable "server_app_secret" {
#   description = "The secret created for AKS server application"
# }

# variable "tenant_id" {
#   description = "The Azure AD tenant id "
# }


# variable "app_id" {
#   description = "The app ID of the AKS client application"
# }

# variable "password" {
#   description = "The secret created for AKS server application"
# }