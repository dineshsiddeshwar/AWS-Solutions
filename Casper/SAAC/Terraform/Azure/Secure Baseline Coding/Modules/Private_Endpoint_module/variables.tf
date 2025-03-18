variable "resource_group_name" {
  description = "The resource group in which the Private endpoint should reside"
  type        = string
  default = ""
}

variable "name" {
  description = "The name for the private endpoint."
  type        = string
}

variable "subnet_id" {
  description = "The subnet id that should be associated with the private endpoint."
  type        = string
  default     = "/subscriptions/2deda99b-1d35-4ee1-a4ce-aa5a3875266a/resourceGroups/EYGDSSECbaseline-rg/providers/Microsoft.Network/virtualNetworks/baseline-vnet/subnets/subnet3"
}

variable "resource_id" {
  description = "The ID of the Private Link Enabled Remote Resource which this Private Endpoint should be connected to."
  type        = string
}

variable "is_manual_connection" {
  description = "Does the Private Endpoint require Manual Approval from the remote resource owner?"
  type        = bool
  default     = false
}

variable "private_dns_zone_name" {
  description = "For Azure services, use the recommended zone names as described in the link https://docs.microsoft.com/en-us/azure/private-link/private-endpoint-dns#azure-services-dns-zone-configuration."
  type        = string
}

variable "ttl" {
  description = "The Time To Live (TTL) of the DNS record in seconds."
  type        = number
  default     = 300
}

variable "vnet_id" {
  description = "The Virtual network ID to which private DNS zone will be linked to"
  type        = string
  default = null
}

variable "tags" {
  type        = map(string)
  description = "The standard tags to be assocaited with the resources."
  default     = {}
}

variable "soa_record" {
  type = object({
    email        = string,
    expire_time  = number,
    minimum_ttl  = number,
    refresh_time = number,
    retry_time   = number,
    ttl          = number,
  })
  description = "(optional) describe your variable"
  default     = null
}

variable "subresource_names" {
  type = list(string)
  description = "(optional) describe your variable"
}

variable "create_private_dns_zone" {
  description = "The boolean value to decide whether or not to create a private dns zone resource"
  type = bool
  default = true
}
