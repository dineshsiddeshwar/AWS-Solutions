# Aws region where resource needs to be deployed. | Example: "us-west-2"
aws_region = "__AWS_REGION__"

# VPC Id of the deployed VPC, can be found on Confluence page AWS VPC CIDR Deployed (Auto updated). | Example: "vpc-0bbc736e"
aws_vpc_id = "__AWS_VPC_ID__"

# Default tags attached to all resources. | Example: { Name = "dynamodb_vpc_endpoint", ... }
dynamodb_common_tags = {
    env-type = "__ENV_TYPE__"  # "dev"  - For example only, Replace it with Application specific value
}

# Name of the DynamoDB table. | Example: "table1"
dynamodb_table_name = "__DYNAMODB_TABLE_NAME__"

# Name of IAM role for Dynamo DB. | Example: "dynamodb_default_iam_role"
dynamodb_iam_role_name = "__DYNAMODB_IAM_ROLE_NAME__"

# Alias used to refrence customer managed key for encrypting data in Dynamo DB. | Example: "alias/key_1"
cmk_key_alias = "__CMK_KEY_ALIAS__"

# Time of the point-in-time recovery point to restore. | Example: "2021-12-06T01:57:37Z"
dynamodb_table_point_in_time_recovery_date_time = "__DYNAMODB_TABLE_POINT_IN_TIME_RECOVERY_DATE_TIME__"

# Name of the table to restore. Must match the name of an existing table. | Example: "source_db_name_to_restore"
dynamodb_table_point_in_time_recovery_source_db_name = "__DYNAMODB_TABLE_POINT_IN_TIME_RECOVERY_SOURCE_DB_NAME__"

# If set, restores table to the most recent point-in-time recovery point. | Example: true
dynamodb_table_point_in_time_recovery_restore_latest_time = __DYNAMODB_TABLE_POINT_IN_TIME_RECOVERY_RESTORE_LATEST_TIME__

# Enter service name for VPC endpoint. | Example: "com.amazonaws.us-west-2.dynamodb"
dynamodb_vpc_endpoint_service_name = "__DYNAMODB_VPC_ENDPOINT_SERVICE_NAME__"

# Enter type of VPC endpoint like Interface, Gateway, GatewayLoadBalancer etc. | Example: "Interface"
dynamodb_vpc_endpoint_type = "__DYNAMODB_VPC_ENDPOINT_TYPE__"

# List of AWS Security group ID created for the VPC ID, Refer confluence page AWS Standard Security Group Baseline. | Example: ["sg-051c238028a9a1e42","sg-051c238028a9a1e43"...]
dynamodb_vpc_sg = ["__DYNAMODB_VPC_SG__"]

# Tags associated with Dynamo DB VPC endpoint. | Example: { Name = "dynamodb_vpc_endpoint", ... }
dynamodb_vpc_endpoint_tags = __DYNAMODB_VPC_ENDPOINT_TAGS__

# Name of Cluster. | Example: "dax_cluster_name"
dax_cluster_name = "__DAX_CLUSTER_NAME__"

# List of Subnets to use for Cluster Group. | Example: ["subnet-01234567890abcdef", ...]
dax_cluster_subnet_ids = ["__DAX_CLUSTER_SUBNET_IDS__"]

# Query Time To Live in milliseconds. | Example: "300000"
dax_cluster_query_ttl = "__DAX_CLUSTER_QUERY_TTL__"

# Record Time To Live in milliseconds. | Example: "300000"
dax_cluster_record_ttl = "__DAX_CLUSTER_RECORD_TTL__"

# A valid Amazon Resource Name (ARN) that identifies an IAM role. At runtime, DAX will assume this role and use the role's permissions to access DynamoDB on your behalf. | Example: "arn:aws:iam::123456789012:role/DAXAccess"
dax_cluster_iam_role_arn = "__DAX_CLUSTER_IAM_ROLE_ARN__"

# The compute and memory capacity of the DAX nodes. | Example: "dax.r4.large"
dax_cluster_node_type = "__DAX_CLUSTER_NODE_TYPE__"

# The number of nodes in the DAX cluster. If 1 then it will create a single-node cluster, without any read replicas. | Example: 1
dax_cluster_node_count = __DAX_CLUSTER_NODE_COUNT__

# Server Side Encryption of DAX cluster. | Example: true
dax_cluster_server_side_encryption = __Server_Side_Encryption__

# Specifies the weekly time range for when maintenance on the cluster is performed. The format is ddd:hh24:mi-ddd:hh24:mi (24H Clock UTC). The minimum maintenance window is a 60 minute period. | Example: "sun:00:00-sun:01:00"
dax_cluster_maintenance_window = "__DAX_CLUSTER_MAINTENANCE_WINDOW__"

# One or more VPC security groups associated with the cluster. | Example: ["sg-051c238028a9a1e42","sg-051c238028a9a1e43"...]
dax_cluster_security_group_ids = ["__DAX_CLUSTER_SECURITY_GROUP_IDS__"]
