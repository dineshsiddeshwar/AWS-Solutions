################S3 Bucket S3AccessLogsBucket###########################################

resource "aws_s3_bucket" "S3AccessLogsBucket" {
  bucket = "platform-da2-central-s3accesslogs-${var.env_type}"
  #acl  = "log-delivery-write"

  tags = {
    platform_donotdelete  = "yes"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "S3AccessLogsBucket" {
  bucket = aws_s3_bucket.S3AccessLogsBucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "S3AccessLogsBucket" {
  bucket = aws_s3_bucket.S3AccessLogsBucket.id

  rule {
    id = var.s3accesslogs_bucket_rule_id
    status = "Enabled"
    transition{
        days = 30
        storage_class = "STANDARD_IA"
    }
    expiration {
      days = 31
    }
  }
}

data "aws_sqs_queue" "SecurityHubQueue"{
  name = "platform-da2-central-securityhub-${var.env_type}-queue"
}

resource "aws_s3_bucket_public_access_block" "S3AccessLogsBucket" {
  bucket = aws_s3_bucket.S3AccessLogsBucket.id
  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

data "aws_iam_role" "platform_splunk_role"{
    name = "Platform_Splunk"
}

data "aws_iam_policy_document" "S3AccessLogsBucketPolicy" {
  policy_id = "AccessLogsBucketPolicy"
  statement {
    sid = "SplunkAccess"
    principals {
      type        = "AWS"
      identifiers = [data.aws_iam_role.platform_splunk_role.arn]
    }
    actions = ["s3:*"]
    resources = [aws_s3_bucket.S3AccessLogsBucket.arn,
    "arn:aws:s3:::platform-da2-central-s3accesslogs-${var.env_type}/*"]
  }
  statement {
    sid = "AWSLogDeliveryAclCheck"
    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }
    actions = ["s3:GetBucketAcl"]
    resources = [aws_s3_bucket.S3AccessLogsBucket.arn]
    }
  statement {
    sid = "AWSLogDeliveryWrite"
    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }
    actions = ["s3:PutObject"]
    resources = [aws_s3_bucket.S3AccessLogsBucket.arn,
                "arn:aws:s3:::platform-da2-central-s3accesslogs-${var.env_type}/*"]
    condition {
        test = "StringEquals"
        variable = "s3:x-amz-acl"
        values = ["bucket-owner-full-control"]
      
    }
    }
}

resource "aws_s3_bucket_policy" "S3AccessLogsBucketPolicy" {
  bucket = aws_s3_bucket.S3AccessLogsBucket.id
  policy = data.aws_iam_policy_document.S3AccessLogsBucketPolicy.json
}


################S3 Bucket CloudtrailBucket###########################################

resource "aws_s3_bucket" "CloudtrailBucket" {
  bucket = "platform-da2-central-cloudtrail-${var.env_type}"

  tags = {
    platform_donotdelete  = "yes"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "CloudtrailBucket" {
  bucket = aws_s3_bucket.CloudtrailBucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "CloudtrailBucket" {
  bucket = aws_s3_bucket.CloudtrailBucket.id

  rule {
    id = var.cloudtrail_bucket_rule_id
    status = "Enabled"
    transition{
        days = 30
        storage_class = "STANDARD_IA"
    }
    expiration {
      days = 365
    }
  }
}

resource "aws_s3_bucket_logging" "CloudtrailBucket" {
  bucket = aws_s3_bucket.CloudtrailBucket.id
  target_bucket = aws_s3_bucket.S3AccessLogsBucket.id
  target_prefix = ""
}

data "aws_sqs_queue" "ConfigCloudtrailQueue"{
  name = "platform-da2-central-config-cloudtrail-${var.env_type}-queue"
}

data  "aws_sqs_queue" "CloudtrailQueue"{
  name = "platform-da2-central-cloudtrail-${var.env_type}-queue"
}

resource "aws_s3_bucket_notification" "CloudtrailBucket" {
  bucket = aws_s3_bucket.CloudtrailBucket.id

  queue {
    queue_arn     = data.aws_sqs_queue.CloudtrailQueue.arn
    events        = ["s3:ObjectCreated:Copy"]
    #filter_suffix = ""
  }
}
resource "aws_s3_bucket_public_access_block" "CloudtrailBucket" {
  bucket = aws_s3_bucket.CloudtrailBucket.id
  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

data "aws_iam_role" "platform_log_admin_role"{
    name = "Platform_LogAdmin"
}

data "aws_iam_policy_document" "CloudtrailBucketPolicy" {
  policy_id = "CloudtrailLogsBucketPolicy"
  statement {
    sid = "SplunkAccess"
    principals {
      type        = "AWS"
      identifiers = [data.aws_iam_role.platform_splunk_role.arn]
    }
    actions = ["s3:*"]
    resources = [ "arn:aws:s3:::platform-da2-central-cloudtrail-${var.env_type}/*",
                  aws_s3_bucket.CloudtrailBucket.arn]
  }
  statement {
    sid = "AWSLogDeliveryPermission"
    principals {
      type        = "AWS"
      identifiers = [data.aws_iam_role.platform_log_admin_role.arn]
    }
    actions = ["s3:PutObject"]
    resources = ["arn:aws:s3:::platform-da2-central-cloudtrail-${var.env_type}/*",
                aws_s3_bucket.CloudtrailBucket.arn]
    condition {
      test = "StringEquals"
      variable = "s3:x-amz-acl"
      values = ["bucket-owner-full-control"]
    }
    }
    
}

resource "aws_s3_bucket_policy" "CloudtrailBucketPolicy" {
  bucket = aws_s3_bucket.CloudtrailBucket.id
  policy = data.aws_iam_policy_document.CloudtrailBucketPolicy.json
}

#############################S3 Bucket Config########################################

resource "aws_s3_bucket" "ConfigBucket" {
  bucket = "platform-da2-central-config-${var.env_type}"

  tags = {
    platform_donotdelete  = "yes"
  }
}


resource "aws_s3_bucket_server_side_encryption_configuration" "ConfigBucket" {
  bucket = aws_s3_bucket.ConfigBucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "ConfigBucket" {
  bucket = aws_s3_bucket.ConfigBucket.id

  rule {
    id = var.config_bucket_rule_id
    status = "Enabled"
    transition{
        days = 30
        storage_class = "STANDARD_IA"
    }
    expiration {
      days = 365
    }
  }
}

resource "aws_s3_bucket_logging" "ConfigBucket" {
  bucket = aws_s3_bucket.ConfigBucket.id
  target_bucket = aws_s3_bucket.S3AccessLogsBucket.id
  target_prefix = ""
}
data "aws_sqs_queue" "ConfigQueue"{
  name = "platform-da2-central-config-${var.env_type}-queue"
}

resource "aws_s3_bucket_notification" "ConfigBucket" {
  bucket = aws_s3_bucket.ConfigBucket.id

  queue {
    queue_arn     = data.aws_sqs_queue.ConfigQueue.arn
    events        = ["s3:ObjectCreated:Copy"]
    #filter_suffix = ""
  }
}

resource "aws_s3_bucket_public_access_block" "ConfigBucket" {
  bucket = aws_s3_bucket.ConfigBucket.id
  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}


data "aws_iam_policy_document" "ConfigBucket" {
  policy_id = "ConfigLogsBucketPolicy"
  statement {
    sid = "SplunkAccess"
    principals {
      type        = "AWS"
      identifiers = [data.aws_iam_role.platform_splunk_role.arn]
    }
    actions = ["s3:*"]
    resources = ["arn:aws:s3:::platform-da2-central-config-${var.env_type}/*",
                  aws_s3_bucket.ConfigBucket.arn]
  }
  statement {
    sid = "AWSLogDeliveryPermission"
    principals {
      type        = "AWS"
      identifiers = [data.aws_iam_role.platform_log_admin_role.arn]
    }
    actions = ["s3:PutObject"]
    resources = ["arn:aws:s3:::platform-da2-central-config-${var.env_type}/*",
                aws_s3_bucket.ConfigBucket.arn]
    condition {
        test = "StringEquals"
        variable = "s3:x-amz-acl"
        values = ["bucket-owner-full-control"]
    }
    }
}

resource "aws_s3_bucket_policy" "ConfigPolicy" {
  bucket = aws_s3_bucket.ConfigBucket.id
  policy = data.aws_iam_policy_document.ConfigBucket.json
}

##############################################S3  VPCFlowLogsBucket############################resource "aws_s3_bucket" "CloudtrailBucket" {
  
resource "aws_s3_bucket" "VpcFlowLogsBucket" {
  bucket = "platform-da2-central-vpcflowlogs-${var.env_type}"

  tags = {
    platform_donotdelete  = "yes"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "VpcFlowLogsBucket" {
  bucket = aws_s3_bucket.VpcFlowLogsBucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "VpcFlowLogsBucket" {
  bucket = aws_s3_bucket.VpcFlowLogsBucket.id

  rule {
    id = var.vpcflowlogs_bucket_rule_id
    status = "Enabled"
    transition{
        days = 30
        storage_class = "STANDARD_IA"
    }
    expiration {
      days = 183
    }
  }
}

resource "aws_s3_bucket_logging" "VpcFlowLogsBucket" {
  bucket = aws_s3_bucket.VpcFlowLogsBucket.id
  target_bucket = aws_s3_bucket.S3AccessLogsBucket.id
  target_prefix = ""
}

data "aws_sqs_queue" "VPCFlowLogsQueue"{
  name = "platform-da2-central-vpcflowlogs-${var.env_type}-queue"
}

resource "aws_s3_bucket_notification" "VpcFlowLogsBucket" {
  bucket = aws_s3_bucket.VpcFlowLogsBucket.id

  queue {
    queue_arn     = data.aws_sqs_queue.VPCFlowLogsQueue.arn
    events        = ["s3:ObjectCreated:Put"]
    #filter_suffix = ""
  }
}

resource "aws_s3_bucket_public_access_block" "VpcFlowLogsBucket" {
  bucket = aws_s3_bucket.VpcFlowLogsBucket.id
  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}


data "aws_iam_policy_document" "VpcFlowLogsBucketPolicy" {
  policy_id = "VPCFlowLogsBucketPolicy"
  statement {
    sid = "SplunkAccess"
    principals {
      type        = "AWS"
      identifiers = [data.aws_iam_role.platform_splunk_role.arn]
    }
    actions = ["s3:*"]
    resources = [aws_s3_bucket.VpcFlowLogsBucket.arn,
    "arn:aws:s3:::platform-da2-central-vpcflowlogs-${var.env_type}/*"]
  }
  statement {
    sid = "AWSLogDeliveryAclCheck"
    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }
    actions = ["s3:GetBucketAcl"]
    resources = [aws_s3_bucket.VpcFlowLogsBucket.arn]
    }
  statement {
    sid = "AWSLogDeliveryWrite"
    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }
    actions = ["s3:PutObject"]
    resources = [aws_s3_bucket.VpcFlowLogsBucket.arn,
      "arn:aws:s3:::platform-da2-central-vpcflowlogs-${var.env_type}/*"]
    condition {
        test = "StringEquals"
        variable = "s3:x-amz-acl"
        values = ["bucket-owner-full-control"]
    }
    }
}

resource "aws_s3_bucket_policy" "VpcFlowLogsBucketPolicy" {
  bucket = aws_s3_bucket.VpcFlowLogsBucket.id
  policy = data.aws_iam_policy_document.VpcFlowLogsBucketPolicy.json
}
