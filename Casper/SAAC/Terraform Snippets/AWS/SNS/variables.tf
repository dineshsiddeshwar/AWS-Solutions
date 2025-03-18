data "aws_region" "current" {}

data "aws_caller_identity" "current" {}

variable "aws_access_key" {
  description = "Aws programatic user account access key for terraform to deploy resource"
  type        = string
}

variable "common_tags" {
  description = "Tags for all EC2 resources"
  type        = map(string)
}
variable "sns_topic_name" {
  description = "The name of the SNS topic"
  type        = string 
}
variable "sns_endpoint" {
  description = "Example: *@capgroup.com"
  type        = string
}

variable "aws_secret_key" {
  description = "Aws programatic user account access key secret for terraform to deploy resource"
  type        = string
}

variable "aws_region" {
  description = "Aws region where resource needs to be deployed"
  type        = string
}

data "aws_vpc" "aws_vpc_id" {
  id = var.sns_aws_vpc_id

}

variable "sns_aws_vpc_id" {
  description = "VPC ID"
  type        = string
}

# SNS permissions for least privilege policies
data "template_file" "sns_least_privilege_policy" {
  template = file("policies/SNSLeastPrivilegePolicy.json")
  vars = {
    account_id = data.aws_caller_identity.current.account_id
  }
}

variable "sns_service_name" {
  type = string
}

variable "sns_vpc_endpoint_type" {
  type = string

}

variable "sns_vpc_endpoint" {
  type = string
}

data "aws_kms_key" "cg_cmk_key" {
  key_id = "alias/${var.sns_key_alias}"
}

variable "sns_key_alias" {
  type = string
}

variable "sns_prefix" {
  type = string
}

variable "sns_vpc_sgs" {
  description = "an array of security groups Example: ['sg-123abc', 'sg-456def's]"
  type = set(string)
}

variable "account_ids" {
  type = string
}


variable "sns_bucket" {
  type = string
}

# SNS permissions for delivery policy
data "template_file" "sns_delivery_policy" {
  template = file("policies/SNSDeliveryPolicy.json")
  vars = {
    sns_endpoint          = var.sns_endpoint
    backoff_function      = var.backoff_function
  }
}
variable "backoff_function" {
  type = string
}
# SNS permissions for IAM role access policy
data "template_file" "sns_role_access_policy" {
  template = file("policies/SNSRoleAccessPolicy.json")
  vars = {
    account_id = data.aws_caller_identity.current.account_id
    aws_region = var.aws_region
  }
}

# SNS permissions policy for Topics not exposed to everyone 
data "template_file" "sns_topics_not_exposed_to_everyone_policy" {
  template = file("policies/SNSTopicsNotExposedToEveryonePolicy.json")
  vars = {
    sns_endpoint = var.sns_endpoint
  }
}

variable "key_alias" {
  type = string
}

data "aws_kms_alias" "cg_cmk_key_alias" {
  name = "alias/${var.sns_alias_name}"
}

variable "sns_alias_name" {
  description = "The name of the key alias"
  type        = string
}
