variable "iam" {

  type = map(string)
  description = "iam module vars"
  
}

variable vpc_all_details {
    type = map (object({
            action_type = map(object({
                cidr = string
                secondary_cidr = optional(string)
                securitygroupname= string
                private = list(string)
                Infoblox1 = optional(string)
                Infoblox2 = optional(string)
                hostedzone_ids = string
                subnets = map (object({
                    AvailabilityZone = string
                    Subnet_cidr=string
                    route53_iplist = optional(list(string))
                    Subnet_name = string
            }))
}))
}))
}



variable "env_type" {

  type = string
  description = "environment type ( prod / dev/ acceptance )"
  
}

variable "rules" {
  description = "Map of known security group rules (define as 'name' = ['from port', 'to port', 'protocol', 'description'])"
  type        = map(list(any))
}

variable "ingress_rules" {
  description = "List of ingress rules to create by name"
  type        = list(string)
  default     = []
}


variable "isproduction" {
  description = "Describes if the env is Prod"
  type = bool
  default = false
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

variable "ou_principals" {
  type = map(string)
  
}

variable env_instanceprofile_suffix {
    type = string
    description = "s3 bucket for cloudhealth"
}