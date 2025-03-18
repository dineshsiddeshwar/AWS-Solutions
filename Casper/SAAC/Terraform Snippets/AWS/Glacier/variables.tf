# AWS Provider variable

data "aws_caller_identity" "current" {}

variable "account_ids" {
  description = "Terraform state environments mapped to the target account ID"
  type        = string
}

variable "account_alias" {
  type = map(string)

}
variable "aws_access_key" {
  description = "Aws programatic user account access key for terraform to deploy resource"
  type        = string

}
variable "aws_secret_key" {
  description = "Aws programatic user account access key secret for terraform to deploy resource"
  type        = string

}

data "aws_region" "current" {}
variable "aws_region" {
  description = "Aws region where resource needs to be deployed"
  type        = string

}
variable "aws_region_acronym" {
  type = string
}

# Environment Variable
variable "glacier_tags" {
  type        = map(string)
  description = "Default tags attached to all resources."
}
variable "tags" {
  type        = string
  description = "Default tags attached to all resources."
}

# Tags used for common resource
variable "common_tags" {
  type        = map(string)
  description = "Default tags attached to all resources."

}
variable "glacier_prefix" {
  type        = string
  description = "A prefix for all the resource"
}

# kms key & alias
data "aws_kms_key" "glacier_cmk_key" {
  key_id = var.glacier_key_arn
}
data "aws_kms_alias" "glacier_cmk_key_alias" {
  name = "alias/${var.glacier_alias_name}"

}
variable "glacier_key_arn" {
  description = "The name of the key arn"
  type        = string
  sensitive   = true
}
variable "glacier_alias_name" {
  description = "The name of the key alias"
  type        = string
}

# IAM User /Role
variable "glacier_user_name" {
  type        = string
  description = "Enter the name of user to have least privledge to access Glacier service"
}

variable "glacier_role_name" {
  type        = string
  description = "Enter the name of role for asssume role policy to access Glacier service"
}

variable "glacier_user_policy" {
  type        = string
  description = "Enter the name of policy to have least privledge to access Glacier service"
}

variable "glacier_iam_policy_name" {
  type        = string
  description = "Enter the name of assume role policy  to access Glacier service"
}

# Policy : Glacier resource policies enforce least privilege - Grant Cross-account permission for specific Amazon S3 Glacier Actions
data "template_file" "glacier_cross_account_permission" {
  template = file("policies/GlacierCrossAccountPermissionPolicy.json")
  vars = {
    cross_account_id = var.cross_account_id
    account_id       = var.account_id
    vault_name       = var.vault_name
    aws_region       = var.aws_region
  }
}

variable "cross_account_id" {
  type        = string
  description = "Enter cross-account id to permit least privledge access for Glacier service"
}

variable "account_id" {
  type        = string
  description = "Enter current account id having Glacier resources"
}
variable "vault_name" {
  type        = string
  description = "Enter glacier resource name which will be available for corss account acceess for operations"
}

# Policy : Glacier resource policies enforce least privilege - Grant Cross-account permission for MFA Delete Operations
data "template_file" "glacier_cross_account_mfa_delete_operations" {
  template = file("policies/GlacierCrossAccountMFADeleteOperationsPolicy.json")
  vars = {
    cross_account_id = var.cross_account_id
    account_id       = var.account_id
    vault_name       = var.vault_name
    aws_region       = var.aws_region
  }
}

variable "glacier_iam_role_arn" {
  type        = string
  description = "Enter the iam role arn for glacier resource "
}
variable "source_ip_address" {
  type        = string
  description = "Enter the list of IP address"
}

# Policy : Glacier Assume role polyc for IAM Role
data "template_file" "glacier_assume_role_policy" {
  template = file("policies/GlacierAssumeRolePolicy.json")
}

# Policy : Glacier managed permission policy
data "template_file" "glacier_managed_permission_policy" {
  template = file("policies/GlacierManagedPermissionPolicy.json")
  vars = {
    account_id = var.account_id
    vault_name = var.vault_name
    aws_region = var.aws_region
  }
}

# Cloudwatch
variable "filter_name_prefix" {
  type        = string
  description = "Enter filter name prfix used to set filter metrics"
}

variable "filter_name_priority" {
  type        = string
  description = "Enter filter name tag based on priority tag to set filter metrics"
}

variable "filter_name_class" {
  type        = string
  description = "Enter filter name tag based on class tag to set filter metrics"
}

variable "glcaier_bucket_id" {
  type        = string
  description = "Enter bucket id of glacier bucket"
}
variable "glacier_bucket_name" {
  type        = string
  description = "Enter the name of glacier bucket"
  sensitive   = true
}
