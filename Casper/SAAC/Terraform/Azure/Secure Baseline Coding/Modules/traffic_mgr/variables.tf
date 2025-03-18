variable "resource_group_name" {
  description = "The resource group in which the Endpoint and Traffic manager should reside"
  type        = string
  default = "EYGDSSECbaseline-rg"
}

variable "traffic_routing" {
  description = "The algorithm for routing method to be adopted by Traffic manager"
  type        = string
  default= "Performance"
}


variable "tags" {
  description = "Base tags for the resource to be inherited from the resource group."
  type        = map(any)
  default = {
    Department  = "EYGDSSEC"
    Environment = "Dev"
  }
}


variable "protocol" {
  description = "Web protocol to be used for monitoring"
  type        = string
  default = "HTTPS"
}

variable "profilename" {
  description = "Profile name for traffic manager"
  type        = string
  default= "test-tmprofile"
}

variable "dnsrelativename" {
  description = "Relative DNS name for traffic manager"
  type        = string
  default = "test-tmprofile"
}

variable "port" {
  description = "Web protocol to be used"
  type        = number
  default = 443
}

variable "path" {
  description = "Path on webserver"
  type        = string
  default = ""
}


variable "interval" {
  description = "Monitoring Interval in seconds"
  type        = number
  default = 30
}


variable "timeout" {
  description = "Timeout in seconds for monitoring"
  type        = number
  default = 10
}

variable "failures" {
  description = "Number of failed attempts while monitoring"
  type        = number
  default = 3
}


variable "endpointname" {
  description = "Possible values for Endpoint Name for Traffic manager - AzureEndpoints, NestedEndpoints."
  type        = string
  default = "test-endpoint"
}

# variable "targeturl" {
#   description = "Target URL for traffic manager"
#   type        = string
#   default = ""
# }

variable "target_resource_id" {
  description = "The resource id of an Azure resource to target. This argument must be provided for an endpoint of type azureEndpoints or nestedEndpoints."
  type        = string
  default = "/subscriptions/2deda99b-1d35-4ee1-a4ce-aa5a3875266a/resourcegroups/EYGDSSECbaseline-rg/providers/Microsoft.Web/sites/test-webapp2604"
  
}


variable "endpointtype" {
  description = "Type of endpoint - External/ Internal"
  type        = string
  default = "azureEndpoints"
}

variable "create_resource_group" {
  description = "Whether to create resource group and use it for all networking resources"
  default     = false
}

variable "location" {
  description = "The location/region to keep all your network resources. To get the list of all locations with table format from azure cli, run 'az account list-locations -o table'"
  default     = "useast"
}