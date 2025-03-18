variable "create" {
  description = "Determines whether resources will be created"
  type        = bool
  default     = true
}

variable "vpc_id" {
  description = "The ID of the VPC in which the endpoint will be used"
  type        = string
  default     = null
}

variable "endpoints" {
  type = map(object({
    service_type       = optional(string)
    service_name_suffix       = string
    hostedzone_suffix = optional(string)
    security_group_ids = optional(list(string))
    subnet_ids         = optional(list(string))
    route_table_ids    = optional(list(string))
    policy             = optional(string)
    private_dns_enabled = optional(bool)
    tags               = optional(map(string))
  }))
  default = {
    "endpoint1" = {
      service_type       = "Interface"
      service_name_suffix       = "defaultvalue"
      hostedzone_suffix = "default"
      security_group_ids = []
      subnet_ids         = []
      route_table_ids    = []
      policy             = ""
      private_dns_enabled = false
    }
  }
}

variable "endpoint_extended" {
  type = map(object({
    service_type       = optional(string)
    service_name_suffix       = string
    hostedzone_suffix = optional(string)
    security_group_ids = optional(list(string))
    subnet_ids         = optional(list(string))
    route_table_ids    = optional(list(string))
    policy             = optional(string)
    private_dns_enabled = optional(bool)
    tags               = optional(map(string))
  }))
  default = {
    "endpoint1" = {
      service_type       = "Interface"
      service_name_suffix       = "defaultvalue"
      hostedzone_suffix = "default"
      security_group_ids = []
      subnet_ids         = []
      route_table_ids    = []
      policy             = ""
      private_dns_enabled = false
    }
  }
}

variable "security_group_ids" {
  description = "Default security group IDs to associate with the VPC endpoints"
  type        = list(string)
  default     = []
}

variable "sharedsubnet1a" {
  description = "subnets IDs in AZ 1A to associate with the VPC endpoints"
  type        = list(string)
  default     = []
}

variable "sharedsubnet1b" {
  description = "Subnet IDs in AZ 1B to associate with the VPC endpoints"
  type        = list(string)
  default     = []
}

variable "sharedsubnet2a" {
  description = "subnets IDs in AZ 2A to associate with the VPC endpoints"
  type        = list(string)
  default     = []
}

variable "sharedsubnet2b" {
  description = "Subnet IDs in AZ 2B to associate with the VPC endpoints"
  type        = list(string)
  default     = []
}


variable "tags" {
  description = "A map of tags to use on all resources"
  type        = map(string)
  default     = {}
}

variable "timeouts" {
  description = "Define maximum timeout for creating, updating, and deleting VPC endpoint resources"
  type        = map(string)
  default     = {}
}

variable "isproduction" {
  description = "Describes if the env is Prod"
  type = bool
  default = false
}

variable "env_type" {
  description = "describes the environment type"
  type = string
  default = "dev"
}

variable "region" {

  description = "describes the region in which the vpc endpoint should be deployed"
  type = string
  default = "us-east-1"
}