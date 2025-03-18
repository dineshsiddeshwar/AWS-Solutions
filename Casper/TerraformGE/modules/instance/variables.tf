variable "ami_id" {
  description = "AMI ID for the instance"
  type        = string
}

variable "admin_instance_type" {
  description = "Admin instance type"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID where the instance will be deployed"
  type        = string
}

variable "instance_template" {
  description = "Launch Template ID for instance"
  type        = string
}