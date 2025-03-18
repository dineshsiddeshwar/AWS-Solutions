
# Backup Jobs topic encryption key
resource "aws_kms_key" "backup_jobs_data_encryption_key" {
  description = "Key used to encrypt fasiled backups data"
  is_enabled = true
  enable_key_rotation = true
}

# Backup Jobs topic encryption key policy
resource "aws_kms_key_policy" "backup_jobs_data_encryption_key_policy" {
  key_id = aws_kms_key.backup_jobs_data_encryption_key.id
  policy = data.aws_iam_policy_document.data_backup_jobs_data_encryption_key_policy.json
  bypass_policy_lockout_safety_check =  false
}

# Backup Jobs topic encryption key alias
resource "aws_kms_alias" "backup_jobs_data_encryption_key_alias" {
  name          = "alias/BackupJobsDataEncryptionKey"
  target_key_id = aws_kms_key.backup_jobs_data_encryption_key.key_id
}

# Backup Jobs S3 Bucket
resource "aws_s3_bucket" "backup_jobs_bucket" {
  bucket = "backups-jobs-us-east-1-${var.master_account}"
}

# Failed Backup Jobs S3 Bucket
resource "aws_s3_bucket" "backup_failed_jobs_new" {
  bucket = "backup-failed-jobs-us-east-1-${var.master_account}"
}

# Backup Jobs S3 Bucket server side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "backup_jobs_bucket_encryption" {
  bucket = aws_s3_bucket.backup_jobs_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.backup_jobs_data_encryption_key.id
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = false
  }
}

# Backup Jobs S3 Bucket block public access
resource "aws_s3_bucket_public_access_block" "backup_jobs_bucket_block_public_access" {
  bucket = aws_s3_bucket.backup_jobs_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Backup Jobs S3 Bucket versioning
resource "aws_s3_bucket_versioning" "backup_jobs_bucket_versioning" {
  bucket = aws_s3_bucket.backup_jobs_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Backup Jobs S3 Bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "backup_jobs_lifecycle_configuration" {
  bucket = aws_s3_bucket.backup_jobs_bucket.id

  rule {
    id = "BackupJobsGlacierRule"

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

# Backup Jobs S3 Bucket  ACL
resource "aws_s3_bucket_acl" "backup_jobs_bucket_acl" {
  bucket = aws_s3_bucket.backup_jobs_bucket.id
}

# Backup Jobs S3 Bucket  Ownership
resource "aws_s3_bucket_ownership_controls" "backup_jobs_bucket_ownership_controls" {
  bucket = aws_s3_bucket.backup_jobs_bucket.id

  rule {
    object_ownership = "ObjectWriter"
  }
}

# Backup Jobs database
resource "aws_glue_catalog_database" "backup_jobs_glue_catalog_database" {
  name = "backups_jobs"
  catalog_id = var.master_account
  description = "Backups jobs data"
}

# Backup Jobs crawler
resource "aws_glue_crawler" "backup_jobs_glue_crawler" {
  database_name = aws_glue_catalog_database.backup_jobs_glue_catalog_database.name
  name          = "Backup-Jobs-GlueCrawler"
  description   = "Crawler for backups jobs"
  role          = aws_iam_role.backup_jobs_glue_crawler_role.arn
  schedule      = "cron(0 8 * * ? *)"
  s3_target {
    path = "s3://${aws_s3_bucket.backup_jobs_bucket.bucket}"
  }
}

# Backup Jobs role
resource "aws_iam_role" "backup_jobs_glue_crawler_role" {
  name = "Backup-Jobs-GlueCrawlerRole"
  description = "Role created for Glue to access backup jobs S3 bucket"
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

resource "aws_iam_role_policy" "backup_jobs_glue_crawler_inline_policy" {
  name = "S3Actions"
  role = aws_iam_role.backup_jobs_glue_crawler_role.id
  policy = data.aws_iam_policy_document.backup_jobs_glue_crawler_policy.json
}

# Backup jobs report lambda
resource "aws_lambda_function" "backup_jobs_report_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_backups_jobs_report.zip"
  function_name = "platform_backup_jobs_report"
  role          = var.role_arn
  handler       = "platform_backups_jobs_report.lambda_handler"
  source_code_hash = data.archive_file.backup_jobs_report_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  environment {
    variables = {
      BACKUP_JOBS_BUCKET_NAME = aws_s3_bucket.backup_jobs_bucket.bucket
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Failed Backup jobs report lambda
resource "aws_lambda_function" "failed_backup_jobs_report_lambda_new" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_failed_backup_jobs_new.zip"
  function_name = "platform_failed_backup_jobs_new"
  role          = var.role_arn
  handler       = "platform_failed_backup_jobs_new.lambda_handler"
  source_code_hash = data.archive_file.platform_failed_backup_jobs_new_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 128
  timeout = 900

  environment {
    variables = {
      bucket_name	 = aws_s3_bucket.backup_failed_jobs_new.bucket
      athena_query = "SELECT resource_type, account_id, backup_job_id, job_status, status_message, creation_date, completion_date FROM platform_backup_report_view WHERE job_status = 'FAILED' AND (resource_type = 'EC2' OR resource_type = 'EBS') AND from_iso8601_timestamp(completion_date) >= date_add('day', -2, current_timestamp)" 
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_cloudwatch_event_rule" "lambda_schedule" {
  name                = "lambda_schedule"
  schedule_expression = "cron(0 0 * * ? *)"  # This schedle to run this at everyday 12am

  tags = {
    Name = "lambda_schedule"
  }
}
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.lambda_schedule.name
  target_id = "IdEventRule"
  arn = aws_lambda_function.failed_backup_jobs_report_lambda_new.arn
}

resource "aws_lambda_permission" "backup_failed_jobs_report_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.failed_backup_jobs_report_lambda_new.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_schedule.arn
}

# Backup jobs lambda schedule
resource "aws_cloudwatch_event_rule" "backup_jobs_report_lambda_schedule" {
  name = var.backup_jobs_report_event_rule_name
  description = "Monthly schdule for backup jobs report"
  schedule_expression = "cron(0 7 * * ? *)"
  is_enabled = true
}

resource "aws_cloudwatch_event_target" "backup_jobs_report_lambda_target" {
  rule      = aws_cloudwatch_event_rule.backup_jobs_report_lambda_schedule.name
  target_id = "IdEventRule"
  arn       = aws_lambda_function.backup_jobs_report_lambda.arn
}

resource "aws_lambda_permission" "backup_jobs_report_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.backup_jobs_report_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.backup_jobs_report_lambda_schedule.arn
}

# Failed Backup Jobs S3 Bucket
resource "aws_s3_bucket" "failed_backup_jobs_bucket" {
  bucket = "failed-backups-jobs-us-east-1-${var.master_account}"
}

# Failed Backup Jobs S3 Bucket server side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "failed_backup_jobs_bucket_encryption" {
  bucket = aws_s3_bucket.failed_backup_jobs_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.backup_jobs_data_encryption_key.id
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = false
  }
}

# Failed Backup Jobs S3 Bucket block public access
resource "aws_s3_bucket_public_access_block" "failed_backup_jobs_bucket_block_public_access" {
  bucket = aws_s3_bucket.failed_backup_jobs_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Failed Backup Jobs S3 Bucket versioning
resource "aws_s3_bucket_versioning" "failed_backup_jobs_bucket_versioning" {
  bucket = aws_s3_bucket.failed_backup_jobs_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Failed Backup Jobs S3 Bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "failed_backup_jobs_lifecycle_configuration" {
  bucket = aws_s3_bucket.failed_backup_jobs_bucket.id

  rule {
    id = "BackupJobsGlacierRule"

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

# Failed Backup Jobs S3 Bucket  ACL
resource "aws_s3_bucket_acl" "failed_backup_jobs_bucket_acl" {
  bucket = aws_s3_bucket.failed_backup_jobs_bucket.id
}

# Failed Backup Jobs S3 Bucket  Ownership
resource "aws_s3_bucket_ownership_controls" "failed_backup_jobs_bucket_ownership_controls" {
  bucket = aws_s3_bucket.failed_backup_jobs_bucket.id

  rule {
    object_ownership = "ObjectWriter"
  }
}

# Failed Backup Jobs S3 Bucket policy
resource "aws_s3_bucket_policy" "failed_backup_jobs_bucket_policy" {
  bucket = aws_s3_bucket.failed_backup_jobs_bucket.id
  policy = data.aws_iam_policy_document.data_falied_backup_jobs_bucket_policy.json
}

# Backup jobs report lambda
resource "aws_lambda_function" "failed_backup_jobs_report_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_failed_backups_jobs_report.zip"
  function_name = "platform_failed_backups_jobs_report"
  role          = var.role_arn
  handler       = "platform_failed_backups_jobs_report.lambda_handler"
  source_code_hash = data.archive_file.failed_backup_jobs_report_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  environment {
    variables = {
      DATABASE = aws_glue_catalog_database.backup_jobs_glue_catalog_database.name
      OUTPUTBUCKET = aws_s3_bucket.failed_backup_jobs_bucket.bucket
      QUERY = "SELECT \n  backups_jobs.backups_jobs_us_east_1_${var.master_account}.accountid, ssm_global_resource_sync.account_bucket_us_east_1_${var.master_account}.account_name, ssm_global_resource_sync.account_bucket_us_east_1_${var.master_account}.account_workload, backups_jobs.backups_jobs_us_east_1_${var.master_account}.backupjobid, backups_jobs.backups_jobs_us_east_1_${var.master_account}.backupvaultname, backups_jobs.backups_jobs_us_east_1_${var.master_account}.backupvaultarn, backups_jobs.backups_jobs_us_east_1_${var.master_account}.resourcearn, backups_jobs.backups_jobs_us_east_1_${var.master_account}.state, backups_jobs.backups_jobs_us_east_1_${var.master_account}.createdby, backups_jobs.backups_jobs_us_east_1_${var.master_account}.resourcetype\nFROM \n  backups_jobs.backups_jobs_us_east_1_${var.master_account}\nLEFT JOIN \n  ssm_global_resource_sync.account_bucket_us_east_1_${var.master_account} ON backups_jobs.backups_jobs_us_east_1_${var.master_account}.accountid = ssm_global_resource_sync.account_bucket_us_east_1_${var.master_account}.account_id\nWHERE \n  backups_jobs.backups_jobs_us_east_1_${var.master_account}.state = 'FAILED' \nAND\n  backups_jobs.backups_jobs_us_east_1_${var.master_account}.resourcetype = 'EC2' \nAND \n  ssm_global_resource_sync.account_bucket_us_east_1_${var.master_account}.account_workload = 'BC'\nAND\n  backups_jobs.backups_jobs_us_east_1_${var.master_account}.partition_0=format_datetime (current_timestamp, 'y')\nAND\n  backups_jobs.backups_jobs_us_east_1_${var.master_account}.partition_1=format_datetime (current_timestamp, 'M')\nAND\n  backups_jobs.backups_jobs_us_east_1_${var.master_account}.partition_2=format_datetime (current_timestamp, 'd');\n"
    
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Failed Backup jobs lambda schedule
resource "aws_cloudwatch_event_rule" "failed_backup_jobs_report_lambda_schedule" {
  name = var.failed_backup_jobs_report_event_rule_name
  description = "Monthly schdule for Failed backup jobs report"
  schedule_expression = "cron(0 9 * * ? *)"
  is_enabled = true
}

resource "aws_cloudwatch_event_target" "failed_backup_jobs_report_lambda_target" {
  rule      = aws_cloudwatch_event_rule.failed_backup_jobs_report_lambda_schedule.name
  target_id = "IdEventRule"
  arn       = aws_lambda_function.failed_backup_jobs_report_lambda.arn
}

resource "aws_lambda_permission" "failed_backup_jobs_report_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.failed_backup_jobs_report_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.failed_backup_jobs_report_lambda_schedule.arn
}

# Athena query for backup jobs
resource "aws_athena_named_query" "backup_jobs_athena_query" {
  name      = "QueryBackupJobs"
  description = "Example query to list all backup jobs in organisation."
  database  = aws_glue_catalog_database.backup_jobs_glue_catalog_database.name
  query     = "SELECT \n  backups_jobs.backups_jobs_us_east_1_${var.master_account}.accountid, ssm_global_resource_sync.account_bucket_us_east_1_${var.master_account}.account_name, ssm_global_resource_sync.account_bucket_us_east_1_${var.master_account}.account_workload, backups_jobs.backups_jobs_us_east_1_${var.master_account}.backupjobid, backups_jobs.backups_jobs_us_east_1_${var.master_account}.backupvaultname, backups_jobs.backups_jobs_us_east_1_${var.master_account}.backupvaultarn, backups_jobs.backups_jobs_us_east_1_${var.master_account}.resourcearn, backups_jobs.backups_jobs_us_east_1_${var.master_account}.state, backups_jobs.backups_jobs_us_east_1_${var.master_account}.createdby, backups_jobs.backups_jobs_us_east_1_${var.master_account}.resourcetype\nFROM \n  backups_jobs.backups_jobs_us_east_1_${var.master_account}\nLEFT JOIN \n  ssm_global_resource_sync.account_bucket_us_east_1_${var.master_account} ON backups_jobs.backups_jobs_us_east_1_${var.master_account}.accountid = ssm_global_resource_sync.account_bucket_us_east_1_${var.master_account}.account_id\nWHERE\n  backups_jobs.backups_jobs_us_east_1_${var.master_account}.partition_0=format_datetime (current_timestamp, 'y')\nAND\n  backups_jobs.backups_jobs_us_east_1_${var.master_account}.partition_1=format_datetime (current_timestamp, 'M')\nAND\n  backups_jobs.backups_jobs_us_east_1_${var.master_account}.partition_2=format_datetime (current_timestamp, 'd');\n"
}

# Athena query for failed backup jobs
resource "aws_athena_named_query" "failed_backup_jobs_athena_query" {
  name      = "QueryFailedBackupJobs"
  description = "Example query to list all failed backup jobs in organisation."
  database  = aws_glue_catalog_database.backup_jobs_glue_catalog_database.name
  query     = "SELECT \n  backups_jobs.backups_jobs_us_east_1_${var.master_account}.accountid, ssm_global_resource_sync.account_bucket_us_east_1_${var.master_account}.account_name, ssm_global_resource_sync.account_bucket_us_east_1_${var.master_account}.account_workload, backups_jobs.backups_jobs_us_east_1_${var.master_account}.backupjobid, backups_jobs.backups_jobs_us_east_1_${var.master_account}.backupvaultname, backups_jobs.backups_jobs_us_east_1_${var.master_account}.backupvaultarn, backups_jobs.backups_jobs_us_east_1_${var.master_account}.resourcearn, backups_jobs.backups_jobs_us_east_1_${var.master_account}.state, backups_jobs.backups_jobs_us_east_1_${var.master_account}.createdby, backups_jobs.backups_jobs_us_east_1_${var.master_account}.resourcetype\nFROM \n  backups_jobs.backups_jobs_us_east_1_${var.master_account}\nLEFT JOIN \n  ssm_global_resource_sync.account_bucket_us_east_1_${var.master_account} ON backups_jobs.backups_jobs_us_east_1_${var.master_account}.accountid = ssm_global_resource_sync.account_bucket_us_east_1_${var.master_account}.account_id\nWHERE \n  backups_jobs.backups_jobs_us_east_1_${var.master_account}.state = 'FAILED' \nAND \n  ssm_global_resource_sync.account_bucket_us_east_1_${var.master_account}.account_workload = 'BC'\nAND\n  backups_jobs.backups_jobs_us_east_1_${var.master_account}.resourcetype = 'EC2'             \nAND\n  backups_jobs.backups_jobs_us_east_1_${var.master_account}.partition_0=format_datetime (current_timestamp, 'y')\nAND\n  backups_jobs.backups_jobs_us_east_1_${var.master_account}.partition_1=format_datetime (current_timestamp, 'M')\nAND\n  backups_jobs.backups_jobs_us_east_1_${var.master_account}.partition_2=format_datetime (current_timestamp, 'd');\n"
}
