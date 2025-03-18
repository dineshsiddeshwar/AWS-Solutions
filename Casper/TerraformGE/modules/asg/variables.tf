variable "desired_capacity" {
  description = "Desired number of instances"
  type        = number
}

variable "min_size" {
  description = "Minimum number of instances"
  type        = number
}

variable "max_size" {
  description = "Maximum number of instances"
  type        = number
}

variable "instance_template" {
  description = "Launch Template ID for instances"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for the Auto Scaling Group"
  type        = list(string)
}

variable "target_group_arn" {
  description = "Target Group ARN"
  type        = string
}

variable "tag_key" {
  description = "Tag Key for Auto Scaling Group"
  type        = string
}

variable "tag_value" {
  description = "Tag Value for Auto Scaling Group"
  type        = string
}