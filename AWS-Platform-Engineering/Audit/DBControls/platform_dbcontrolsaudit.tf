resource "aws_s3_bucket" "MyDBBucket" {
  bucket = var.ScoreCardBucketName
  object_lock_enabled = true
  tags = {
    platform_donotdelete  = "yes"
  }
}

resource "aws_s3_bucket_public_access_block" "MyDBBucket_block_public_access" {
  bucket = aws_s3_bucket.MyDBBucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "MyDBBucket_bucket_ownership_controls" {
  bucket = aws_s3_bucket.MyDBBucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_notification" "MyDBBucket_bucket_notification_conf" {
  bucket = aws_s3_bucket.MyDBBucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.ScoreCardS3ToSharePoint.arn
    events              = ["s3:ObjectCreated:*"]
  }
}

resource "aws_lambda_permission" "LambdaInvokePermission" {
  count         = var.env_type=="prod" ? 1 : 0
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ScoreCardS3ToSharePoint.arn
  principal     = "s3.amazonaws.com"
  source_account= "056670755576"
  source_arn    = "arn:aws:s3:::${var.ScoreCardBucketName}"
}

data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_ScoreCardS3ToSharePoint.py"
  output_path = "${path.module}/platform_ScoreCardS3ToSharePoint.zip"
}

resource "aws_lambda_function" "ScoreCardS3ToSharePoint" {
  depends_on    = [aws_lambda_layer_version.ScoreCardOffice3LambdaLayer]
  filename      = "${path.module}/platform_ScoreCardS3ToSharePoint.zip"
  function_name = "platform_ScoreCardS3ToSharePoint"
  description = "Lambda function to upload scorecards from s3 to SharePoint"
  role          = aws_iam_role.ScoreCardS3ToSharePointRole.arn
  handler       = "platform_ScoreCardS3ToSharePoint.lambda_handler"
  memory_size = 128
  source_code_hash = data.archive_file.lambda.output_base64sha256
  layers        = [aws_lambda_layer_version.ScoreCardOffice3LambdaLayer.arn]
  runtime = "python3.9"

  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_lambda_layer_version" "ScoreCardOffice3LambdaLayer" {
  filename   = "${path.module}/LambdaLayerZippedFiles/office3.zip"
  layer_name = "ScoreCardOffice3"
  description = "Office3 for Python Layer"
  skip_destroy = true
  compatible_runtimes = ["python3.8", "python3.9", "python3.10"]
}

resource "aws_iam_role" "ScoreCardS3ToSharePointRole" {
  name = "platform_ScoreCardS3ToSharePointRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
  path = "/" 
  managed_policy_arns = [
    aws_iam_policy.ScoreCardS3ToSharePointPolicy.arn
  ]

  tags = {
    platform_donotdelete = "yes"
  }
}

resource "aws_iam_policy" "ScoreCardS3ToSharePointPolicy" {
  name        = "platform_ScoreCardS3ToSharePointPolicy"
  path        = "/"
  description = "platform_ScoreCardS3ToSharePointPolicy"
  policy = jsonencode({
     Version = "2012-10-17"
    "Statement": [
        {
            "Action": [
                "logs:CreateLogGroup"
            ],
            "Resource": [
                "arn:aws:logs:*:${var.account_id}:*"
            ],
            "Effect": "Allow",
            "Sid": "VisualEditor0"
        },
        {
            "Action": [
                "logs:CreateLogGroup",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:*:${var.account_id}:log-group:/aws/lambda/platform_ScoreCardS3ToSharePointPolicy:*"
            ],
            "Effect": "Allow",
            "Sid": "VisualEditor1"
        },
        {
            "Action": [
                "s3:ListAccessPointsForObjectLambda",
                "s3:GetObjectVersionTagging",
                "s3:GetStorageLensConfigurationTagging",
                "s3:GetObjectAcl",
                "s3:GetBucketObjectLockConfiguration",
                "s3:GetIntelligentTieringConfiguration",
                "s3:GetObjectVersionAcl",
                "s3:GetBucketPolicyStatus",
                "s3:GetObjectRetention",
                "s3:GetBucketWebsite",
                "s3:GetJobTagging",
                "s3:ListJobs",
                "s3:GetMultiRegionAccessPoint",
                "s3:GetObjectAttributes",
                "s3:GetObjectLegalHold",
                "s3:GetBucketNotification",
                "s3:DescribeMultiRegionAccessPointOperation",
                "s3:GetReplicationConfiguration",
                "s3:ListMultipartUploadParts",
                "s3:GetObject",
                "s3:DescribeJob",
                "s3:GetAnalyticsConfiguration",
                "s3:GetObjectVersionForReplication",
                "s3:GetAccessPointForObjectLambda",
                "s3:GetStorageLensDashboard",
                "s3:GetLifecycleConfiguration",
                "s3:GetAccessPoint",
                "s3:GetInventoryConfiguration",
                "s3:GetBucketTagging",
                "s3:GetAccessPointPolicyForObjectLambda",
                "s3:GetBucketLogging",
                "s3:ListBucketVersions",
                "s3:ListBucket",
                "s3:GetAccelerateConfiguration",
                "s3:GetObjectVersionAttributes",
                "s3:GetBucketPolicy",
                "s3:GetEncryptionConfiguration",
                "s3:GetObjectVersionTorrent",
                "s3:GetBucketRequestPayment",
                "s3:GetAccessPointPolicyStatus",
                "s3:GetObjectTagging",
                "s3:GetMetricsConfiguration",
                "s3:GetBucketOwnershipControls",
                "s3:GetBucketPublicAccessBlock",
                "s3:GetMultiRegionAccessPointPolicyStatus",
                "s3:ListBucketMultipartUploads",
                "s3:GetMultiRegionAccessPointPolicy",
                "s3:GetAccessPointPolicyStatusForObjectLambda",
                "s3:ListAccessPoints",
                "s3:GetBucketVersioning",
                "s3:ListMultiRegionAccessPoints",
                "s3:GetBucketAcl",
                "s3:GetAccessPointConfigurationForObjectLambda",
                "s3:ListStorageLensConfigurations",
                "s3:GetObjectTorrent",
                "s3:GetMultiRegionAccessPointRoutes",
                "s3:GetStorageLensConfiguration",
                "s3:GetAccountPublicAccessBlock",
                "s3:ListAllMyBuckets",
                "s3:GetBucketCORS",
                "s3:GetBucketLocation",
                "s3:GetAccessPointPolicy",
                "s3:GetObjectVersion",
                "s3:GetBucketNotification",
                "s3:PutBucketNotification",
                "secretsmanager:ListSecrets",
                "secretsmanager:GetSecretValue"
            ],
            "Resource": "*",
            "Effect": "Allow",
            "Sid": "VisualEditor2"
        }
    ]
    })
  #policy = file("${path.module}/Policies/IAMP0004-PlatformScoreCardS3ToSharePointPolicy/policy.json")
}


