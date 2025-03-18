# AWS Provider variable
data "aws_caller_identity" "current" {}

variable "aws_region" {
  description = "Aws region where resource needs to be deployed"
  type        = string
}

# Environment Variable
variable "common_tags" {
  type        = map(string)
  description = "Default tags attached to all resources."
}

# VPC Input Variables

data "aws_vpc" "athena_vpc_id" {
  id = var.athena_vpc_id
}

# 1. Ensure Athena utilizes VPC Endpoints far Private Inter-Service Communication
data "aws_vpc_endpoint" "athena_vpc_endpoint" {
  vpc_id       = data.aws_vpc.athena_vpc_id.id
  service_name = var.athena_service_name
}

variable "athena_vpc_id" {
  type        = string
  description = "VPC Id of the deployed VPC, can be found on Confluence page AWS VPC CIDR Deployed (Auto updated)"
}

variable "athena_vpc_sg" {
  type        = string
  description = "AWS Security group ID created for the VPC ID, Refer confluence page AWS Standard Security Group Baseline."
}

variable "athena_service_name" {
  type        = string
  description = "Enter service name for VPC endpoint"
}

variable "athena_vpc_endpoint_type" {
  type        = string
  description = "Enter type of VPC endpoint like Interface , Gateway etc"
}

# Policy : Athena resource policies enforce least privilege 
data "template_file" "athena_least_privilege_access" {
  template = file("policies/AthenaLeastPrivilegeAccessPolicy.json")
  vars = {
    vpc_endpoint_id          = data.aws_vpc_endpoint.athena_vpc_endpoint.id
    athena_principal_arn     = var.athena_principal_arn
    athena_resource_arn      = var.athena_resource_arn
  }
}

variable "athena_principal_arn" {
  description = "prinicipal arn that require access to athena"
  type        = string
}
variable "athena_resource_arn" {
  description = "ARN of resource where user should be granted access"
  type        = string
}

# kms key & alias
data "aws_kms_alias" "athena_cmk_key_alias" {
  name = var.athena_alias_name
}

variable "athena_alias_name" {
  description = "The name of the key alias, example: alias/myalias"
  type        = string
}

# S3 Bucket
variable "athena_bucket" {
  type        = string
  description = "Enter the Name of S3 bucket for storing Athena datbase"
}
variable "athena_user_name" {
  type        = string
  description = "Enter the name of user having least privledge to acees Database"
}
variable "athena_user_policy_name" {
  type        = string
  description = "Enter the name of policy to allow to athena database access"

}
variable "athena_database_name" {
  type        = string
  description = "Enter the name of datbase"
}

variable "athena_bucket_role_arns" {
  type        = string
  description = "Enter the S3 bucket role arns"

}

data "aws_canonical_user_id" "current" {} # Current cannonical user id 

# Athena Workgroup and Named query resource variables

variable "athena_workgroup" {
  type        = string
  description = "Enter the Athena workgroup name"
}
variable "athena_engine_version" {
  type        = string
  description = "Enter the Athena engine vesrion"
}
variable "athena_named_query" {
  type        = string
  description = "Enter the anme for athena named query resource"
}

data "aws_s3_bucket" "athena_bucket" {
  bucket = var.athena_bucket  
}

variable "athena_bucket_out" {
  type = string
  description = "S3 bucket used to store athena output files"
  
}
