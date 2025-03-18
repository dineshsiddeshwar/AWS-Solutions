######################################################################################################################################################################
############################################################       Define required variables   #######################################################################
######################################################################################################################################################################

# Private_endpoint variables
variable "resource_group" {
  description = "Details for resource group"
  type = map 
}

#Values for role assignment
variable "principal_id"{
  description = "Userid/object id"
  type = string
}
variable "role_definition_name" {
  description = "Role which needs to assigned"
  type = string  
}

variable "private_dns_zone_group_name" {
 type = string 
}

variable "private_endpoint_name" {
  description = "Name of the existing private endpoint"
  type = string
}

variable "private_service_connection_name" {
  description = "Name of the existing private service connection"
  type = string
}

variable "subnet_id" {
  description = "The subnet to deploy private endpoint to"
  type = string
}
variable "pe_private_dns_zone_name" {
  description = "The name of private dns zone"
  type = string
}

variable "resource_id" {
  description = "The resource to which you want to deploy private endpoint to"
  type = string 
}
variable "subresource_names" {
  description = "A list of subresource names which the Private Endpoint is able to connect to. subresource_names corresponds to group_id. Changing this forces a new resource to be created."
  type = list(string)
}

#Tags
variable "sa_tags" {
  description = "Organization specific tags for private endpoint"
  type        = map(string)
}

variable "pe_monitor_action_group_name" {
  description = "Name of the monitor action group"
  type = string
}

variable "pe_monitor_action_group_short_name" {
  type = string 
}
