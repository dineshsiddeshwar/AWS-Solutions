variable "subnet_ids" {
  description = "Subnet IDs for the NLB"
  type        = list(string)
}

variable "security_groups" {
  description = "List of Security Group IDs"
  type        = list(string)
}

variable "tags" {
  description = "Tags to apply to the Network Load Balancer"
  type        = map(string)
}

variable "target_group_arn" {
  description = "ARN of the Target Group"
  type        = string
}


