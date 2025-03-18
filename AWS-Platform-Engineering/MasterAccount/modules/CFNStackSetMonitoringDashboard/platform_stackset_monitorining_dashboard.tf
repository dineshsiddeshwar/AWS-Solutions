#IAM Role for Glue Crawler
resource "aws_iam_role" "cfn_ss_crawler_role" {
  name                =  "platform_cfn_ss_crawler_role"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "glue.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole",
                    }
                ]
            })
  path                = "/"
  managed_policy_arns = [ "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole", "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_role_policy" "cfn_ss_crawler_role_inline_policy" {
  name = "S3BucketAccessPolicy"
  role = aws_iam_role.cfn_ss_crawler_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
        ]
        Effect   = "Allow"
        Resource = "arn:aws:s3:::platform-cfn-stackset-inventory-us-east-1-${var.master_account}/*"
      },
    ]
  })
}

#Glue Database for CFN StackSet Inventory
resource "aws_glue_catalog_database" "cfn_stackset_glue_catalog_database" {
  description = "Glue database to store all the data related to CloudFormation StackSets"
  name = "platform_cfn_stackset_db"
  catalog_id = var.master_account
}

#Glue Classifier for classifying CSV file
resource "aws_glue_classifier" "cfn_stackset_glue_csv_classifier" {
  name = "platform_CFN_SS_Glue_Classifier"

  csv_classifier {
    allow_single_column    = false
    contains_header        = "UNKNOWN"
    delimiter              = ","
    disable_value_trimming = true
    quote_symbol           = "\""
  }
}

# Glue crawler to crawl through the CFN StackSet inventory data stored in CSV file
resource "aws_glue_crawler" "cfn_stackset_glue_crawler" {
  database_name = aws_glue_catalog_database.cfn_stackset_glue_catalog_database.name
  classifiers   = [ 
    aws_glue_classifier.cfn_stackset_glue_csv_classifier.id
  ]
  configuration = jsonencode(
    {
      CreatePartitionIndex = false
      Version              = 1
    }
  )
  name          = "platform_CFN_SS_Crawler"
  description   = "Glue Crawler to crawl the CSV files stored in S3 buckets where CFN StackSet inventory data is stored"
  role          = aws_iam_role.cfn_ss_crawler_role.arn
  s3_target {
    path = "s3://platform-cfn-stackset-inventory-us-east-1-${var.master_account}"
  }
  tags = {
    "platform_donotdelete" = "yes"
  }
}

#IAM Role for CFN Monitoring Lambda function
resource "aws_iam_role" "crawler_lambda_execution_role" {
  name                =  "platform_crawler_lambda_role"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole",
                        "Condition": {
                            "StringEquals": {
                                "aws:SourceAccount": var.master_account
                            }
                        }
                    }
                ]
            })
  managed_policy_arns = [ "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole", "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_role_policy" "crawler_lambda_execution_role_inline_policy" {
  name = "platform_AmazonLambdaExecutionPolicy"
  role = aws_iam_role.crawler_lambda_execution_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "AllowStartGlueCrawler"
        Action = [
          "glue:StartCrawler",
        ]
        Effect   = "Allow"
        Resource = "arn:aws:glue:us-east-1:${var.master_account}:crawler/platform_CFN_SS_Crawler"
      },
    ]
  })
}

#Lambda function to run the Glue Crawler
resource "aws_lambda_function" "cfn_stackset_glue_crawler_lambda" {
  description   = "Lambda function to start the Glue crawler as soon as new object is uploaded to S3 CFN inventory bucket"
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_cfn_ss_glue_crawler.zip"
  function_name = "platform_cfn_ss_glue_crawler"
  role          = aws_iam_role.crawler_lambda_execution_role.arn
  handler       = "platform_cfn_ss_glue_crawler.lambda_handler"
  source_code_hash = data.archive_file.cfn_stackset_glue_crawler_lambda_zip.output_base64sha256

  architectures = ["arm64"]
  runtime = "python3.10"
  timeout = 120

  environment {
    variables = {
      GLUE_CRAWLER_NAME = "platform_CFN_SS_Crawler"
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

#S3 bucket to store CFN StackSet inventory data
resource "aws_s3_bucket" "cfn_stackset_inventory_bucket" {
  bucket = "platform-cfn-stackset-inventory-us-east-1-${var.master_account}"
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cfn_stackset_inventory_bucket_encryption" {
  bucket = aws_s3_bucket.cfn_stackset_inventory_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "cfn_stackset_inventory_bucket_lifecycle_configuration" {
  bucket = aws_s3_bucket.cfn_stackset_inventory_bucket.id

  rule {
    id = "SevenDaysExpiry"

    expiration {
      days = 7
    }

    filter {}

    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "cfn_stackset_inventory_bucket_block_public_access" {
  bucket = aws_s3_bucket.cfn_stackset_inventory_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_acl" "cfn_stackset_inventory_bucket_acl" {
  bucket = aws_s3_bucket.cfn_stackset_inventory_bucket.id
}

resource "aws_s3_bucket_ownership_controls" "cfn_stackset_inventory_bucket_ownership_controls" {
  bucket = aws_s3_bucket.cfn_stackset_inventory_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_notification" "cfn_stackset_inventory_bucket_notification_conf" {
  bucket = aws_s3_bucket.cfn_stackset_inventory_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.cfn_stackset_glue_crawler_lambda.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".csv"
  }
}

#Inventory data S3 bucket policy
resource "aws_s3_bucket_policy" "cfn_stackset_inventory_bucket_policy" {
  bucket = aws_s3_bucket.cfn_stackset_inventory_bucket.id
  policy = data.aws_iam_policy_document.cfn_stackset_inventory_bucket_policy.json
}

#Lambda permission to trigger on S3 object upload
resource "aws_lambda_permission" "cfn_stackset_glue_crawler_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cfn_stackset_glue_crawler_lambda.arn
  principal     = "s3.amazonaws.com"
  source_account = var.master_account
  source_arn    = "arn:aws:s3:::platform-cfn-stackset-inventory-us-east-1-${var.master_account}"
}

#IAM Role for CFN Monitoring Lambda function
resource "aws_iam_role" "cfn_ss_monitoring_lambda_role" {
  name                =  "platform_monitoring_lambda_role"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole",
                        "Condition": {
                            "StringEquals": {
                                "aws:SourceAccount": var.master_account
                            }
                        }
                    }
                ]
            })
  managed_policy_arns = [ "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole", "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_role_policy" "cfn_ss_monitoring_lambda_role_inline_policy" {
  name = "platform_AmazonLambdaExecutionPolicy"
  role = aws_iam_role.cfn_ss_monitoring_lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "AllowCFNStackSetList"
        Action = [
          "cloudformation:ListStackSets",
          "cloudformation:ListStackInstances",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Sid = "AllowS3Upload"
        Action = [
          "s3:PutObject",
        ]
        Effect   = "Allow"
        Resource = "arn:aws:s3:::platform-cfn-stackset-inventory-us-east-1-${var.master_account}/*"
      },
    ]
  })
}

#Lambda function for CFN StackSet monitoring
resource "aws_lambda_function" "cfn_stackset_monitoring_lambda" {
  description   = "Lambda function to describe all CloudFormation StackSets"
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_cfn_ss_monitoring.zip"
  function_name = "platform_cfn_ss_monitoring"
  role          = aws_iam_role.cfn_ss_monitoring_lambda_role.arn
  handler       = "platform_cfn_ss_monitoring.lambda_handler"
  source_code_hash = data.archive_file.cfn_stackset_monitoring_lambda_zip.output_base64sha256

  architectures = ["arm64"]
  runtime = "python3.10"
  memory_size = 512
  timeout = 900

  environment {
    variables = {
      CFN_SS_INVENTORY_BUCKET = "platform-cfn-stackset-inventory-us-east-1-${var.master_account}"
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# IAM Role for EventBridge scheduler
resource "aws_iam_role" "cfn_ss_scheduler_role" {
  name                =  "platform_cfn_ss_scheduler_role"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "scheduler.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole",
                        "Condition": {
                            "StringEquals": {
                                "aws:SourceAccount": var.master_account
                            }
                        }
                    }
                ]
            })
}

resource "aws_iam_role_policy" "cfn_ss_scheduler_role_inline_policy" {
  name = "platform_AmazonEventBridgeExecutionPolicy"
  role = aws_iam_role.cfn_ss_scheduler_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "AllowLambdaInvoke"
        Action = [
          "lambda:InvokeFunction",
        ]
        Effect   = "Allow"
        Resource = aws_lambda_function.cfn_stackset_monitoring_lambda.arn
      },
    ]
  })
}

# EventBridge scheduler to invoke CFN StackSet monitoring Lambda function
resource "aws_scheduler_schedule" "cfn_stackset_monitoring_lambda_schedule" {
  name        = "platform_cfn_stackset_monitoring_schedule"
  description = "Scheduler to run the Lambda function at 6 AM IST every day"

  flexible_time_window {
    mode = "OFF"
  }
  schedule_expression = "cron(0 6 * * ? *)"
  schedule_expression_timezone = "Asia/Calcutta"
  state = "ENABLED"

  target {
    arn      = aws_lambda_function.cfn_stackset_monitoring_lambda.arn
    role_arn = aws_iam_role.cfn_ss_scheduler_role.arn
  }
}







