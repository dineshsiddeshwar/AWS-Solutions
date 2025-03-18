# AWS Provider variable
variable "aws_region" {
  description = "Aws region where resource needs to be deployed. | Example: \"us-west-2\""
  type        = string
}

variable "efs_common_tags" {
  type        = map(string)
  description = "Default tags attached to all resources. | Example: { Name = \"efs_system_1\", ... }"
}

data "aws_caller_identity" "current" {}

variable "aws_vpc_id" {
  type        = string
  description = "VPC Id of the deployed VPC, can be found on Confluence page AWS VPC CIDR Deployed (Auto updated). | Example: \"vpc-0bbc736e\""
}

data "aws_vpc" "aws_vpc_id" {
  id = var.aws_vpc_id
}

# Generic EFS Variables begin
variable "efs_availability_zone_name" {
  type = string
  description = "Awailability zone for EFS. Optional (Required for single IA EFS) | Example: \"us-west-2a\""
}

variable "efs_creation_token" {
  type = string
  description = "A unique name (a maximum of 64 characters are allowed) used as reference when creating the Elastic File System. Optional | Example: \"efs_system_1\""
}

variable "efs_data_lifecycle_to_ia" {
  type=string
  description = "How long it takes to transition files to the IA storage class. | Example: \"AFTER_7_DAYS\""
  validation {
    condition     = var.efs_data_lifecycle_to_ia == "AFTER_7_DAYS" || var.efs_data_lifecycle_to_ia == "AFTER_14_DAYS" || var.efs_data_lifecycle_to_ia == "AFTER_30_DAYS" || var.efs_data_lifecycle_to_ia == "AFTER_60_DAYS" || var.efs_data_lifecycle_to_ia == "AFTER_90_DAYS" || var.efs_data_lifecycle_to_ia == ""
    error_message = "The lifecycle value must be valid. ref:https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/efs_file_system#lifecycle-policy-arguments ."
  }
}

variable "efs_data_lifecycle_to_primary_sc" {
  type=string
  description = "Describes when to transition a file from IA storage to primary storage.  | Example: \"AFTER_1_ACCESS\""
  validation {
    condition     = var.efs_data_lifecycle_to_primary_sc == "AFTER_1_ACCESS" || var.efs_data_lifecycle_to_primary_sc == ""
    error_message = "The lifecycle value must be valid. ref:https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/efs_file_system#lifecycle-policy-arguments ."
  }
}

variable "efs_performance_mode" {
  type = string
  description = "Awailability zone for EFS | Example: \"generalPurpose\""
  validation {
    condition     = var.efs_performance_mode == "generalPurpose" || var.efs_performance_mode == "maxIO"
    error_message = "The performance mode value must be valid. ref:https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/efs_file_system#performance_mode ."
  }
}

variable "efs_throughput_mode" {
  type=string
  description = "Throughput mode for the file system. Defaults to bursting | Example: \"bursting\""
  validation {
    condition     = var.efs_throughput_mode == "bursting" || var.efs_throughput_mode == "provisioned"
    error_message = "The throughput mode value must be valid. ref:https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/efs_file_system#throughput_mode ."
  }
}

variable "efs_provisioned_throughput" {
  type=number
  description = "The throughput, measured in MiB/s, that you want to provision for the file system. Only applicable with throughput_mode set to provisioned. | Example: 10"
}

variable "efs_specific_tags" {
  type = map(string)
  description = "Tags specific to EFS | Example: { Name = \"efs_vpc_endpoint\", ... }"
}
# Generic EFS Variables end

# EFS VPC Endpoint variables begin
variable "efs_vpc_endpoint_service_name" {
  type = string
  description = "Name of EFS VPC endpoint service | Example: \"com.amazonaws.us-west-2.efs\""
}

variable "efs_vpc_endpoint_type" {
  type = string
  description = "EFS VPC endpoint type, Gateway, GatewayLoadBalancer, or Interface | Example: \"Gateway\""
   validation {
    condition     = var.efs_vpc_endpoint_type == "Gateway" || var.efs_vpc_endpoint_type == "GatewayLoadBalancer" || var.efs_vpc_endpoint_type == "Interface"
    error_message = "The throughput mode value must be valid. ref:https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint#vpc_endpoint_type ."
  }
}

variable "efs_vpc_endpoint_sg_ids" {
  type = set(string)
  description = "List of Secuity Groups asscoiated with VPC endpoint | Example: [\"sg-051c238028a9a1e42\", ...]"
}

variable "efs_vpc_endpoint_tags" {
  type = map(string)
  description = "Tags specific to EFS VPC Endpoint | Example: { Name = \"efs_vpc_endpoint\", ... }"
}
# EFS VPC Endpoint variables end

# EFS Encryption of data at REST, variables begin
variable "cg_cmk_key_alias" {
  description = "Alias used to refrence customer managed key for encrypting data in Dynamo DB. | Example: \"alias/key_1\""
  type        = string
  sensitive   = true
}

data "aws_kms_alias" "cg_cmk_key_alias" {
  name = "alias/${var.cg_cmk_key_alias}"
}
# EFS Encryption variables ends

# EFS IAM Variables begin
variable "efs_iam_user_name" {
  type = string
  description = "User name for account with efs access. | Example: \"efs_account_name\""
}
data "aws_iam_user" "efs_iam_user" {
  user_name = var.efs_iam_user_name
}


data "template_file" "efs_iam_role_file" {
  template = "Policies/EFSIamRole.json"
  vars = {
    aws_user = data.aws_iam_user.efs_iam_user.arn
  }
}

variable "efs_iam_role_name" {
  type        = string
  description = "Name of IAM role for EFS. | Example: \"efs_default_iam_role\""
}
# EFS IAM Variables end

# EFS Access Policy Variables begin
data "template_file" "efs_access_policy_file" {
  template = "Policies/EFSAccessPolicy.json"
  vars = {
    efs_access_role = aws_iam_role.efs_iam_role.arn
    aws_efs_arn     = aws_efs_file_system.efs_file_system.arn
  }
}
# EFS Access Policy Variables end
