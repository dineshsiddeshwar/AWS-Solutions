variable "role_name" {
  description = "Name of the Role attached with the Instance Template"
  type        = string
}

variable "ami_id" {
  description = "AMI ID for the instance template"
  type        = string
}

variable "engine_node_instance_type" {
  description = "Engine Node instance type"
  type        = string
}

variable "security_groups" {
  description = "List of Security Group IDs"
  type        = list(string)
}

variable "subnet_id" {
  description = "Subnet ID where the instance will be deployed"
  type        = string
}

variable "volume_size" {
  description = "Size of the EBS root volume for EC2 instances"
  type        = string
}

variable "volume_type" {
  description = "Type of the EBS root volume for EC2 instances"
  type        = string
}

variable "kms_key_arn" {
  description = "KMS Key Arn to encrypt the Root Volume attached with instance"
  type        = string
}

variable "instance_tags" {
  description = "Tags to apply to the EC2 instance"
  type        = map(string)
}

variable "volume_tags" {
  description = "Tags to apply to the attached volumes"
  type        = map(string)
}

variable "tags" {
  description = "Tags to apply to the Launch Template"
  type        = map(string)
}
