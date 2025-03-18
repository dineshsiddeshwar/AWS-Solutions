variable "vpc_deployment_region" {
    type = string
    default = "us-west-1"
}

variable "vpc_security_group_values" {
    type = list(object({
      from_port = number
      to_port = number
      protocol = string
      cidr_block = list(string)
    }))
    description = "Security groups for the application load balancer"
    default = [
        {
      from_port = 3306
      to_port = 3306
      protocol = "tcp"
      cidr_block = [ "10.0.0.0/16" ]
        },
        {
      from_port = 3306
      to_port = 3306
      protocol = "tcp"
      cidr_block = [ "10.0.0.0/16" ]
        }
    ]
}

variable "network_address_type" {
    type = string
    default = "ipv4"
}