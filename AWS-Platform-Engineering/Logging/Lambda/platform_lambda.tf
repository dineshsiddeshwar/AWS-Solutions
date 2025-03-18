data "aws_iam_role" "platform_log_admin_role"{
    name = "Platform_LogAdmin"
}


data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/platform_config_cloudtrail.py"
  output_path = "${path.module}/lambda_function_payload.zip"
}



resource "aws_lambda_function" "platform_config_cloudtrail" {
  filename      = "${path.module}/lambda_function_payload.zip"
  function_name = "platform_config_cloudtrail"
  description = "Lambda function to collect CloudTrail & Config logfiles from common bucket and put it in the respective S3 Bucket of LoggingAccount."
  role          = data.aws_iam_role.platform_log_admin_role.arn
  handler       = "platform_config_cloudtrail.lambda_handler"
  memory_size = 256

  source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime = "python3.8"

  timeout = 900

  environment {
    variables = {
      setup_env = var.env_type
      ou_id = var.ou_id
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

data aws_sqs_queue ConfigCloudtrailQueue{
  name = "platform-da2-central-config-cloudtrail-${var.env_type}-queue"
}

resource "aws_lambda_event_source_mapping" "ConfigCloudTrailLambdaEventSourcing" {
  batch_size = 5
  event_source_arn = data.aws_sqs_queue.ConfigCloudtrailQueue.arn
  #event_source_arn = aws_sqs_queue.ConfigCloudtrailQueue.arn
  function_name    = aws_lambda_function.platform_config_cloudtrail.arn
}

