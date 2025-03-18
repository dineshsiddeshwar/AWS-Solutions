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

variable "Infoblox1" {
    description = "Infoblox IP 1"
    type = string
    default = ""
  
}

variable "Infoblox2" {
    description = "Infoblox IP 2"
    type = string
    default = ""
  
}

variable "vpc_id" {
  description = "ID of the VPC where to create security group"
  type        = string
  default     = null
}

variable "ou_principals" {
  type=map(string)
}

variable "region" {
    type = string
  
}

variable "endpoint_ips_subnet1a" {
  type = list(string)
  
}

variable "endpoint_ips_subnet1b" {
  type = list(string)
  
}