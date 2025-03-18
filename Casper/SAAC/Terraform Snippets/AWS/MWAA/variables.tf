# Account resources
data "aws_caller_identity" "current_caller_identity" {}

locals {
  account_id=data.aws_caller_identity.current_caller_identity.account_id
}

variable "aws_region" {
  description = "AWS Provider Region"
  type        = string
}

#### Common Variables begin
variable "mwaa_tags" {
  description = "Tags for all MWAA resources"
  type        = map(string)
}
#### Common Variables end

#### Variables for resource aws_vpc_endpoint begins
variable "aws_vpc_id" {
  description = "AWS VPC ID"
  type        = string
}

data "aws_vpc" "aws_vpc_id" {
  id = var.aws_vpc_id # string
}

variable "mwaa_service_name" {
  description = "Airflow service name"
  type        = string
}
# For the Apache Airflow environment - "com.amazonaws.us-west-2.airflow.env"
# For Apache Airflow operations - "com.amazonaws.us-west-2.airflow.ops"

variable "mwaa_vpc_endpoint_type" {
  description = "The VPC endpoint type, Gateway, GatewayLoadBalancer, or Interface. Defaults to Interface."
  type        = string
}

variable "mwaa_sg_ids" {
  description = "Airflow security groups"
  type        = list(string)
}
#### Variables for resource aws_vpc_endpoint ends

#### Variables for iam resources begins
variable "mwaa_iam_user" {
  description = "Airflow Iam user name"
  type        = string
}

variable "mwaa_iam_policy_name" {
  description = "IAM policy name"
  type        = string
}

data "template_file" "mwaa_iam_policy_file" {
  template = file("policies/AirflowIamAccessPolicy.json")
  vars = {
    account_id     = local.account_id
    execution_role = var.mwaa_iam_policy_file_execution_role
  }
}

variable "mwaa_iam_policy_file_execution_role" {
  description = "IAM Roles allowed to assigned to IAM Policy "
  type        = string
}

variable "mwaa_iam_execution_role_name" {
  description = "IAM ROles"
  type        = string
}

data "template_file" "mwaa_iam_execution_role_file" {
  template = file("policies/AirflowIamExecutionRole.json")
  vars = {
    s3_bucket_arn = data.aws_s3_bucket.mwaa_s3_bucket.arn
  }
}

variable "mwaa_iam_execution_policy_name" {
  description = ""
  type        = string
}

variable "mwaa_iam_execution_policy_path" {
  description = ""
  type        = string
  # default = "/"
}

data "template_file" "mwaa_iam_execution_policy_file" {
  template = "policies/AirflowIamExecutionPolicy.json"
  vars = {
    mwaa_environment_arn = aws_mwaa_environment.mwaa_environment.arn
    bucket_arn           = data.aws_s3_bucket.mwaa_s3_bucket.arn
    mwaa_cloudtrail_arn  = var.mwaa_cloudtrail_arn
    aws_region           = var.aws_region
    account_id           = local.account_id
  }
}
#### Variables for iam resources ends

#### Variables for mwaa environment resources begins
variable "mwaa_environment_name" {
  description = "The name of the Apache Airflow Environment"
  type        = string
}

# Pre defined MWAA S3 Bucket
variable "mwaa_s3_bucket_name" {
  type        = string
  description = "The name of S3 bucket asscoiated with MWAA resource."
}

data "aws_s3_bucket" "mwaa_s3_bucket" {
  bucket = var.mwaa_s3_bucket_name
}

variable "mwaa_enviroment_dag_s3_path" {
  description = "The relative path to the DAG folder on your Amazon S3 storage bucket."
  type        = string
}

variable "mwaa_enviroment_plugins_s3_path" {
  description = "The relative path to the plugins.zip file on your Amazon S3 storage bucket."
  type        = string
  # default = "plugins.zip"
}

variable "mwaa_enviroment_requirements_s3_path" {
  description = "The relative path to the requirements.txt file on your Amazon S3 storage bucket."
  type        = string
  # default = "requirements.txt"
}

variable "mwaa_max_workers" {
  description = "The maximum number of workers that can be automatically scaled up. Value need to be between 1 and 25. Will be 10 by default."
  type        = number
}

variable "mwaa_kms_key_arn" {
  description = "The ARN of your KMS key that you want to use for encryption. "
  type        = string
}

variable "mwaa_environment_sg_ids" {
  description = "Security groups IDs for the MWAA environment."
  type        = list(string)
}

variable "mwaa_environment_vpc_private_subnet_id" {
  description = "Two private subnets needed for MWAA environment"
  type        = set(string)
}
#### Variables for mwaa environment resources ends

#### Variables for Secrets Manager resources begins
variable "mwaa_logging_user_secretsmanager_secret_name" {
  description = "Name of Secret manager secret Key for aws airflow."
  type        = string
}
data "template_file" "mwaa_logging_user_secretsmanager_secret_policy_file" {
  template = file("policies/AirflowSecretManagerSecretsPolicy.json")
  vars = {
    account_id = local.account_id
  }
}
#### Variables for Secrets Manager resources ends
#### Variables for cloudTrail begins
variable "mwaa_cloudtrail_arn"{
  description = "ARN for CloudTrail refrenced by aws airflow."
  type        = string
}
#### Variables for cloudTrail ends
