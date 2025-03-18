/*
 * # Terraform DynamoDB deployment
 * 
 * Requirements: 
 *  Ensure least privilege access is enforced for all DynamoDB users and roles
 *  Ensure DynamoDB tables are encrypted at rest using organization managed CMK
 *  Ensure Data in Transit for DynamoDB is encrypted using TLS 1.2
 *  Ensure DynamoDB uses VPC Endpoints to communicate with services inside VPC
 *  Ensure CloudTrail logging is enabled for DynamoDB
 *  Ensure CloudWatch Alarms is enabled to monitor DynamoDB
 *  Ensure Amazon DynamoDB tables have continuous backups enabled
 *  Ensure on-demand backup and restore functionality is in use for DynamoDB tables
 *  Ensure object tagging is enabled for DynamoDB
 *  Ensure unused DynamoDB tables are removed
 *  Ensure DynamoDB streams is used to support data-plane logging
 *  Ensure Amazon DynamoDB Accelerator (DAX) clusters enforce Server-Side Encryption (SSE)
 *
 */

locals {
  account_id = data.aws_caller_identity.current.account_id
}

#  Ensure least privilege access is enforced for all DynamoDB users and roles
resource "aws_iam_role" "dynamodb_iam_role" {
  name               = var.dynamodb_iam_role_name
  assume_role_policy = data.template_file.dynamodb_iam_role_file.rendered
  tags               = var.dynamodb_common_tags # Ensure object tagging is enabled for DynamoDB
}

#  Ensure DynamoDB tables are encrypted at rest using organization managed CMK
resource "aws_dynamodb_table" "dynamodb_table" {
  name = data.aws_dynamodb_table.dynamodb_table.id
  server_side_encryption {
    enabled     = true
    kms_key_arn = data.aws_kms_alias.cg_cmk_key_alias.arn
  }
  point_in_time_recovery { # Ensure Amazon DynamoDB tables have continuous backups enabled
    enabled = true
  }
  #  Ensure on-demand backup and restore functionality is in use for DynamoDB tables
  restore_date_time      = var.dynamodb_table_point_in_time_recovery_date_time
  restore_source_name    = var.dynamodb_table_point_in_time_recovery_source_db_name
  restore_to_latest_time = var.dynamodb_table_point_in_time_recovery_restore_latest_time
  tags                   = var.dynamodb_common_tags
}
#  Ensure Data in Transit for DynamoDB is encrypted using TLS 1.2
# Implemented by default

#  Ensure unused DynamoDB tables are removed
/*
This is done through ansible automation platform lifecycle. 
Please refer the link: 
*/

#  Ensure DynamoDB streams is used to support data-plane logging
resource "aws_kinesis_stream" "dynamodb_kinesis" {
  name        = "order_item_changes"
  shard_count = 1
  tags        = var.dynamodb_common_tags
}
resource "aws_dynamodb_kinesis_streaming_destination" "dynamodb_kinesis_streaming_destination" {
  stream_arn = aws_kinesis_stream.dynamodb_kinesis.arn
  table_name = aws_dynamodb_table.dynamodb_table.name
}


#  Ensure DynamoDB uses VPC Endpoints to communicate with services inside VPC
resource "aws_vpc_endpoint" "dynamodb_vpc_endpoint" {
  vpc_id              = data.aws_vpc.aws_vpc_id.id
  service_name        = var.dynamodb_vpc_endpoint_service_name
  vpc_endpoint_type   = var.dynamodb_vpc_endpoint_type
  security_group_ids  = var.dynamodb_vpc_sg
  private_dns_enabled = true

  tags = var.dynamodb_vpc_endpoint_tags
}

#  Ensure CloudTrail logging is enabled for DynamoDB
/*
Actions are performed and managed by preexisting organisation model
*/


#  Ensure ClaudWatch Alarms is enabled to monitor DynamoDB
resource "aws_cloudwatch_metric_alarm" "dynamodb_cloudwatch_consumed_read_units_alarm" {
  alarm_name          = var.dynamodb_cloudwatch_consumed_read_units_alarm_name
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = var.dynamodb_cloudwatch_consumed_read_units_alarm_evaluation_periods
  metric_name         = "ConsumedReadCapacityUnits"
  namespace           = "AWS/DynamoDB"
  period              = var.dynamodb_cloudwatch_consumed_read_units_alarm_period
  statistic           = "Average"
  dimensions = {
    TableName = "${var.dynamodb_table_name}"
  }
  threshold                 = var.dynamodb_cloudwatch_consumed_read_units_alarm_threshold
  alarm_description         = var.dynamodb_cloudwatch_consumed_read_units_alarm_description
  insufficient_data_actions = var.dynamodb_cloudwatch_consumed_read_units_alarm_insufficient_data_actions
  datapoints_to_alarm       = var.dynamodb_cloudwatch_consumed_read_units_alarm_datapoints_to_alarm
  treat_missing_data        = var.dynamodb_cloudwatch_consumed_read_units_alarm_treat_missing_data
  alarm_actions             = var.dynamodb_cloudwatch_consumed_read_units_alarm_sns_topic_arns
  tags                      = var.dynamodb_cloudwatch_consumed_read_units_alarm_tags
}

#  Ensure Amazon DynamoDB Accelerator (DAX) clusters enforce Server-Side Encryption (SSE)
# Create DAX Subnet Group
resource "aws_dax_subnet_group" "dax_cluster_subnet_group" {
  name       = var.dax_cluster_name
  subnet_ids = var.dax_cluster_subnet_ids
}
# Create DAX Subnet Group
resource "aws_dax_parameter_group" "dax_cluster_parameter_group" {
  name = var.dax_cluster_name

  parameters {
    name  = "query-ttl-millis"
    value = var.dax_cluster_query_ttl
  }

  parameters {
    name  = "record-ttl-millis"
    value = var.dax_cluster_record_ttl
  }
}

# Create DAX Cluster
resource "aws_dax_cluster" "dax_cluster" {
  cluster_name       = var.dax_cluster_name
  iam_role_arn       = var.dax_cluster_iam_role_arn
  node_type          = var.dax_cluster_node_type
  replication_factor = var.dax_cluster_node_count
  server_side_encryption {
    enabled = true
    # enabled = var.dax_cluster_server_side_encryption ###################Note: Should be True ????
  }
  parameter_group_name = aws_dax_parameter_group.dax_cluster_parameter_group.name
  subnet_group_name    = aws_dax_subnet_group.dax_cluster_subnet_group.name
  maintenance_window   = var.dax_cluster_maintenance_window
  security_group_ids   = var.dax_cluster_security_group_ids
  tags                 = var.dynamodb_common_tags
}

