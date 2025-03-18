variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "desired_capacity" {
  description = "Desired number of instances in Auto Scaling Group"
  type        = number
  default     = 4
}

variable "min_size" {
  description = "Minimum number of instances in Auto Scaling Group"
  type        = number
  default     = 2
}

variable "max_size" {
  description = "Maximum number of instances in Auto Scaling Group"
  type        = number
  default     = 6
}

variable "subnet_ids" {
  description = "List of existing subnet IDs"
  type        = list(string)
}

variable "tag_key" {
  description = "Tag Key for Auto Scaling Group"
  type        = string
}

variable "tag_value" {
  description = "Tag Value for Auto Scaling Group"
  type        = string
}

variable "managed_policy_arns" {
  description = "Existing Managed Policy Arns attached with the role"
  type        = list(string)
}

variable "tags" {
  description = "Tags to apply to - IAM role, Instance Template, Network Load Balancer, Security Groups, Target Group, VPC Endpoints"
  type        = map(string)
  default     = {
    environment = "stageauthsso"
  }
}

variable "ami_id" {
  description = "AMI ID for the instance"
  type        = string
}

variable "admin_instance_type" {
  description = "Admin instance type"
  type        = string
  default     = "t2.micro"
}

variable "subnet_id" {
  description = "Subnet ID where the instance will be deployed"
  type        = string
}

variable "engine_node_instance_type" {
  description = "Engine Node instance type"
  type        = string
  default     = "t2.micro"
}

variable "volume_size" {
  description = "Size of the EBS root volume for EC2 instances"
  type        = string
  default     = 15
}

variable "volume_type" {
  description = "Type of the EBS root volume for EC2 instances"
  type        = string
  default     = "gp3"
}

variable "kms_key_arn" {
  description = "KMS Key Arn to encrypt the Root Volume attached with instance"
  type        = string
}

variable "instance_tags" {
  description = "Tags to apply to the EC2 instance"
  type        = map(string)
  default     = {
    uai       = "UAI3046825"
  }
}

variable "volume_tags" {
  description = "Tags to apply to the attached volumes"
  type        = map(string)
  default     = {
    uai       = "UAI3046825"
  }
}

variable "vpc_id" {
  description = "Existing VPC ID"
  type        = string
}