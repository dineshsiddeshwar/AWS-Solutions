#Lambda function to update DL DDB table in bulk
resource "aws_lambda_function" "bulk_dl_ddb_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_bulk_dl_ddb.zip"
  function_name = "platform_bulk_dl_ddb"
  role          = aws_iam_role.platform_bulk_dl_ddb_role.arn
  handler       = "platform_bulk_dl_ddb.lambda_handler"
  source_code_hash = data.archive_file.bulk_dl_ddb_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 128
  timeout = 900

  environment {
    variables = {
      DDB_TABLE_NAME = "DL_Details"
    }
  }
  layers = ["arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python39:3", aws_lambda_layer_version.bulk_dl_pandas_lambda_layer.arn]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Pandas Lambda Layer
resource "aws_lambda_layer_version" "bulk_dl_pandas_lambda_layer" {
  filename   = "${path.module}/LambdaLayerZippedFiles/pandas.zip"
  layer_name = "PythonPandasLibraryLayer"
  description = "Pandas Library"
  skip_destroy = true
  compatible_runtimes = ["python3.8","python3.9"]
}

# Create S3 Bucket where DL Excel sheet will be uploaded
resource "aws_s3_bucket" "s3_excel_bucket" {
  bucket = "new-dl-excel-bucket-us-east-1-${var.master_account}"

  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "s3_excel_bucket_encryption" {
  bucket = aws_s3_bucket.s3_excel_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "s3_excel_bucket_block_public_access" {
  bucket = aws_s3_bucket.s3_excel_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "s3_excel_bucket_ownership" {
  bucket = aws_s3_bucket.s3_excel_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_acl" "s3_excel_bucket_acl" {
  bucket = aws_s3_bucket.s3_excel_bucket.id
}

resource "aws_lambda_permission" "allow_s3_excel_bucket_lambda_invoke" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.bulk_dl_ddb_lambda.arn
  principal     = "s3.amazonaws.com"
  source_account = var.master_account
  source_arn    = aws_s3_bucket.s3_excel_bucket.arn
}

resource "aws_s3_bucket_notification" "s3_excel_bucket_notification" {
  bucket = aws_s3_bucket.s3_excel_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.bulk_dl_ddb_lambda.arn
    events              = ["s3:ObjectCreated:Put"]
    filter_suffix       = ".xls"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.bulk_dl_ddb_lambda.arn
    events              = ["s3:ObjectCreated:Put"]
    filter_suffix       = ".xlsx"
  }

  depends_on = [aws_lambda_permission.allow_s3_excel_bucket_lambda_invoke]
}

# DL Details DynamoDB Table 
resource "aws_dynamodb_table" "dl_dynamodb_table" {
  name           = "DL_Details"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "DLEmailId"
  point_in_time_recovery { 
    enabled = true 
  } 

  attribute {
    name = "DLEmailId"
    type = "S"
  }
}

resource "aws_iam_role" "platform_bulk_dl_ddb_role" {
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
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole", "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_role_policy" "platform_bulk_dl_ddb_inline_policy" {
  name = "BulkDlDdbLambdaRolePolicy"
  role = aws_iam_role.platform_bulk_dl_ddb_role.id
  policy = data.aws_iam_policy_document.data_bulk_dl_ddb_policy.json
}