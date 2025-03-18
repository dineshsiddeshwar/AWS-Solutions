variable "aws_region" {
  description = ""
  type        = string
}
variable "aws_ec2_account_id" {
  description = ""
  type        = string
  sensitive   = true
}
# EC2 Instances that will be created in VPC Private Subnets
variable "ec2_vpc_id" {
  description = ""
  type        = string
  sensitive   = true
}
data "aws_vpc" "ec2_vpc" {
  id = var.ec2_vpc_id
}

# VPC Endpoints
data "aws_vpc_endpoint" "ec2_vpc_endpoint_id" {
  vpc_id       = data.aws_vpc.ec2_vpc.id
  service_name = var.ec2_service_name
}

variable "ec2_service_name" {
  description = ""
  type        = string
  sensitive   = true
}
variable "ec2_vpc_endpoint_type" {
  description = ""
  type        = string
  sensitive   = true
}
variable "ec2_vpc_sgs" {
  description = ""
  type        = set(string)
  sensitive   = true
}
variable "ec2_vpc_endpoint_tag" {
  description = ""
  type        = map(string)
  sensitive   = true
}

## Variables
variable "ami_owners" {
  description = ""
  type        = list(string)
  sensitive   = true
}
variable "approved_amis_filter_name" {
  description = ""
  type        = list(string)
}
variable "approved_amis_filter_root_device_type" {
  description = ""
  type        = list(string)
}
variable "approved_amis_filter_virtualization_type" {
  description = ""
  type        = list(string)
}
variable "approved_amis_filter_architecture" {
  description = ""
  type        = list(string)
}
variable "ec2_availability_zone" {
  description = ""
  type        = string
}
variable "ebs_volume_size" {
  description = ""
  type        = number
}
variable "aws_ec2_instance_profile_reader_profile_name" {
  description = ""
  type        = string
}
variable "aws_ec2_instance_type" {
  description = ""
  type        = string
}
variable "aws_ec2_instance_keypair" {
  description = ""
  type        = string
  sensitive   = true
}
variable "aws_ec2_vpc_private_subnet_id" {
  description = ""
  type        = string
  sensitive   = true
}
variable "aws_ec2_vpc_private_sgs" {
  description = ""
  type        = set(string)
  sensitive   = true
}
variable "ebs_device_name" {
  description = ""
  type        = string
}

variable "ec2_key_arn" {
  description = ""
  type        = string
}
variable "ec2_subnet_id" {
  description = ""
  type        = string
}
## Data

# AWS EC2 permissions for ec2 reader role policy
data "template_file" "EC2LeastPrivilegeAccessPolicy" {
  template = file("policies/EC2LeastPrivilegeAccessPolicy.json")
  vars = {
    ec2_region     = var.aws_region
    ec2_account_id = var.aws_ec2_account_id
    ec2_subnet_id  = var.aws_ec2_vpc_private_subnet_id
  }
}

variable "common_tags" {
  description = "Tags for all EC2 resources"
  type        = map(string)
}

# data source to get the default EBS encryption KMS key in the current region.
data "aws_ebs_default_kms_key" "current" {}
