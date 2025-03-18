variable "vpc_id" {
  description = "The ID of the VPC in which the endpoint will be used"
  type        = string
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for the Endpoints"
  type        = list(string)
}

variable "security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface"
  type        = list(string)
}

variable "tags" {
  description = "Tags to apply to all the VPC Endpoints"
  type        = map(string)
}
