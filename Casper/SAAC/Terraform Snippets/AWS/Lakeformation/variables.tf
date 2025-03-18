# Account data
data "aws_caller_identity" "current_caller_identity" {}

# Ensure establishment of fine grained access controls
# aws_lakeformation_data_lake_settings
variable "aws_region" {
  description = "the region the tf is being run in"
  type        = string
}

variable "lakeformation_list_of_admins" {
  description = "List of Admins require access to Lake formation"
  type        = set(string)
}

variable "lakeformation_database_permissions" {
  description = "List of permissions granted to the principal on database"
  type        = set(string)
}

variable "lakeformation_database_principal" {
  description = "Principal to be granted the permissions on the resource. Supported principals are IAM users or IAM roles."
  type        = string
}

variable "lakeformation_create_table_permissions" {
  description = "List of permissions granted to the principal on tables"
  type        = set(string)
}

variable "lakeformation_create_table_principal" {
  description = "Principal to be granted the permissions on the resource. Supported principals are IAM users or IAM roles, for tables"
  type        = string
}

# lakeformation_lf_tag
variable "lakeformation_lf_tag_key" {
  description = "The key-name for the tag."
  type        = string
}

variable "lakeformation_lf_tag_values" {
  description = "A list of possible values an attribute can take."
  type        = set(string)
}

variable "lf_tag_values" {
  description = "A list of possible values an attribute can take for database"
  type        = string
}

# lakeformation_resource_s3
variable "lakeformation_resource_s3_arn" {
  description = "ARN for S3 bucket to be associated with Lake formation"
  type        = string
}

# lakeformation_resource_s3_glue_catalog_database
variable "lakeformation_resource_s3_glue_catalog_database_name" {
  description = "lake formation S3 Glue catalog database name to be used"
  type        = string
}

#  Ensure default permissions for newly created databases and tables are set to be disabled
# cg_cmk_key_alias
variable "lakeformation_kms_alias" {
  description = "Example: mydir/myalias"
  type        = string
}

data "aws_kms_alias" "cg_cmk_key_alias" {
  name = var.lakeformation_kms_alias
}

# lakeformation_permissions_tags
variable "lakeformation_permissions_principal" {
  description = "Provide principal for Lake Formation table permissions"
  type        = string
}

variable "lakeformation_permissions_permissions" {
  description = "Provide permissions list for Lake Formation Table"
  type        = list(string)
}

variable "lakeformation_permissions_lf_tag_policy_resource_type" {
  description = "The resource type for which the LF-tag policy applies."
  type        = string
}

variable "lakeformation_permissions_lf_tag_policy_expression_key1" {
  description = "Key for LF Resource Tag"
  type        = string
}

variable "lakeformation_permissions_lf_tag_policy_expression_values2" {
  description = "Value for LF Resource Tag"
  type        = set(string)
}

variable "lakeformation_permissions_s3_principal" {
  description = "Provide principal for Lake Formation S3 Bucket"
  type        = string
}

variable "lakeformation_permissions_s3_permissions" {
  description = "Provide permissions list for Lake Formation S3 Bucket"
  type        = list(string)
}

variable "lakeformation_permissions_s3_data_location_arn" {
  description = "Lake Formation S3 bucket ARN"
  type        = string
}
variable "lakeformation_security_role_arn" {
  description = "ARN for AWS Glue Database"
  type        = string
}

variable "aws_glue_catalog_database_permissions" {
  description = "Lake formation glue data base permissions"
  type        = list(string)
}

variable "aws_glue_catalog_database_name" {
  description = "Lake formation glue data base name"
  type        = string
}

variable "aws_glue_catalog_database_id" {
  description = "Lake formation glue data base catelog id"
  type        = string
}

variable "lakeformation_vpc_id" {
  description = "Lakeformation vpc id"
  type        = string
}

variable "lakeformation_service_name" {
  description = "Lakeformation Service Name"
  type        = string
}

variable "lakeformation_endpoint_type" {
  description = "Lakeformation endpoint type"
  type        = string
}

variable "lakeformation_security_group_ids" {
  description = "Lakeformation VPC Security Group ids"
  type        = set(string)
}

variable "lakeformation_iam_role_caller_identity_account_id" {
  description = "LakeFormation IAM Role Caller Account id"
  type        = string
}

variable "lakeformation_iam_role_caller_identity_account_arn" {
  description = "LakeFormation IAM Role Caller Account ARN"
  type        = string
}

variable "lakeformation_iam_role_confused_deputy_prevention_name" {
  description = "IAM Role confused deputy role name"
  type        = string
}

variable "lakeformation_iam_role_confused_deputy_prevention_description" {
  description = "IAM Role confused deputy role description"
  type        = string
}

data "template_file" "ConfusedDeputyPreventionExamplePolicy" {
  template = file("policies/ConfusedDeputyPreventionExamplePolicy.json")
  vars = {
    lakeformation_iam_role_caller_identity_account_id  = var.lakeformation_iam_role_caller_identity_account_id
    lakeformation_iam_role_caller_identity_account_arn = var.lakeformation_iam_role_caller_identity_account_arn
  }
}

variable "lakeformation_security_role_key_access_id" {
  description = "Access id for cloudTrail security role"
  type        = string
}

variable "lakeformation_security_role_key_access_arn" {
  description = ""
  type        = string
}

variable "lakeformation_security_role_key_access_name" {
  description = ""
  type        = string
}

variable "lakeformation_security_role_key_access_description" {
  description = ""
  type        = string
}

# This is a policy document instead of template file because it is complex, this is
# appropriate for now, however when Policy as Code capabilities mature we will
# need to lift all policies to JSON files
data "aws_iam_policy_document" "security_role_access_policy" {
  version = "2012-10-17"
  statement {
    actions = var.lf_sr_key_access_allowed_admin_actions
    effect  = "Allow"

    principals {
      identifiers = var.lf_sr_key_access_allowed_admin_identifiers
      type        = "AWS"
    }

    resources = var.lf_sr_key_access_allowed_admin_resources
    sid = "Allow access for Key Administrators"
  }

  statement {
    actions = var.lf_sr_key_access_allowed_use_actions
    effect = "Allow"
    
    principals {
      identifiers = var.lf_sr_key_access_allowed_use_principals
      type = "AWS"
    }

    resources = var.lf_sr_key_access_allowed_use_resources
    sid = "Allow use of the key"
  }

  statement  {
    actions = var.lf_sr_key_access_allowed_persistent_actions

    condition  {
      test = var.lf_sr_key_access_allowed_persistent_test
      values = var.lf_sr_key_access_allowed_persistent_values
      variable = "kms:GrantIsForAWSResource"
    }

    effect = "Allow"

    principals  {
      identifiers = var.lf_sr_key_access_allowed_persistent_principals
      type = "AWS"
    }

    resources = var.lf_sr_key_access_allowed_persistent_resources
    sid = "Allow attachment of persistent resources"
  }
}

variable "lakeformation_cloudtrail_bucket" {
  description = "The cloudtrail bucket that lakeformation pushes logs into"
  type        = string
}

variable "lakeformation_cloudtrail_s3_bucket_arn" {
  description = "The ARN of the cloudtrail bucket, this is used by the IAM policy"
  type        = string
}

variable "lakeformation_cloudtrail_force_destroy" {
  description = "A boolean that indicates all objects (including any locked objects) should be deleted from the bucket so that the bucket can be destroyed without error. These objects are not recoverable."
  type        = bool
}

variable "lakeformation_cloudtrail_name" {
  description = "(Required) Name of the trail."
  type        = string
}

variable "lakeformation_cloudtrail_s3_key_prefix" {
  description = "(Optional) S3 key prefix that follows the name of the bucket you have designated for log file delivery."
  type        = string
}

variable "lakeformation_security_role_trail_account_id" {
  description = "the cloudtrail account id"
  type        = string
}

data "template_file" "TrailPolicy" {
  template = file("policies/TrailPolicy.json")
  vars = {
    lakeformation_trail_s3_bucket_arn = var.lakeformation_cloudtrail_s3_bucket_arn,
    account_id                        = var.lakeformation_security_role_trail_account_id
  }
}

variable "lakeformation_security_role_trail_key_access_arn" {
  description = "the arn of the cloudtrail resource to be sent logs"
  type        = string
}

variable "lakeformation_security_role_trail_policy_name" {
  description = "the common name of this cloudtrail policy"
  type        = string
}

variable "lakeformation_security_role_trail_policy_description" {
  description = "a brief description of the cloudtrail policy"
  type        = string
}

variable "lf_sr_key_access_allowed_admin_actions" {
  description = "The actions that are used by the IAM policy statement"
  type        = set(string)
}

variable "lf_sr_key_access_allowed_admin_resources" {
  description = "Intended for ADMIN resources using the key, this is the identifier for resources the services are calling"
  type        = set(string)
}

variable "lf_sr_key_access_allowed_admin_identifiers" {
  description = ""
  type        = set(string)
}

variable "lf_sr_key_access_allowed_use_actions" {
  description = "The actions that are used by the IAM policy statement"
  type        = set(string)
}

variable "lf_sr_key_access_allowed_use_resources" {
  description = "Intended for GENERAL USE resources using the key, this is the identifier for resources the services are calling"
  type        = set(string)
}

variable "lf_sr_key_access_allowed_use_principals" {
  description = "Intended for resources using the key, this is the identifier for services calling the resources"
  type        = set(string)
}

variable "lf_sr_key_access_allowed_persistent_actions" {
  description = "The actions that you can use in an IAM policy statement"
  type        = set(string)
}

variable "lf_sr_key_access_allowed_persistent_test" {
  description = "Condition by which to filter resources"
  type        = string
}

variable "lf_sr_key_access_allowed_persistent_values" {
  description = "The actual resource being filtered by the condition"
  type        = list(string)
}

variable "lf_sr_key_access_allowed_persistent_principals" {
  description = "Intended for persistent resources, this is the identifier for services calling the resources"
  type        = set(string)
}

variable "lf_sr_key_access_allowed_persistent_resources" {
  description = "Intended for persistent resources, this is the identifier for resources the services are calling"
  type        = set(string)
}

variable "lakeformation_tags" {
  description = "Organizational tags"
  type = map(string)  
}
