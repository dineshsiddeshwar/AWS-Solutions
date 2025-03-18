variable vpc_cidr_details {
    type = map(object({
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
}

variable "env_type" {
  type = string
  description = "environment type (dev/acceptance/prod)"
  
}

variable "isproduction" {
  description = "Describes if the env is Prod"
  type = bool
  default = false
}