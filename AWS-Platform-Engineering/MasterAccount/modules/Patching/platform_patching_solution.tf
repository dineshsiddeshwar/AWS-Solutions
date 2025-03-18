# Patching managed instance data encryption key
resource "aws_kms_key" "patching_managed_instance_encryption_key" {
  is_enabled = true
  enable_key_rotation = true
  description = "Key used to encrypt instance data"
}

# Patching managed instance data encryption key policy
resource "aws_kms_key_policy" "patching_managed_instance_encryption_key_policy" {
  key_id = aws_kms_key.patching_managed_instance_encryption_key.id
  policy = jsonencode({
    "Version": "2012-10-17",
    "Id": "AccountPolicy",
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${var.master_account}:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        },
        {
            "Sid": "Allow use of the key by Systems Manager",
            "Effect": "Allow",
            "Principal": {
                "Service": "ssm.amazonaws.com"
            },
            "Action": [
                "kms:DescribeKey",
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey",
                "kms:GenerateDataKeyWithoutPlaintext"
            ],
            "Resource": "*"
        },
        {
            "Sid": "Allow use of the key by service roles within the organization",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "kms:Encrypt",
                "kms:GenerateDataKey"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:PrincipalOrgID": var.org_id
                }
            }
        },
        {
            "Sid": "Enable Operator Permissions",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "kms:Decrypt",
            "Resource": "*",
            "Condition": {
                "StringLike": {
                    "aws:PrincipalArn": "arn:aws:iam::${var.master_account}:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_platform_Operator*"
                }
            }
        }
    ]
  })
}

# Patching managed instance data encryption key alias
resource "aws_kms_alias" "patching_managed_instance_encryption_key_alias" {
  name          = "alias/SSM-ManagedInstanceDataEncryptionKey"
  target_key_id = aws_kms_key.patching_managed_instance_encryption_key.key_id
}

# Resource Sync S3 Bucket
resource "aws_s3_bucket" "resource_sync_bucket" {
  bucket = "ssm-resource-sync-us-east-1-${var.master_account}"
}

# Resource Sync S3 Bucket server side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "resource_sync_bucket_encryption" {
  bucket = aws_s3_bucket.resource_sync_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.patching_managed_instance_encryption_key.key_id
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = false
  }
}

# Resource Sync S3 Bucket block public access
resource "aws_s3_bucket_public_access_block" "resource_sync_bucket_block_public_access" {
  bucket = aws_s3_bucket.resource_sync_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Resource Sync S3 Bucket versioning
resource "aws_s3_bucket_versioning" "resource_sync_bucket_versioning" {
  bucket = aws_s3_bucket.resource_sync_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Resource Sync S3 Bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "resource_sync_bucket_lifecycle_configuration" {
  bucket = aws_s3_bucket.resource_sync_bucket.id

  rule {
    id = "ResourceSyncGlacierRule"

    expiration {
      days = 180
    }

    filter {}

    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

# Resource Sync S3 Bucket  Ownership controls
resource "aws_s3_bucket_ownership_controls" "resource_sync_bucket_ownership" {
  bucket = aws_s3_bucket.resource_sync_bucket.id

  rule {
    object_ownership = "ObjectWriter"
  }
}

resource "aws_s3_bucket_acl" "resource_sync_bucket_acl" {
  bucket = aws_s3_bucket.resource_sync_bucket.id
}

# Resource Sync S3 Bucket policy
resource "aws_s3_bucket_policy" "resource_sync_bucket_policy" {
  bucket = aws_s3_bucket.resource_sync_bucket.id
  policy = data.aws_iam_policy_document.data_resource_sync_bucket_policy.json
}

# Execution Logs S3 Bucket
resource "aws_s3_bucket" "execution_logs_bucket" {
  bucket = "ssm-execution-logs-us-east-1-${var.master_account}"
}

# Execution Logs S3 Bucket server side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "execution_logs_bucket_encryption" {
  bucket = aws_s3_bucket.execution_logs_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
    bucket_key_enabled = false
  }
}

# Execution Logs S3 Bucket block public access
resource "aws_s3_bucket_public_access_block" "execution_logs_bucket_block_public_access" {
  bucket = aws_s3_bucket.execution_logs_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Execution Logs S3 Bucket versioning
resource "aws_s3_bucket_versioning" "execution_logs_bucket_versioning" {
  bucket = aws_s3_bucket.execution_logs_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Execution Logs S3 Bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "execution_logs_bucket_lifecycle_configuration" {
  bucket = aws_s3_bucket.execution_logs_bucket.id

  rule {
    id = "ExecutionGlacierRule"

    expiration {
      days = 180
    }

    filter {}

    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

# Execution Logs S3 Bucket  Ownership controls
resource "aws_s3_bucket_ownership_controls" "execution_logs_bucket_ownership" {
  bucket = aws_s3_bucket.execution_logs_bucket.id

  rule {
    object_ownership = "ObjectWriter"
  }
}

resource "aws_s3_bucket_acl" "execution_logs_bucket_acl" {
  bucket = aws_s3_bucket.execution_logs_bucket.id
}

# Execution Logs S3 Bucket policy
resource "aws_s3_bucket_policy" "execution_logs_bucket_policy" {
  bucket = aws_s3_bucket.execution_logs_bucket.id
  policy = data.aws_iam_policy_document.data_execution_logs_bucket_policy.json
}

# Patching Window catalog product
resource "aws_servicecatalog_product" "patching_servicecatalog_product" {
  accept_language  = "en"
  name  = "platform_patching_window_product"
  owner = "Shell"
  distributor = "Wipro"
  type  = "CLOUD_FORMATION_TEMPLATE"
  support_email = "SITI-CLOUD-SERVICES@shell.com"
  provisioning_artifact_parameters {
    template_url = "https://s3.amazonaws.com/${var.release_bucket_name}/TFC-Master/10/ServiceCatalogTemplates/patching_window.template"
    name = var.patching_template_version
    type = "CLOUD_FORMATION_TEMPLATE"
  }
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Patching Window catalog portfolio
resource "aws_servicecatalog_portfolio" "patching_servicecatalog_portfolio" {
  name          = "platform_patching_portfolio"
  provider_name = "Shell"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Patching Window catalog product portfolio association
resource "aws_servicecatalog_product_portfolio_association" "patching_servicecatalog_product_portfolio_association" {
  portfolio_id = aws_servicecatalog_portfolio.patching_servicecatalog_portfolio.id
  product_id   = aws_servicecatalog_product.patching_servicecatalog_product.id
}

# Patching Window catalog product launch constraint
resource "aws_servicecatalog_constraint" "patching_servicecatalog_product_launch_constraint" {
  portfolio_id = aws_servicecatalog_portfolio.patching_servicecatalog_portfolio.id
  product_id   = aws_servicecatalog_product.patching_servicecatalog_product.id
  type         = "LAUNCH"

  parameters = jsonencode({
    "LocalRoleName" : aws_iam_role.servicecatalog_launch_role.name
  })
  depends_on = [
    aws_iam_role.servicecatalog_launch_role
 ]
}

# Service Catalog launch role
resource "aws_iam_role" "servicecatalog_launch_role" {
  name = "platform-service-catalog-launch-role"
  description = "Role created to launch SC products"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "servicecatalog.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
  path = "/"
}

# Emergency patching Lambda
resource "aws_lambda_function" "emergency_patching_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_emergency_patching.zip"
  function_name = "platform_emergency_patching"
  role          =  var.role_arn
  handler       = "platform_emergency_patching.lambda_handler"
  source_code_hash = data.archive_file.emergency_patching_lambda_zip.output_base64sha256

  environment {
    variables = {
      TASK_LAMBDA_NAME = "platform_maintenance_window_task"
      ASG_TASK_LAMBDA_NAME = "platform_maintenance_window_asg_task"
      PATCHING_TEMPLATE_REGION = "us-east-1"
    }
  } 

  runtime = "python3.8"
  memory_size = 128
  timeout = 900
}

# Patch Baseline Override S3 Bucket
resource "aws_s3_bucket" "patch_baseline_override_bucket" {
  bucket = "patch-baseline-override-us-east-1-${var.master_account}"
}

# Patch Baseline Override S3 Bucket server side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "patch_baseline_override_bucket_encryption" {
  bucket = aws_s3_bucket.patch_baseline_override_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
    bucket_key_enabled = false
  }
}

# Patch Baseline Override S3 Bucket block public access
resource "aws_s3_bucket_public_access_block" "patch_baseline_override_bucket_block_public_access" {
  bucket = aws_s3_bucket.patch_baseline_override_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Patch Baseline Override S3 Bucket versioning
resource "aws_s3_bucket_versioning" "patch_baseline_override_bucket_versioning" {
  bucket = aws_s3_bucket.patch_baseline_override_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Patch Baseline Override S3 Bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "patch_baseline_override_bucket_lifecycle_configuration" {
  bucket = aws_s3_bucket.patch_baseline_override_bucket.id

  rule {
    id = "InventoryGlacierRule"

    expiration {
      days = 180
    }

    filter {}

    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

# Execution Logs S3 Bucket  Ownership controls
resource "aws_s3_bucket_ownership_controls" "patch_baseline_override_bucket_ownership" {
  bucket = aws_s3_bucket.patch_baseline_override_bucket.id

  rule {
    object_ownership = "ObjectWriter"
  }
}

resource "aws_s3_bucket_acl" "patch_baseline_override_bucket_acl" {
  bucket = aws_s3_bucket.patch_baseline_override_bucket.id
}

# Patch Baseline Override S3 Bucket policy
resource "aws_s3_bucket_policy" "patch_baseline_override_bucket_policy" {
  bucket = aws_s3_bucket.patch_baseline_override_bucket.id
  policy = data.aws_iam_policy_document.data_patch_baseline_override_bucket_policy.json
}

# Glue database
resource "aws_glue_catalog_database" "ssm_glue_catalog_database" {
  description = "Systems Manager Global Resource Data Sync Database"
  name = "ssm_global_resource_sync"
  catalog_id = var.master_account
}

# Glue crawler
resource "aws_glue_crawler" "ssm_glue_crawler" {
  database_name = aws_glue_catalog_database.ssm_glue_catalog_database.name
  name          = "SSM-GlueCrawler"
  description   = "Crawler for AWS Systems Manager Resource Data Sync"
  role          = aws_iam_role.ssm_glue_crawler_role.arn
  schedule      = "cron(0 8 * * ? *)"
  s3_target {
    path = "s3://${aws_s3_bucket.resource_sync_bucket.bucket}"
    exclusions = ["AWS:InstanceInformation/accountid=*/test.json"]
  }
}

# Glue crawler role
resource "aws_iam_role" "ssm_glue_crawler_role" {
  name = "SSM-GlueCrawlerRole"
  description = "Role created for Glue to access resource data sync S3 bucket"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "glue.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
  path = "/service-role/"
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole", "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_role_policy" "ssm_glue_crawler_inline_policy" {
  name = "S3Actions"
  role = aws_iam_role.ssm_glue_crawler_role.id
  policy = data.aws_iam_policy_document.ssm_glue_crawler_policy.json
}

# Delete Glue Table Column Function Role
resource "aws_iam_role" "ssm_delete_glue_table_column_function_role" {
  name = "SSM-DeleteGlueTableColumnFunctionRole"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",  "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_role_policy" "ssm_delete_glue_table_column_function_inline_policy" {
  name = "GlueActions"
  role = aws_iam_role.ssm_delete_glue_table_column_function_role.id
  policy = data.aws_iam_policy_document.ssm_delete_glue_table_column_function_policy.json
}

# SSM Delete Glue Table Column Function
resource "aws_lambda_function" "ssm_delete_glue_table_column_lambda" {
  description    = "Deletes the 'resourcetype' Glue table that causes an issue when loading partitions in Athena"
  filename      = "${path.module}/PythonFunctionZippedFiles/SSM-DeleteGlueTableColumnFunction.zip"
  function_name = "SSM-DeleteGlueTableColumnFunction"
  role          =  aws_iam_role.ssm_delete_glue_table_column_function_role.arn
  handler       = "SSM-DeleteGlueTableColumnFunction.lambda_handler"
  source_code_hash = data.archive_file.ssm_delete_glue_table_column_lambda_zip.output_base64sha256

  environment {
    variables = {
      CRAWLER_NAME = "SSM-GlueCrawler"
      DATABASE_NAME = "ssm_global_resource_sync"
    }
  } 

  runtime = "python3.8"
  memory_size = 128
  timeout = 600
}

# SSM Delete Glue Table Column Function schedule
resource "aws_cloudwatch_event_rule" "ssm_delete_glue_table_column_schedule" {
  name        = "SSM-DeleteGlueTableColumn"
  description = "Deletes resourcetype from Glue table"
  event_pattern = jsonencode({
    "source": ["aws.glue"],
    detail-type = [
      "Glue Crawler State Change"
    ],
    "detail": {
      "state" = [ 
         "Succeeded"
      ]
    }
  })
  is_enabled = true
}

# SSM Delete Glue Table Column Function schedule target
resource "aws_cloudwatch_event_target" "ssm_delete_glue_table_column_target" {
  rule      = aws_cloudwatch_event_rule.ssm_delete_glue_table_column_schedule.name
  target_id = "TargetFunctionV1"
  arn       = aws_lambda_function.ssm_delete_glue_table_column_lambda.arn
}

# SSM Delete Glue Table Column lambda schedule permission
resource "aws_lambda_permission" "ssm_delete_glue_table_column_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ssm_delete_glue_table_column_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ssm_delete_glue_table_column_schedule.arn
}

# Master InventoryGlue crawler
resource "aws_glue_crawler" "master_inventory_glue_crawler" {
  database_name = aws_glue_catalog_database.ssm_glue_catalog_database.name
  name          = "Master-Inventory-GlueCrawler"
  description   = "Crawler for Master Inventory"
  role          = "service-role/Master-Inventory-GlueCrawlerRole"
  schedule      = "cron(0 8 * * ? *)"
  s3_target {
    path = "s3://${aws_s3_bucket.ec2_inventory_bucket.bucket}"
  }
  configuration = jsonencode(
    {
      CrawlerOutput = {
        Partitions = { AddOrUpdateBehavior = "InheritFromTable" }
        Tables = { AddOrUpdateBehavior = "MergeNewColumns" }
      }
      Version = 1
    }
  )
}

# Master InventoryGlue crawler Role
resource "aws_iam_role" "master_inventory_glue_crawler_role" {
  name = "Master-Inventory-GlueCrawlerRole"
  description = "Role created for Glue to access master inventory S3 bucket"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "glue.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
  path = "/service-role/"
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole", "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_role_policy" "master_inventory_glue_crawler_inline_policy" {
  name = "S3Actions"
  role = aws_iam_role.master_inventory_glue_crawler_role.id
  policy = data.aws_iam_policy_document.master_inventory_glue_crawler_policy.json
}

# SNS Patch reporting encryption key
resource "aws_kms_key" "sns_patch_reporting_encryption_key" {
  is_enabled = true
  enable_key_rotation = true
  description = "Key used to encrypt SNS inventory topic"
}

# SNS Patch reporting encryption key policy
resource "aws_kms_key_policy" "sns_patch_reporting_encryption_key_policy" {
  key_id = aws_kms_key.sns_patch_reporting_encryption_key.id
  policy = jsonencode({
    "Version": "2012-10-17",
    "Id": "AccountPolicy",
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${var.master_account}:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        },
        {
            "Sid": "Allow use of the key by service roles within the organization",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "kms:DescribeKey",
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey",
                "kms:GenerateDataKeyWithoutPlaintext"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:PrincipalOrgID": var.org_id
                }
            }
        }
    ]
  })
}

# SNS Patch reporting encryption key alias
resource "aws_kms_alias" "sns_patch_reporting_encryption_key_alias" {
  name          = "alias/SNSPatchReportingEncryptionKey"
  target_key_id = aws_kms_key.sns_patch_reporting_encryption_key.key_id
}

# Patching reprot sns topic
resource "aws_sns_topic" "patching_report_sns_topic" {
  name = var.patching_report_sns_topic_name
  kms_master_key_id = aws_kms_alias.sns_patch_reporting_encryption_key_alias.id
}

# Patching reprot sns topic subscription
resource "aws_sns_topic_subscription" "patching_report_sns_topic_subscription_1" {
  topic_arn = aws_sns_topic.patching_report_sns_topic.arn
  protocol  = "email"
  endpoint  = var.subscription_email_1
}

# # Patching reprot sns topic subscription
# resource "aws_sns_topic_subscription" "patching_report_sns_topic_subscription_2" {
#   topic_arn = aws_sns_topic.patching_report_sns_topic.arn
#   protocol  = "email"
#   endpoint  = var.subscription_email_2
# }

# Patching reprot sns topic subscription
resource "aws_sns_topic_subscription" "patching_report_sns_topic_subscription_3" {
  topic_arn = aws_sns_topic.patching_report_sns_topic.arn
  protocol  = "email"
  endpoint  = var.subscription_email_3
  count     = var.env_type == "prod" ? 0 : 0
}
  
# Patching report Function
resource "aws_lambda_function" "patching_report_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_patch_report_monthly.zip"
  function_name = "platform_patch_report_monthly"
  role          =  var.role_arn
  handler       = "platform_patch_report_monthly.lambda_handler"
  source_code_hash = data.archive_file.patching_report_lambda_zip.output_base64sha256

  environment {
    variables = {
      DATABASE = aws_glue_catalog_database.ssm_glue_catalog_database.name
      OUTPUTBUCKET = aws_s3_bucket.patching_report_bucket.bucket
      TOPICARN = aws_sns_topic.patching_report_sns_topic.arn
      QUERYMANAGED = aws_athena_named_query.managed_inventory_athena_query.id                                       
      QUERYNONMANAGED = aws_athena_named_query.non_managed_inventory_athena_query.id                         
      QUERYMASTER = aws_athena_named_query.master_inventory_athena_query.id
      QUERYCONSOLIDATED = aws_athena_named_query.consolidated_patch_compliance_athena_query.id
    }
  } 

  runtime = "python3.8"
  memory_size = 128
  timeout = 300
}

# Patching report schedule
resource "aws_cloudwatch_event_rule" "patching_report_schedule" {
  name        = var.platform_patch_report_monthly_event_rule_name
  description = "Monthly schdule for instances patching complaince report"
  schedule_expression = "cron(0 9 14,27 * ? *)"
  is_enabled = true
}

# Patching report schedule target
resource "aws_cloudwatch_event_target" "patching_report_target" {
  rule      = aws_cloudwatch_event_rule.patching_report_schedule.name
  target_id = "IdEventRule"
  arn       = aws_lambda_function.patching_report_lambda.arn
}

# Patching report lambda schedule permission
resource "aws_lambda_permission" "patching_report_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.patching_report_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.patching_report_schedule.arn
}

# Patching report S3 Bucket
resource "aws_s3_bucket" "patching_report_bucket" {
  bucket = "patching-report-us-east-1-${var.master_account}"
}

# Patching report S3 Bucket server side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "patching_report_bucket_encryption" {
  bucket = aws_s3_bucket.patching_report_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.patching_managed_instance_encryption_key.key_id
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = false
  }
}

# Patching report S3 Bucket block public access
resource "aws_s3_bucket_public_access_block" "patching_report_bucket_block_public_access" {
  bucket = aws_s3_bucket.patching_report_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Patching report S3 Bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "patching_report_bucket_lifecycle_configuration" {
  bucket = aws_s3_bucket.patching_report_bucket.id

  rule {
    id = "AthenaGlacierRule"

    expiration {
      days = 180
    }

    filter {}

    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

# Patching report S3 Bucket  Ownership controls
resource "aws_s3_bucket_ownership_controls" "patching_report_bucket_ownership" {
  bucket = aws_s3_bucket.patching_report_bucket.id

  rule {
    object_ownership = "ObjectWriter"
  }
}

resource "aws_s3_bucket_acl" "patching_report_bucket_acl" {
  bucket = aws_s3_bucket.patching_report_bucket.id
}

# Patching report S3 Bucket policy
resource "aws_s3_bucket_policy" "patching_report_bucket_policy" {
  bucket = aws_s3_bucket.patching_report_bucket.id
  policy = data.aws_iam_policy_document.data_patching_report_bucket_policy.json
}

# Athena Query S3 Bucket
resource "aws_s3_bucket" "athena_query_bucket" {
  bucket = "ssm-res-sync-athena-query-results-us-east-1-${var.master_account}"
}

# Athena Query S3 Bucket server side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "athena_query_bucket_encryption" {
  bucket = aws_s3_bucket.athena_query_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.patching_managed_instance_encryption_key.key_id
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = false
  }
}

# Athena Query S3 Bucket block public access
resource "aws_s3_bucket_public_access_block" "athena_query_bucket_block_public_access" {
  bucket = aws_s3_bucket.athena_query_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Athena Query S3 Bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "athena_query_bucket_lifecycle_configuration" {
  bucket = aws_s3_bucket.athena_query_bucket.id

  rule {
    id = "AthenaGlacierRule"

    expiration {
      days = 180
    }

    filter {}

    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

# Athena Query S3 Bucket  Ownership controls
resource "aws_s3_bucket_ownership_controls" "athena_query_bucket_ownership" {
  bucket = aws_s3_bucket.athena_query_bucket.id

  rule {
    object_ownership = "ObjectWriter"
  }
}

resource "aws_s3_bucket_acl" "athena_query_bucket_acl" {
  bucket = aws_s3_bucket.athena_query_bucket.id
}

# Athena query for Non Compliant Patch
resource "aws_athena_named_query" "non_compliant_patch_athena_query" {
  name      = "QueryNonCompliantPatch"
  description = "Example query to list managed instances that are non-compliant for patching."
  database  = "${aws_s3_bucket.resource_sync_bucket.bucket}-database"
  query     = "SELECT \n  * \nFROM \n  aws_complianceitem \nWHERE \n  status='NON_COMPLIANT' AND compliancetype='Patch' \nLIMIT 20\n"
}

# Athena query for Non Compliant Patch
resource "aws_athena_named_query" "ssm_agent_version_athena_query" {
  name      = "QuerySSMAgentVersion"
  description = "Example query to list SSM Agent versions installed on managed instances."
  database  = "${aws_s3_bucket.resource_sync_bucket.bucket}-database"
  query     = "SELECT\n  *\nFROM\n  aws_application \nWHERE \n  name='Amazon SSM Agent' OR name='amazon-ssm-agent' \nLIMIT 20;\n"
}

# Athena query for Instance list
resource "aws_athena_named_query" "instance_list_athena_query" {
  name      = "QueryInstanceList"
  description = "Example query to return a list of non-terminated instances."
  database  = "${aws_s3_bucket.resource_sync_bucket.bucket}-database"
  query     = "SELECT \n  * \nFROM \n  aws_instanceinformation \nWHERE \n  instancestatus IS NULL;\n"
}

# Athena query for Instance applications
resource "aws_athena_named_query" "instance_applications_athena_query" {
  name      = "QueryInstanceApplications"
  description = "Example query to return a list of non-terminated instances and their applications installed."
  database  = "${aws_s3_bucket.resource_sync_bucket.bucket}-database"
  query     = "SELECT\n  name,applicationtype,publisher,version,instanceid\nFROM\n  aws_application, aws_instanceinformation\nWHERE\n  aws_instanceinformation.instancestatus IS NULL;\n"
}

# Athena query for Master inventory
resource "aws_athena_named_query" "master_inventory_athena_query" {
  name      = "QueryMasterInventory"
  description = "Example query to list all instances in the organisation."
  database  = "${aws_s3_bucket.resource_sync_bucket.bucket}-database"
  query     = "SELECT \n  ec2_inventory_bucket_us_east_1_${var.master_account}.account_id, account_bucket_us_east_1_${var.master_account}.ou_name, account_bucket_us_east_1_${var.master_account}.account_name, account_bucket_us_east_1_${var.master_account}.account_workload, ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id, ec2_inventory_bucket_us_east_1_${var.master_account}.instancetype, ec2_inventory_bucket_us_east_1_${var.master_account}.imageid, ec2_inventory_bucket_us_east_1_${var.master_account}.subnetid, ec2_inventory_bucket_us_east_1_${var.master_account}.vpcid, ec2_inventory_bucket_us_east_1_${var.master_account}.lastlauncheddate, ec2_inventory_bucket_us_east_1_${var.master_account}.state, ec2_inventory_bucket_us_east_1_${var.master_account}.privateipaddress, ec2_inventory_bucket_us_east_1_${var.master_account}.tags\nFROM \n  ec2_inventory_bucket_us_east_1_${var.master_account}\nINNER JOIN account_bucket_us_east_1_${var.master_account} ON ec2_inventory_bucket_us_east_1_${var.master_account}.account_id = account_bucket_us_east_1_${var.master_account}.account_id\nWHERE\n  partition_0=format_datetime (current_timestamp, 'y')\nAND\n  partition_1=format_datetime (current_timestamp, 'M')\nAND\n  partition_2=format_datetime(date_add('day',-1,current_timestamp),'d');\n"
}

# Athena query for Non Managed inventory
resource "aws_athena_named_query" "non_managed_inventory_athena_query" {
  name      = "QueryNonManagedInventory"
  description = "Example query to list all non managed instances in organisation."
  database  = "${aws_s3_bucket.resource_sync_bucket.bucket}-database"
  query     = "SELECT \n    ec2_inventory_bucket_us_east_1_${var.master_account}.account_id, account_bucket_us_east_1_${var.master_account}.ou_name, account_bucket_us_east_1_${var.master_account}.account_name, account_bucket_us_east_1_${var.master_account}.account_workload, ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id, ec2_inventory_bucket_us_east_1_${var.master_account}.instancetype, ec2_inventory_bucket_us_east_1_${var.master_account}.imageid, ec2_inventory_bucket_us_east_1_${var.master_account}.subnetid, ec2_inventory_bucket_us_east_1_${var.master_account}.vpcid, ec2_inventory_bucket_us_east_1_${var.master_account}.lastlauncheddate, ec2_inventory_bucket_us_east_1_${var.master_account}.state, ec2_inventory_bucket_us_east_1_${var.master_account}.privateipaddress, ec2_inventory_bucket_us_east_1_${var.master_account}.tags\nFROM \n  ec2_inventory_bucket_us_east_1_${var.master_account}\nINNER JOIN account_bucket_us_east_1_${var.master_account} ON ec2_inventory_bucket_us_east_1_${var.master_account}.account_id = account_bucket_us_east_1_${var.master_account}.account_id\nWHERE \n  instance_id not in (SELECT instanceid FROM aws_instanceinformation)\nAND\n  partition_0=format_datetime (current_timestamp, 'y')\nAND\n  partition_1=format_datetime (current_timestamp, 'M')\nAND\n  partition_2=format_datetime(date_add('day',-1,current_timestamp),'d');\n"
}

# Athena query for  Managed inventory
resource "aws_athena_named_query" "managed_inventory_athena_query" {
  name      = "ManagedInstanceInventory"
  description = "Query to extract Managed instance inventory across all the child accounts along with the compliance status and platform_install_patch tag information"
  database  = "${aws_s3_bucket.resource_sync_bucket.bucket}-database"
  query     = "SELECT \n  aws_complianceitem.resourceid, aws_complianceitem.status, aws_complianceitem.compliancetype, aws_complianceitem.classification, aws_complianceitem.id, aws_complianceitem.patchstate, aws_complianceitem.accountid, account_bucket_us_east_1_${var.master_account}.account_workload, aws_complianceitem.region, aws_complianceitem.installedtime, aws_complianceitem.capturetime, aws_tag.key, aws_tag.value, aws_instanceinformation.platformname, aws_instanceinformation.ipaddress, aws_instanceinformation.platformtype, aws_instanceinformation.instancestatus\nFROM \n  aws_complianceitem\nINNER JOIN aws_tag ON aws_complianceitem.resourceid = aws_tag.resourceid\nINNER JOIN aws_instanceinformation ON aws_instanceinformation.resourceid = aws_complianceitem.resourceid\nRIGHT JOIN account_bucket_us_east_1_${var.master_account} ON cast(account_bucket_us_east_1_${var.master_account}.account_id as varchar) = aws_complianceitem.accountid\nWHERE compliancetype='Patch' AND key= 'platform_install_patch' AND aws_instanceinformation.instancestatus != 'Terminated' AND aws_complianceitem.patchstate != 'NotApplicable'\n"
}

# Athena query for Inventory Compliance Quicksight
resource "aws_athena_named_query" "inventory_compliance_quicksight_athena_query" {
  name      = "InventoryComplianceQuicksight"
  description = "Query to extract compliance status for quicksight dashboard"
  database  = "${aws_s3_bucket.resource_sync_bucket.bucket}-database"
  query     = "CREATE OR REPLACE VIEW patch_table as\nSELECT\n  aws_compliancesummary.resourceid, aws_compliancesummary.status, aws_compliancesummary.compliancetype,aws_compliancesummary.accountid, aws_compliancesummary.region,aws_tag.key, aws_tag.value, aws_instanceinformation.platformname, aws_instanceinformation.ipaddress, aws_instanceinformation.platformtype, aws_instanceinformation.instancestatus, aws_compliancesummary.executiontime\nFROM\n  aws_compliancesummary\nINNER JOIN aws_tag ON aws_compliancesummary.resourceid = aws_tag.resourceid\nINNER JOIN aws_instanceinformation ON aws_instanceinformation.resourceid = aws_compliancesummary.resourceid\nWHERE compliancetype='Patch' AND key= 'platform_install_patch'\n"
}

# Athena query for Master Inventory Quicksight
resource "aws_athena_named_query" "master_inventory_quicksight_athena_query" {
  name      = "MasterInventoryQuicksight"
  description = "Query to extract master inventory for quicksight dashboard"
  database  = "${aws_s3_bucket.resource_sync_bucket.bucket}-database"
  query     = "CREATE OR REPLACE VIEW Master_Inventory as            \nSELECT \n  * \nFROM \n  ec2_inventory_bucket_us_east_1_${var.master_account}\nWHERE \n  partition_0=format_datetime (current_timestamp, 'y')\nAND\n  partition_1=format_datetime (current_timestamp, 'M')\nAND\n  partition_2=format_datetime(date_add('day',-1,current_timestamp),'d');\n"
}

# Athena query for Consolidated Patch Compliance
resource "aws_athena_named_query" "consolidated_patch_compliance_athena_query" {
  name      = "ConsolidatedPatchCompliance"
  description = "Query to extract consolidated patch report"
  database  = "${aws_s3_bucket.resource_sync_bucket.bucket}-database"
  query     = "SELECT DISTINCT \n  aws_compliancesummary.resourceid, aws_compliancesummary.status, aws_compliancesummary.accountid, account_bucket_us_east_1_${var.master_account}.account_workload,account_bucket_us_east_1_${var.master_account}.account_name, aws_tag.value as account_owner, aws_compliancesummary.region, aws_compliancesummary.capturetime, aws_instanceinformation.platformname, aws_instanceinformation.ipaddress, aws_instanceinformation.platformtype, aws_instanceinformation.instancestatus, ec2_inventory_bucket_us_east_1_${var.master_account}.imageid\nFROM \n  aws_compliancesummary\nINNER JOIN aws_tag ON aws_compliancesummary.resourceid = aws_tag.resourceid\nINNER JOIN aws_instanceinformation ON aws_instanceinformation.resourceid = aws_compliancesummary.resourceid\nRIGHT JOIN account_bucket_us_east_1_${var.master_account} ON cast(account_bucket_us_east_1_${var.master_account}.account_id as varchar) = aws_compliancesummary.accountid\nRIGHT JOIN ec2_inventory_bucket_us_east_1_${var.master_account} ON ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id=aws_compliancesummary.resourceid\nWHERE compliancetype='Patch' AND key= 'platform_Custodian' AND aws_instanceinformation.instancestatus != 'Terminated';\n"
}

# EC2 Inventory encryption key
resource "aws_kms_key" "ec2_inventory_encryption_key" {
  is_enabled = true
  enable_key_rotation = true
  description = "Key used to encrypt ec2 inventory data"
}

# EC2 Inventory encryption key policy
resource "aws_kms_key_policy" "ec2_inventory_encryption_key_policy" {
  key_id = aws_kms_key.ec2_inventory_encryption_key.id
  bypass_policy_lockout_safety_check = false
  policy = data.aws_iam_policy_document.data_ec2_inventory_encryption_key_policy.json
}

# EC2 Inventory encryption key alias
resource "aws_kms_alias" "ec2_inventory_encryption_key_alias" {
  name          = "alias/EC2InventoryEncryptionKey"
  target_key_id = aws_kms_key.ec2_inventory_encryption_key.key_id
}

# EC2 Inventory S3 Bucket
resource "aws_s3_bucket" "ec2_inventory_bucket" {
  bucket = "ec2-inventory-bucket-us-east-1-${var.master_account}"
}

# EC2 Inventory S3 Bucket server side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "ec2_inventory_bucket_encryption" {
  bucket = aws_s3_bucket.ec2_inventory_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.ec2_inventory_encryption_key.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

# EC2 Inventory S3 Bucket block public access
resource "aws_s3_bucket_public_access_block" "ec2_inventory_bucket_block_public_access" {
  bucket = aws_s3_bucket.ec2_inventory_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# EC2 Inventory S3 Bucket versioning
resource "aws_s3_bucket_versioning" "ec2_inventory_bucket_versioning" {
  bucket = aws_s3_bucket.ec2_inventory_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# EC2 Inventory S3 Bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "ec2_inventory_bucket_lifecycle_configuration" {
  bucket = aws_s3_bucket.ec2_inventory_bucket.id

  rule {
    id = "InventoryGlacierRule"

    expiration {
      days = 180
    }

    filter {}

    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

# EC2 Inventory S3 Bucket  Ownership controls
resource "aws_s3_bucket_ownership_controls" "ec2_inventory_bucket_ownership" {
  bucket = aws_s3_bucket.ec2_inventory_bucket.id

  rule {
    object_ownership = "ObjectWriter"
  }
}

resource "aws_s3_bucket_acl" "ec2_inventory_bucket_acl" {
  bucket = aws_s3_bucket.ec2_inventory_bucket.id
}

# EC2 Inventory bucket name ssm parameter
resource "aws_ssm_parameter" "ec2_inventory_bucket_name_ssm_parameter" {
  name  = "platform_ec2_inventory_bucket_name"
  type  = "String"
  value = aws_s3_bucket.ec2_inventory_bucket.bucket
}

# EC2 Inventory Secondary Function
resource "aws_lambda_function" "ec2_inventory_secondary_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_ec2_inventory_secondary.zip"
  function_name = "platform_ec2_inventory_secondary"
  role          =  var.role_arn
  handler       = "platform_ec2_inventory_secondary.lambda_handler"
  source_code_hash = data.archive_file.ec2_inventory_secondary_lambda_zip.output_base64sha256

  environment {
    variables = {
      INVENTORY_BUCKET_SSM_NAME = aws_ssm_parameter.ec2_inventory_bucket_name_ssm_parameter.name
    }
  } 

  runtime = "python3.8"
  memory_size = 128
  timeout = 900
}

# EC2 Inventory Main Function
resource "aws_lambda_function" "ec2_inventory_main_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_ec2_inventory_main.zip"
  function_name = "platform_ec2_inventory_main"
  role          =  var.role_arn
  handler       = "platform_ec2_inventory_main.lambda_handler"
  source_code_hash = data.archive_file.ec2_inventory_main_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  depends_on = [
    aws_lambda_function.ec2_inventory_secondary_lambda
 ]
}

# Master Inventory Report Statemachine
resource "aws_sfn_state_machine" "master_inventory_state_machine" {
  name     = "platform_MasterInventoryReportmachine"
  role_arn = var.role_arn

  definition = data.template_file.master_inventory_state_machine_template.rendered
}

# EC2 Inventory schedule
resource "aws_cloudwatch_event_rule" "ec2_inventory_schedule" {
  name = var.master_inventory_state_machine_event_rule_name
  description = "If any new Instances are launch, it will trigger lambda and gather all inventory details and store it into s3 "
  is_enabled = true
  schedule_expression = "cron(0 6 * * ? *)"
  depends_on = [
    aws_lambda_function.ec2_inventory_main_lambda
 ]
}

# EC2 Inventory schedule target
resource "aws_cloudwatch_event_target" "ec2_inventory_schedule_target" {
  rule      = aws_cloudwatch_event_rule.ec2_inventory_schedule.name
  target_id = "MasterInventorySchedule"
  arn       = aws_sfn_state_machine.master_inventory_state_machine.arn
  role_arn = var.role_arn
}

# Accounts Details S3 Bucket
resource "aws_s3_bucket" "account_details_bucket" {
  bucket = "account-bucket-us-east-1-${var.master_account}"
}

# Accounts Details S3 Bucket server side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "account_details_bucket_encryption" {
  bucket = aws_s3_bucket.account_details_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.ec2_inventory_encryption_key.key_id
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = false
  }
}

# Accounts Details S3 Bucket block public access
resource "aws_s3_bucket_public_access_block" "account_details_bucket_block_public_access" {
  bucket = aws_s3_bucket.account_details_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Accounts Details S3 Bucket versioning
resource "aws_s3_bucket_versioning" "account_details_bucket_versioning" {
  bucket = aws_s3_bucket.account_details_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Accounts Details S3 Bucket  Ownership controls
resource "aws_s3_bucket_ownership_controls" "account_details_bucket_ownership" {
  bucket = aws_s3_bucket.account_details_bucket.id

  rule {
    object_ownership = "ObjectWriter"
  }
}

resource "aws_s3_bucket_acl" "account_details_bucket_acl" {
  bucket = aws_s3_bucket.account_details_bucket.id
}

# Account details Function
resource "aws_lambda_function" "account_details_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_accounts_details.zip"
  function_name = "platform_accounts_details"
  role          =  var.role_arn
  handler       = "platform_accounts_details.lambda_handler"
  source_code_hash = data.archive_file.account_details_lambda_zip.output_base64sha256

  environment {
    variables = {
      ACCOUNTS_DETAILS_BUCKET_NAME = aws_s3_bucket.account_details_bucket.bucket
    }
  } 

  runtime = "python3.8"
  memory_size = 128
  timeout = 900
}

# Account details Function schedule
resource "aws_cloudwatch_event_rule" "account_details_schedule" {
  name = var.account_details_event_rule_name
  description = "Monthly schedule for accounts details"
  schedule_expression = "cron(0 6 * * ? *)"
  is_enabled = true
}

# Account details Function schedule target
resource "aws_cloudwatch_event_target" "account_details_target" {
  rule      = aws_cloudwatch_event_rule.account_details_schedule.name
  target_id = "IdEventRule"
  arn       = aws_lambda_function.account_details_lambda.arn
}

# Account details lambda schedule permission
resource "aws_lambda_permission" "account_details_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.account_details_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.account_details_schedule.arn
}

# Account details Glue crawler
resource "aws_glue_crawler" "account_details_glue_crawler" {
  database_name = aws_glue_catalog_database.ssm_glue_catalog_database.name
  description = "Crawler for Accounts Details"
  name          = "Accounts-Details-GlueCrawler"
  role          = aws_iam_role.account_details_glue_crawler_role.arn
  schedule      = "cron(0 8 * * ? *)"
  s3_target {
    path = "s3://${aws_s3_bucket.account_details_bucket.bucket}"
  }
  configuration = jsonencode(
    {
      CrawlerOutput = {
        Partitions = { AddOrUpdateBehavior = "InheritFromTable" }
        Tables = { AddOrUpdateBehavior = "MergeNewColumns" }
      }
      Version = 1
    }
  )
}

# Account details Glue crawler role
resource "aws_iam_role" "account_details_glue_crawler_role" {
  name = "Accounts-Details-GlueCrawlerRole"
  description = "Role created for Glue to access Accounts Details S3 bucket"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "glue.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
  path = "/service-role/"
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole", "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_role_policy" "account_details_glue_crawler_inline_policy" {
  name = "S3Actions"
  role = aws_iam_role.account_details_glue_crawler_role.id
  policy = data.aws_iam_policy_document.account_details_glue_crawler_policy.json
}

# Athena query for Account details
resource "aws_athena_named_query" "account_details_athena_query" {
  name      = "AccountsDetails"
  description = "Query to extract accounts details"
  database  = aws_glue_catalog_database.ssm_glue_catalog_database.name
  query   = "SELECT \n  *\nFROM \n  accounts_details\n"
}

# Maintenace Window Deletion Function
resource "aws_lambda_function" "maintenance_window_deletion_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_delete_maintenance_windows.zip"
  function_name = "platform_delete_maintenance_windows"
  role          =  var.role_arn
  handler       = "platform_delete_maintenance_windows.lambda_handler"
  source_code_hash = data.archive_file.maintenance_window_deletion_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900
}

# Maintenace Window Deletion  Statemachine
resource "aws_sfn_state_machine" "maintenance_window_deletion_state_machine" {
  name     = "platform_MaintenaceWindowDeletionStateMachine"
  role_arn = var.role_arn

  definition = data.template_file.maintenance_window_deletion_state_machine_template.rendered
}

#SSM Compliance Athena Query for QuickSight Dashboard
resource "aws_athena_named_query" "quick_sight_ssm_compliance_athena_query" {
  name      = "QuickSightSSMCompliance"
  description = "Query to extract SSM compliance report"
  database  = "${aws_s3_bucket.resource_sync_bucket.bucket}-database"
  query   = "CREATE OR REPLACE VIEW \"ssm_quicksight_dashboard\" AS\nSELECT DISTINCT ec2_inventory_bucket_us_east_1_${var.master_account}.ouname OU_NAME,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.account_name ACCOUNT_NAME,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.account_id ACCOUNT_ID,\n  aws_instanceinformation.region AWS_REGION,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id INSTANCE_ID,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.state INSTANCE_STATE,\n  aws_instanceinformation.instancestatus SSM_CONNECTIVITY,\n  (\n    CASE\n      WHEN (aws_instanceinformation.resourcetype \u003c\u003e '') THEN 'Managed-Instance' ELSE 'Non-Managed-Instance'\n    END\n  ) SSM_Status,\n  aws_instanceinformation.platformname PLATFORM_NAME,\n  aws_instanceinformation.platformtype PLATFORM_TYPE,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_0 YEAR,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_1 MONTH,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_2 DATE\nFROM (\n    ec2_inventory_bucket_us_east_1_${var.master_account}\n    LEFT JOIN aws_instanceinformation ON (\n      ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = aws_instanceinformation.instanceid\n    )\n  )\n"
}

#Patch Compliance Athena Query for QuickSight Dashboard
resource "aws_athena_named_query" "quick_sight_patch_compliance_athena_query" {
  name      = "QuickSightPatchCompliance"
  description = "Query to extract Patch compliance report"
  database  = "${aws_s3_bucket.resource_sync_bucket.bucket}-database"
  query   = "CREATE OR REPLACE VIEW \"patch_quicksight_dashboard\" AS\nSELECT DISTINCT ec2_inventory_bucket_us_east_1_${var.master_account}.ouname OU_NAME,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.account_name ACCOUNT_NAME,\n  aws_compliancesummary.accountid ACCOUNT_ID,\n  aws_compliancesummary.region AWS_REGION,\n  aws_compliancesummary.resourceid INSTANCE_ID,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.state INSTANCE_STATE,\n  aws_instanceinformation.platformname PLATFORM_NAME,\n  aws_instanceinformation.platformtype PLATFORM_TYPE,\n  aws_compliancesummary.status PATCH_STATUS,\n  aws_compliancesummary.patchgroup PATCH_GROUP,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_0 YEAR,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_1 MONTH,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_2 DATE\nFROM (\n    (\n      ec2_inventory_bucket_us_east_1_${var.master_account}\n      LEFT JOIN aws_compliancesummary ON (\n        ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = aws_compliancesummary.resourceid\n      )\n    )\n    LEFT JOIN aws_instanceinformation ON (\n      ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = aws_instanceinformation.instanceid\n    )\n  )\nWHERE (aws_compliancesummary.compliancetype = 'Patch')\n"
}

#AD Instances Compliance Athena Query for QuickSight Dashboard
resource "aws_athena_named_query" "quick_sight_ad_compliance_athena_query" {
  name      = "QuickSightADCompliance"
  description = "Query to extract AD instances compliance report"
  database  = "${aws_s3_bucket.resource_sync_bucket.bucket}-database"
  query   = "CREATE OR REPLACE VIEW \"ad_compliance_dashboard\" AS WITH T1 AS (\n    SELECT DISTINCT resourceid\n    FROM \"ssm_global_resource_sync\".\"aws_instanceinformation\"\n  ),\n  T2 AS (\n    SELECT DISTINCT resourceid\n    FROM \"ssm_global_resource_sync\".\"aws_instanceinformation\"\n    WHERE (\n        \"upper\"(computername) LIKE '%SHELL.COM%'\n        OR \"upper\"(computername) LIKE '%SHELL-CLOUD.COM%'\n    )\n  )\nSELECT DISTINCT ec2_inventory_bucket_us_east_1_${var.master_account}.ouname OU_NAME,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.account_name ACCOUNT_NAME,\n  aws_instanceinformation.accountid ACCOUNT_ID,\n  aws_instanceinformation.region AWS_REGION,\n  aws_instanceinformation.resourceid INSTANCE_ID,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.state INSTANCE_STATE,\n  aws_instanceinformation.instancestatus SSM_AGENT_STATUS,\n  aws_instanceinformation.computername HOST_NAME,\n  (\n    CASE\n      WHEN (T2.resourceid IS NULL) THEN 'Non-AD-Instance' ELSE 'AD-Instance'\n    END\n  ) AD_STATUS,\n  aws_instanceinformation.platformname PLATFORM_NAME,\n  aws_instanceinformation.platformtype PLATFORM_TYPE,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_0 YEAR,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_1 MONTH,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_2 DATE\nFROM (\n      (\n        (\n          ec2_inventory_bucket_us_east_1_${var.master_account}\n          LEFT JOIN aws_instanceinformation ON (\n            ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = aws_instanceinformation.instanceid\n          )\n        )\n        LEFT JOIN T1 ON (\n          ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = T1.resourceid\n        )\n      )\n      LEFT JOIN T2 ON (\n        ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = T2.resourceid\n      )\n    )\n"
}

#Falcon Compliance Athena Query for QuickSight Dashboard
resource "aws_athena_named_query" "quick_sight_falcon_compliance_athena_query" {
  name      = "QuickSightFalconCompliance"
  description = "Query to extract Falcon compliance report"
  database  = "${aws_s3_bucket.resource_sync_bucket.bucket}-database"
  query   = "CREATE OR REPLACE VIEW \"falcon_compliance_dashboard\" AS WITH T1 AS (\n    SELECT DISTINCT resourceid\n    FROM \"ssm_global_resource_sync\".\"aws_application\"\n  ),\n  T2 AS (\n    SELECT DISTINCT resourceid\n    FROM \"ssm_global_resource_sync\".\"aws_application\"\n    WHERE (packageid LIKE '%falcon%')\n  )\nSELECT DISTINCT ec2_inventory_bucket_us_east_1_${var.master_account}.ouname OU_NAME,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.account_name ACCOUNT_NAME,\n  aws_application.accountid ACCOUNT_ID,\n  aws_application.region AWS_REGION,\n  aws_application.resourceid INSTANCE_ID,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.state INSTANCE_STATE,\n  (\n    CASE\n      WHEN (T2.resourceid IS NULL) THEN 'Non-Falcon-Instance' ELSE 'Falcon-Instance'\n    END\n  ) FALCON_STATUS,\n  aws_instanceinformation.platformname PLATFORM_NAME,\n  aws_instanceinformation.platformtype PLATFORM_TYPE,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_0 YEAR,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_1 MONTH,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_2 DATE\nFROM (\n    (\n      (\n        (\n          ec2_inventory_bucket_us_east_1_${var.master_account}\n          LEFT JOIN aws_application ON (\n            ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = aws_application.resourceid\n          )\n        )\n        LEFT JOIN aws_instanceinformation ON (\n          ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = aws_instanceinformation.instanceid\n        )\n      )\n      LEFT JOIN T1 ON (\n        ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = T1.resourceid\n      )\n    )\n    LEFT JOIN T2 ON (\n      ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = T2.resourceid\n    )\n  )\n"
}

#Flexera Compliance Athena Query for QuickSight Dashboard
resource "aws_athena_named_query" "quick_sight_flexera_compliance_athena_query" {
  name      = "QuickSightFlexeraCompliance"
  description = "Query to extract Flexera compliance report"
  database  = "${aws_s3_bucket.resource_sync_bucket.bucket}-database"
  query   = "CREATE OR REPLACE VIEW \"flexera_compliance_dashboard\" AS WITH T1 AS (\n    SELECT DISTINCT resourceid\n    FROM \"ssm_global_resource_sync\".\"aws_application\"\n  ),\n  T2 AS (\n    SELECT DISTINCT resourceid\n    FROM \"ssm_global_resource_sync\".\"aws_application\"\n    WHERE (publisher = 'Flexera Software LLC')\n  )\nSELECT DISTINCT ec2_inventory_bucket_us_east_1_${var.master_account}.ouname OU_NAME,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.account_name ACCOUNT_NAME,\n  aws_application.accountid ACCOUNT_ID,\n  aws_application.region AWS_REGION,\n  aws_application.resourceid INSTANCE_ID,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.state INSTANCE_STATE,\n  (\n    CASE\n      WHEN (T2.resourceid IS NULL) THEN 'Non-Flexera-Instance' ELSE 'Flexera-Instance'\n    END\n  ) FLEXERA_STATUS,\n  aws_instanceinformation.platformname PLATFORM_NAME,\n  aws_instanceinformation.platformtype PLATFORM_TYPE,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_0 YEAR,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_1 MONTH,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_2 DATE\nFROM (\n      (\n        (\n          (\n            ec2_inventory_bucket_us_east_1_${var.master_account}\n            LEFT JOIN aws_application ON (\n              ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = aws_application.resourceid\n            )\n          )\n          LEFT JOIN aws_instanceinformation ON (\n            ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = aws_instanceinformation.instanceid\n          )\n        )\n        LEFT JOIN T1 ON (\n          ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = T1.resourceid\n        )\n      )\n      LEFT JOIN T2 ON (\n        ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = T2.resourceid\n      )\n    )\n"
}

resource "aws_lambda_function" "report_patch_compliance_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_report_patch_compliance_monthly.zip"
  function_name = "platform_report_patch_compliance_monthly"
  role          =  var.role_arn
  handler       = "platform_report_patch_compliance_monthly.lambda_handler"
  source_code_hash = data.archive_file.report_patch_compliance_lambda_zip.output_base64sha256

  environment {
    variables = {
      OUTPUTBUCKET = aws_s3_bucket.patching_report_bucket.bucket
    }
  } 

  runtime = "python3.8"
  memory_size = 10000
  timeout = 900
}

# Patching report schedule
resource "aws_cloudwatch_event_rule" "report_patch_compliance_schedule" {
  name        = "platform_report_patch_compliance_trigger"
  description = "Monthly schdule for instances patching complaince report"
  schedule_expression = "cron(0 11 15,28 * ? *)"
  is_enabled = true
}

# Patching report schedule target
resource "aws_cloudwatch_event_target" "report_patch_compliance_target" {
  rule      = aws_cloudwatch_event_rule.report_patch_compliance_schedule.name
  target_id = "IdEventRule"
  arn       = aws_lambda_function.report_patch_compliance_lambda.arn
}

# Patching report lambda schedule permission
resource "aws_lambda_permission" "report_patch_compliance_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.report_patch_compliance_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.report_patch_compliance_schedule.arn
}

resource "aws_athena_named_query" "falcon_insatallation_compliance_athena_query" {
  name      = "FalconInstallationCompliance"
  description = "Query to extract Falcon compliance report"
  database  = "${aws_s3_bucket.resource_sync_bucket.bucket}-database"
  query   = "WITH T1 AS (\n    SELECT DISTINCT resourceid\n    FROM \"ssm_global_resource_sync\".\"aws_application\"\n  ),\n  T2 AS (\n    SELECT DISTINCT resourceid\n    FROM \"ssm_global_resource_sync\".\"aws_application\"\n    WHERE (packageid LIKE '%falcon%')\n  )\nSELECT DISTINCT ec2_inventory_bucket_us_east_1_${var.master_account}.ouname OU_NAME,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.account_name ACCOUNT_NAME,\n  aws_application.accountid ACCOUNT_ID,\n  aws_application.region AWS_REGION,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.imageid,\n aws_application.resourceid INSTANCE_ID,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.state INSTANCE_STATE,\n  (\n    CASE\n      WHEN (T2.resourceid IS NULL) THEN 'Falcon Not Installed' ELSE 'Falcon Installed'\n    END\n  ) FALCON_STATUS,\n  aws_instanceinformation.platformname PLATFORM_NAME,\n  aws_instanceinformation.platformtype PLATFORM_TYPE,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_0 YEAR,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_1 MONTH,\n  ec2_inventory_bucket_us_east_1_${var.master_account}.partition_2 DATE\nFROM (\n    (\n      (\n        (\n          ec2_inventory_bucket_us_east_1_${var.master_account}\n          LEFT JOIN aws_application ON (\n            ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = aws_application.resourceid\n          )\n        )\n        LEFT JOIN aws_instanceinformation ON (\n          ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = aws_instanceinformation.instanceid\n        )\n      )\n      LEFT JOIN T1 ON (\n        ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = T1.resourceid\n      )\n    )\n    LEFT JOIN T2 ON (\n      ec2_inventory_bucket_us_east_1_${var.master_account}.instance_id = T2.resourceid\n    )\n  )\n WHERE ec2_inventory_bucket_us_east_1_${var.master_account}.partition_0=format_datetime(current_timestamp, 'y') AND ec2_inventory_bucket_us_east_1_${var.master_account}.partition_1=format_datetime (current_timestamp, 'M') AND ec2_inventory_bucket_us_east_1_${var.master_account}.partition_2=format_datetime(date_add('day',-1,current_timestamp),'d') AND aws_application.resourceid!=''"
}

resource "aws_lambda_function" "falcon_installation_compliance_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_falcon_installation_compliance.zip"
  function_name = "platform_falcon_installation_compliance"
  role          =  var.role_arn
  handler       = "platform_falcon_installation_compliance.lambda_handler"
  source_code_hash = data.archive_file.falcon_installation_compliance_lambda_zip.output_base64sha256
  environment {
    variables = {
      DATABASE = aws_glue_catalog_database.ssm_glue_catalog_database.name
      OUTPUTBUCKET = aws_s3_bucket.patching_report_bucket.bucket
      QUERY = aws_athena_named_query.falcon_insatallation_compliance_athena_query.id
    }
  } 

  runtime = "python3.8"
  memory_size = 2000
  timeout = 900
}

# Falcon report schedule
resource "aws_cloudwatch_event_rule" "falcon_installation_compliance_schedule" {
  name        = "platform_falcon_installation_compliance_trigger"
  description = "Monthly schdule for instances falcon complaince report"
  schedule_expression = "cron(0 11 3 * ? *)"
  is_enabled = true
}

# Falcon report schedule target
resource "aws_cloudwatch_event_target" "falcon_installation_compliance_target" {
  rule      = aws_cloudwatch_event_rule.falcon_installation_compliance_schedule.name
  target_id = "IdEventRule"
  arn       = aws_lambda_function.falcon_installation_compliance_lambda.arn
}

# Falcon report lambda schedule permission
resource "aws_lambda_permission" "falcon_installation_compliance_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.falcon_installation_compliance_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.falcon_installation_compliance_schedule.arn
}

resource "aws_lambda_function" "sqs_to_dynamodb_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_patch_sqs_to_dynamo.zip"
  function_name = "platform_patch_sqs_to_dynamo"
  role          =  var.role_arn
  handler       = "platform_patch_sqs_to_dynamo.lambda_handler"
  source_code_hash = data.archive_file.sqs_to_dynamodb_lambda_zip.output_base64sha256
  runtime = "python3.8"
  memory_size = 2000
  timeout = 900
}

resource "aws_lambda_function" "dynamo_report_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_patch_dynamo_report.zip"
  function_name = "platform_patch_dynamo_report"
  role          =  var.role_arn
  handler       = "platform_patch_dynamo_report.lambda_handler"
  source_code_hash = data.archive_file.dynamo_report_lambda_zip.output_base64sha256
  runtime = "python3.8"
  memory_size = 2000
  timeout = 900
  environment {
    variables = {
      OUTPUTBUCKET = aws_s3_bucket.patching_report_bucket.bucket
    }
  } 
}

# Falcon report schedule
resource "aws_cloudwatch_event_rule" "dynamo_report_schedule" {
  name        = "platform_dynamo_report_trigger"
  description = "Monthly schdule for instances falcon complaince report"
  schedule_expression = "cron(0 11 27 * ? *)"
  is_enabled = true
}

# Falcon report schedule target
resource "aws_cloudwatch_event_target" "dynamo_report_target" {
  rule      = aws_cloudwatch_event_rule.dynamo_report_schedule.name
  target_id = "IdEventRule"
  arn       = aws_lambda_function.dynamo_report_lambda.arn
}

# Falcon report lambda schedule permission
resource "aws_lambda_permission" "dynamo_report_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.dynamo_report_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.dynamo_report_schedule.arn
}

resource "aws_dynamodb_table" "patching_table" {
  name           = "Patch_Metadata"
  read_capacity  = 5
  write_capacity = 5

  hash_key       = "instance_id"

  point_in_time_recovery { 
    enabled = true 
  }

  attribute {
    name = "instance_id"
    type = "S"
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_sqs_queue" "patching_metadata" {
  name                      = "patching_metadata_queue"
  message_retention_seconds = 345600
  visibility_timeout_seconds = 900

  tags = {
    platform_donotdelete = "yes"
  }
}

resource "aws_lambda_event_source_mapping" "sqs_lambda_mapping" {
  batch_size  = 100
  maximum_batching_window_in_seconds = 10
  event_source_arn = aws_sqs_queue.patching_metadata.arn
  function_name    = aws_lambda_function.sqs_to_dynamodb_lambda.arn
}

resource "aws_sqs_queue_policy" "patching_metadata_policy" {
  queue_url = aws_sqs_queue.patching_metadata.id
  policy    = data.aws_iam_policy_document.patching_metadata_iam_policy.json
}
