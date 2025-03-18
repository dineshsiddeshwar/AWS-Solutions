data "aws_iam_role" "platform_Admin"{
    name = "platform_Admin"
}


data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/platform_billing_automation_lambda.py"
  output_path = "${path.module}/lambda_function_payload.zip"
}



resource "aws_lambda_function" "platform_billing_automation_lambda" {
  filename      = data.archive_file.lambda.output_path
  function_name = "platform_billing_automation_lambda"
  description = "Lambda function to provide billing details."
  layers =   ["arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python39:18"]
  role          = data.aws_iam_role.platform_Admin.arn
  handler       = "platform_billing_automation_lambda.lambda_handler"
  memory_size = 256
  source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime = "python3.9"

  timeout = 900

  environment {
    variables = {
      athena_database = var.athena_database
      athena_table = var.athena_table
      s3_output_location = var.s3_output_location
      s3_bucket = var.s3_bucket
      account_id = var.account_id
      cost_tracker = var.cost_tracker
      main_billing_file = var.main_billing_file
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}


data "archive_file" "lambda_cost_tracker" {
  type        = "zip"
  source_file = "${path.module}/platform_cost_tracker_lambda.py"
  output_path = "${path.module}/lambda_cost_tracker_payload.zip"
}



resource "aws_lambda_function" "platform_cost_tracker_lambda" {
  filename      = data.archive_file.lambda_cost_tracker.output_path
  function_name = "platform_cost_tracker_lambda"
  description = "Lambda function to create cost tracker"
  layers =   ["arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python39:18"]
  role          = data.aws_iam_role.platform_Admin.arn
  handler       = "platform_cost_tracker_lambda.lambda_handler"
  memory_size = 256
  source_code_hash = data.archive_file.lambda_cost_tracker.output_base64sha256

  runtime = "python3.9"

  timeout = 900

  environment {
    variables = {
      athena_database = var.athena_database
      athena_table = var.athena_table
      s3_output_location = var.s3_output_location
      s3_bucket = var.s3_bucket
      account_id = var.account_id
      cost_tracker = var.cost_tracker
      main_billing_file = var.main_billing_file
      from_email =var.from_email
      to_email = var.to_email
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}

######################################### Cloudwatch Event Rule #######################################


resource "aws_cloudwatch_event_rule" "platform_billing_automation" {
  name        = "platform_billing_automation"
  description = "Rule for triggering lambda function"
  schedule_expression = "cron(0 10 6 * ? *)"
  
}

resource "aws_cloudwatch_event_target" "platform_billing_automation" {
  rule      = aws_cloudwatch_event_rule.platform_billing_automation.name
  target_id = "SendToLambda"
  arn       = aws_lambda_function.platform_billing_automation_lambda.arn
}

resource "aws_lambda_permission" "platform_billing_automation" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.platform_billing_automation_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.platform_billing_automation.arn
}


resource "aws_cloudwatch_event_rule" "platform_cost_tracker" {
  name        = "platform_cost_tracker"
  description = "Rule for triggering cost tracker lambda function"
  schedule_expression = "cron(0 8 6 * ? *)"
  
}

resource "aws_cloudwatch_event_target" "platform_cost_tracker" {
  rule      = aws_cloudwatch_event_rule.platform_cost_tracker.name
  target_id = "SendToCostLambda"
  arn       = aws_lambda_function.platform_cost_tracker_lambda.arn
}

resource "aws_lambda_permission" "platform_cost_tracker" {
  statement_id  = "AllowExecutionFromCloudWatch1"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.platform_cost_tracker_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.platform_cost_tracker.arn
}