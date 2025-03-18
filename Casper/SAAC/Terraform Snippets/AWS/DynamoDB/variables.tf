# AWS Provider variable
variable "aws_region" {
  description = "Aws region where resource needs to be deployed. | Example: \"us-west-2\""
  type        = string

}

# Generic AWS Information
data "aws_caller_identity" "current" {}

variable "aws_vpc_id" {
  type        = string
  description = "VPC Id of the deployed VPC, can be found on Confluence page AWS VPC CIDR Deployed (Auto updated). | Example: \"vpc-0bbc736e\""
}

data "aws_vpc" "aws_vpc_id" {
  id = var.aws_vpc_id
}

variable "dynamodb_common_tags" {
  type        = map(string)
  description = "Default tags attached to all resources. | Example: { Name = \"dynamodb_vpc_endpoint\", ... }"
}

# Dynamo DB Info
variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table. | Example: \"table1\""
  type        = string

}

data "aws_dynamodb_table" "dynamodb_table" {
  name = var.dynamodb_table_name
}

# DynamoDB IAM Requirements
data "template_file" "dynamodb_iam_role_file" {
  template = "Policies/dynamoDBIamRole.json"
  vars = {
    region     = var.aws_region
    account_id = local.account_id
  }
}

variable "dynamodb_iam_role_name" {
  type        = string
  description = "Name of IAM role for Dynamo DB. | Example: \"dynamodb_default_iam_role\""
}

# Encryption of data at REST
variable "cg_cmk_key_alias" {
  description = "Alias used to refrence customer managed key for encrypting data in Dynamo DB. | Example: \"alias/key_1\""
  type        = string
  sensitive   = true
}
# Get cmk key using alias name
data "aws_kms_alias" "cg_cmk_key_alias" {
  name = "alias/${var.cg_cmk_key_alias}"
}

# Dynamo DB Recovery Variables
variable "dynamodb_table_point_in_time_recovery_date_time" {
  description = "Time of the point-in-time recovery point to restore. | Example: \"2021-12-06T01:57:37Z\""
  type = string
}
variable "dynamodb_table_point_in_time_recovery_source_db_name" {
  description = "Name of the table to restore. Must match the name of an existing table. | Example: \"source_db_name_to_restore\""
  type = string
}
variable "dynamodb_table_point_in_time_recovery_restore_latest_time" {
  description = "If set, restores table to the most recent point-in-time recovery point. | Example: true"
  type = bool
}


# VPC Endpoint details
variable "dynamodb_vpc_endpoint_service_name" {
  description = "Enter service name for VPC endpoint. | Example: \"com.amazonaws.us-west-2.dynamodb\""
  type        = string
}
variable "dynamodb_vpc_endpoint_type" {
  description = "Enter type of VPC endpoint like Interface, Gateway, GatewayLoadBalancer etc. | Example: \"Interface\""
  type        = string
}

variable "dynamodb_vpc_sg" {
  description = "List of AWS Security group ID created for the VPC ID, Refer confluence page AWS Standard Security Group Baseline. | Example: [\"sg-051c238028a9a1e42\",\"sg-051c238028a9a1e43\"...]"
  type        = list(string)
}

variable "dynamodb_vpc_endpoint_tags" {
  description = "Tags associated with Dynamo DB VPC endpoint. | Example: { Name = \"dynamodb_vpc_endpoint\", ... }"
  type        = map(string)
}

# Cloud watch resources
variable "dynamodb_cloudwatch_consumed_read_units_alarm_name" {
  description = "Name of CloudWatch Alarm for DynamoDB consumed read units. | Example: \"dynamodb_read_units_alarm\""
  type        = string
}

variable "dynamodb_cloudwatch_consumed_read_units_alarm_description" {
  description = "Description of CloudWatch Alarm for DynamoDB consumed read units. | Example: \"This metric monitors DynamoDB ConsumedReadCapacityUnits for <dynamodb_table_name>\""
  type        = string
}

variable "dynamodb_cloudwatch_consumed_read_units_alarm_evaluation_periods" {
  description = "Evaluation Period for DynamoDB consumed read units alarm. | Example: \"5\""
  type        = string
}
variable "dynamodb_cloudwatch_consumed_read_units_alarm_period" {
  description = "Period for DynamoDB consumed read units alarm in seconds. | Example: \"60\""
  type        = string
}
variable "dynamodb_cloudwatch_consumed_read_units_alarm_threshold" {
  description = "The value against which the specified statistic is compared.  | Example: \"4\""
  type = string

}

variable "dynamodb_cloudwatch_consumed_read_units_alarm_treat_missing_data" {
  description = "Sets how this alarm is to handle missing data points.  | Example: \"missing\""
  type = string
  validation {
    condition     = var.dynamodb_cloudwatch_consumed_read_units_alarm_treat_missing_data == "missing" || var.dynamodb_cloudwatch_consumed_read_units_alarm_treat_missing_data == "ignore" || var.dynamodb_cloudwatch_consumed_read_units_alarm_treat_missing_data == "breaching" || var.dynamodb_cloudwatch_consumed_read_units_alarm_treat_missing_data == "notBreaching"
    error_message = "The treat_missing_data value must be a valid. ref:https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_metric_alarm ."
  }
}

variable "dynamodb_cloudwatch_consumed_read_units_alarm_insufficient_data_actions" {
  description = "The list of actions to execute when this alarm transitions into an INSUFFICIENT_DATA state from any other state. Each action is specified as an Amazon Resource Name (ARN). | Example: [\"arn:aws:sns:us-west-2:344526710204:security-alerts-topic\", ...]"
  type = list(string)

}

variable "dynamodb_cloudwatch_consumed_read_units_alarm_datapoints_to_alarm" {
  description = "The number of datapoints that must be breaching to trigger the alarm. | Example: 2"
  type = number
}

variable "dynamodb_cloudwatch_consumed_read_units_alarm_tags" {
  description = "Tags associated with DynamoDB Read units alarm. | Example: { Name = \"cloudwatch_red_units_alarm\", ... }"
  type        = map(string)
}

variable "dynamodb_cloudwatch_consumed_read_units_alarm_sns_topic_arns" {
  description = "List of Sns topic arn for reporting DynamoDB read unites alarm. | Example: [\"arn:aws:sns:us-west-2:344526710204:security-alerts-topic\", ...]"
  type        = set(string)
}

# DAX cluster resources
variable "dax_cluster_name" {
  description = "Name of Cluster. | Example: \"dax_cluster_name\""
  type        = string
}

variable "dax_cluster_subnet_ids" {
  description = "List of Subnets to use for Cluster Group. | Example: [\"subnet-01234567890abcdef\", ...]"
  type        = list(string)
}

variable "dax_cluster_query_ttl" {
  description = "Query Time To Live in milliseconds. | Example: \"300000\""
  type        = string
}

variable "dax_cluster_record_ttl" {
  description = "Record Time To Live in milliseconds. | Example: \"300000\""
  type        = string
}

variable "dax_cluster_iam_role_arn" {
  description = "A valid Amazon Resource Name (ARN) that identifies an IAM role. At runtime, DAX will assume this role and use the role's permissions to access DynamoDB on your behalf. | Example: \"arn:aws:iam::123456789012:role/DAXAccess\""
  type        = string
}

variable "dax_cluster_node_type" {
  description = "The compute and memory capacity of the DAX nodes. | Example: \"dax.r4.large\""
  type        = string
}

variable "dax_cluster_node_count" {
  description = "The number of nodes in the DAX cluster. If 1 then it will create a single-node cluster, without any read replicas. | Example: 1"
  type        = number
}

variable "dax_cluster_maintenance_window" {
  type        = string
  description = "Specifies the weekly time range for when maintenance on the cluster is performed. The format is ddd:hh24:mi-ddd:hh24:mi (24H Clock UTC). The minimum maintenance window is a 60 minute period. | Example: \"sun:00:00-sun:01:00\""
}

variable "dax_cluster_security_group_ids" {
  type        = list(string)
  description = "One or more VPC security groups associated with the cluster. | Example: [\"sg-051c238028a9a1e42\",\"sg-051c238028a9a1e43\"...]"
}
