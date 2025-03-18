#  Exception AMI DynamoDB Table
resource "aws_dynamodb_table" "exception_ami_dynamodb_table" {
  name           = "platform_exception_ami_accounts"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "AccountNumber"
  point_in_time_recovery { 
    enabled = true 
  }

  attribute {
    name = "AccountNumber"
    type = "S"
  }
}

# Tag automation create resource lambda
resource "aws_lambda_function" "tagautomation_create_resource_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_tagautomation_create_resource.zip"
  function_name = "platform_tagautomation_create_resource"
  role          = var.role_arn
  handler       = "platform_tagautomation_create_resource.lambda_handler"
  source_code_hash = data.archive_file.tagautomation_create_resource_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# AMI tagging lambda
resource "aws_lambda_function" "ami_tagging_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_ami_tagging.zip"
  function_name = "platform_ami_tagging"
  role          = var.role_arn
  handler       = "platform_ami_tagging.lambda_handler"
  source_code_hash = data.archive_file.ami_tagging_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2880
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# EKS AMI tagging lambda
resource "aws_lambda_function" "eks_ami_tagging_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_ami_tagging_eks.zip"
  function_name = "platform_ami_tagging_eks"
  role          = var.role_arn
  handler       = "platform_ami_tagging_eks.lambda_handler"
  source_code_hash = data.archive_file.eks_ami_tagging_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2880
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Exception scheduled AMI tagging lambda
resource "aws_lambda_function" "exception_scheduled_ami_tagging_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_exception_scheduled_ami_tagging.zip"
  function_name = "platform_exception_scheduled_ami_tagging"
  role          = var.role_arn
  handler       = "platform_exception_scheduled_ami_tagging.lambda_handler"
  source_code_hash = data.archive_file.exception_scheduled_ami_tagging_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2880
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Exception AMI tagging lambda
resource "aws_lambda_function" "exception_ami_tagging_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_exception_ami_tagging.zip"
  function_name = "platform_exception_ami_tagging"
  role          = var.role_arn
  handler       = "platform_exception_ami_tagging.lambda_handler"
  source_code_hash = data.archive_file.exception_ami_tagging_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2880
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Custom AMI Tagging Lambda
resource "aws_lambda_function" "custom_ami_tagging_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_Custome-AMI-Tagging.zip"
  function_name = "platform_Custome-AMI-Tagging"
  role          = var.role_arn
  handler       = "platform_Custome-AMI-Tagging.lambda_handler"
  source_code_hash = data.archive_file.custom_ami_tagging_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 2176
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Exception AMI Tagging lambda schedule
resource "aws_cloudwatch_event_rule" "exception_ami_tagging_schedule" {
  name        = "platform_Approve-Latest-AMI"
  description = "Scheduled Rule for every 12 hours"
  schedule_expression = "cron(0 */12 * * ? *)"
  is_enabled = true
}

resource "aws_cloudwatch_event_target" "exception_ami_tagging_target" {
  rule      = aws_cloudwatch_event_rule.exception_ami_tagging_schedule.name
  target_id = "TargetFunctionV2"
  arn       = aws_lambda_function.exception_scheduled_ami_tagging_lambda.arn
}

resource "aws_lambda_permission" "exception_ami_tagging_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.exception_scheduled_ami_tagging_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.exception_ami_tagging_schedule.arn
}