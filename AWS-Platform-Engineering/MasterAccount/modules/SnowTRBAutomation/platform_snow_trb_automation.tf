# TRB Approved Images DynamoDB Table
resource "aws_dynamodb_table" "trb_approved_images_dynamodb_table" {
  name           = "TRB_AMI_Exception_Management"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "RequestNumber"
  point_in_time_recovery { 
    enabled = true 
  }

  attribute {
    name = "RequestNumber"
    type = "S"
  }
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Requests Lambda Layer
resource "aws_lambda_layer_version" "trb_requests_lambda_layer" {
  filename   = "${path.module}/LambdaLayerZippedFiles/python.zip"
  layer_name = "TRBRequests"
  description = "TRB HTTPS Requests Layer"
  skip_destroy = true
  compatible_runtimes = ["python3.8"]
}

# TRB Automation Lambda
resource "aws_lambda_function" "trb_automation_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_TRB_management_payer.zip"
  function_name = "platform_TRB_management_payer"
  role          = var.role_arn
  handler       = "platform_TRB_management_payer.lambda_handler"
  source_code_hash = data.archive_file.trb_automation_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  environment {
    variables = {
      platform_trb_details = "TRB_AMI_Exception_Management"
      platform_child_event_rule_name = "platform_trb_automation_rule_name"
      target_function_name = "platform_TRB_management_child"
      trb_parameter_ami_name = "platform_trb_ami_name"
      trb_parameter_owner_id = "platform_trb_ami_owner_id"
      trb_parameter_image_id = "platform_trb_ami_image_id"
      step_function_arn = aws_sfn_state_machine.trb_automation_state_machine.arn
      step_function_name = aws_sfn_state_machine.trb_automation_state_machine.name
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }

  layers = [aws_lambda_layer_version.trb_requests_lambda_layer.arn]
}

resource "aws_lambda_function" "trb_automation_lambda_child_trigger" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_TRB_management_payer_child_account_trigger.zip"
  function_name = "platform_TRB_management_payer_child_account_trigger"
  role          = var.role_arn
  handler       = "platform_TRB_management_payer_child_account_trigger.lambda_handler"
  source_code_hash = data.archive_file.trb_automation_monitoring_lambda_child_trigger_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900

  environment {
    variables = {
      platform_trb_details = "TRB_AMI_Exception_Management"
      platform_child_event_rule_name = "platform_trb_automation_rule_name"
      target_function_name = "platform_TRB_management_child"
      trb_parameter_ami_name = "platform_trb_ami_name"
      trb_parameter_owner_id = "platform_trb_ami_owner_id"
      trb_parameter_image_id = "platform_trb_ami_image_id"
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }

  layers = [aws_lambda_layer_version.trb_requests_lambda_layer.arn]
}

resource "aws_lambda_function" "trb_result_aggregator" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_TRB_management_payer_result_aggregator.zip"
  function_name = "platform_TRB_management_payer_result_aggregator"
  role          = var.role_arn
  handler       = "platform_TRB_management_payer_result_aggregator.lambda_handler"
  source_code_hash = data.archive_file.trb_result_aggregator_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900

  environment {
    variables = {
      platform_trb_details = "TRB_AMI_Exception_Management"
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }

  layers = [aws_lambda_layer_version.trb_requests_lambda_layer.arn]
}

# TRB Automation Monitoring Lambda
resource "aws_lambda_function" "trb_automation_monitoring_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_TRB_management_monitoring.zip"
  function_name = "platform_TRB_management_monitoring"
  role          = var.role_arn
  handler       = "platform_TRB_management_monitoring.lambda_handler"
  source_code_hash = data.archive_file.trb_automation_monitoring_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 128
  timeout = 900

  environment {
    variables = {
      platform_trb_details = "TRB_AMI_Exception_Management"
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }

  layers = [aws_lambda_layer_version.trb_requests_lambda_layer.arn]
}

resource "aws_cloudwatch_event_rule" "trb_automation_monitoring_lambda_schedule" {
  name = "platform_TRB_Management_Expiration_schedule"
  description = "Scheduled to run the lambda every Day at 10AM"
  schedule_expression = "cron(0 10 * * ? *)"
  is_enabled = true
}

resource "aws_cloudwatch_event_target" "trb_automation_monitoring_lambda_target" {
  rule      = aws_cloudwatch_event_rule.trb_automation_monitoring_lambda_schedule.name
  target_id = "TargetFunctionV1"
  arn       = aws_lambda_function.trb_automation_monitoring_lambda.arn
}

resource "aws_lambda_permission" "trb_automation_monitoring_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.trb_automation_monitoring_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.trb_automation_monitoring_lambda_schedule.arn
}

# TRB Automation Rest API
resource "aws_api_gateway_rest_api" "trb_automation_rest_api" {
  name = "LatestTRBAuth"
  description = "APIs used for service-now TRB approved image Whitelisting requests"
  api_key_source = "AUTHORIZER"
}

# TRB Automation Rest API Policy
resource "aws_api_gateway_rest_api_policy" "trb_automation_rest_api_policy" {
  rest_api_id = aws_api_gateway_rest_api.trb_automation_rest_api.id
  policy      = data.aws_iam_policy_document.data_trb_automation_rest_api_policy.json
}

# TRB Automation Rest API Resource to Whitelist Path
resource "aws_api_gateway_resource" "trb_automation_rest_api_resource" {
  rest_api_id = aws_api_gateway_rest_api.trb_automation_rest_api.id
  parent_id   = aws_api_gateway_rest_api.trb_automation_rest_api.root_resource_id
  path_part   = "TRBResource"
}

# TRB Automation Rest API Authorizer
resource "aws_api_gateway_authorizer" "trb_automation_rest_api_authorizer" {
  name                   = "trb_api_key_authorizer"
  authorizer_result_ttl_in_seconds = 300
  rest_api_id            = aws_api_gateway_rest_api.trb_automation_rest_api.id
  authorizer_uri         = "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:${var.master_account}:function:platform_snow_integration_authorizer/invocations"
  identity_source =  "method.request.querystring.apiKey"
  type = "REQUEST"
}

# TRB Automation Rest API Post Method
resource "aws_api_gateway_method" "trb_automation_rest_api_post_method" {
  rest_api_id   = aws_api_gateway_rest_api.trb_automation_rest_api.id
  resource_id   = aws_api_gateway_resource.trb_automation_rest_api_resource.id
  authorizer_id = aws_api_gateway_authorizer.trb_automation_rest_api_authorizer.id
  http_method   = "POST"
  authorization = "CUSTOM"
  api_key_required = true
}

# TRB Automation Rest API Post Integration
resource "aws_api_gateway_integration" "trb_automation_rest_api_post_integration" {
  rest_api_id          = aws_api_gateway_rest_api.trb_automation_rest_api.id
  resource_id          = aws_api_gateway_resource.trb_automation_rest_api_resource.id
  integration_http_method = "POST"
  http_method = aws_api_gateway_method.trb_automation_rest_api_post_method.http_method
  passthrough_behavior = "WHEN_NO_TEMPLATES"
  type = "AWS" 
  uri = "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/${aws_lambda_function.trb_automation_lambda.arn}/invocations"
}

# TRB Automation Rest API Post Integration response
resource "aws_api_gateway_integration_response" "trb_automation_rest_api_post_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.trb_automation_rest_api.id
  resource_id = aws_api_gateway_resource.trb_automation_rest_api_resource.id
  http_method = aws_api_gateway_method.trb_automation_rest_api_post_method.http_method
  status_code = "200"

  response_templates = {
    "application/json" = ""
  }
}

# TRB Automation Rest API Post Method response
resource "aws_api_gateway_method_response" "trb_automation_rest_api_post_method_response" {
  rest_api_id = aws_api_gateway_rest_api.trb_automation_rest_api.id
  resource_id = aws_api_gateway_resource.trb_automation_rest_api_resource.id
  http_method = aws_api_gateway_method.trb_automation_rest_api_post_method.http_method
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }
}

# TRB Automation Rest API Options Method
resource "aws_api_gateway_method" "trb_automation_rest_api_options_method" {
  rest_api_id   = aws_api_gateway_rest_api.trb_automation_rest_api.id
  resource_id   = aws_api_gateway_resource.trb_automation_rest_api_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

# TRB Automation Rest API Options Integration
resource "aws_api_gateway_integration" "trb_automation_rest_api_options_integration" {
  rest_api_id          = aws_api_gateway_rest_api.trb_automation_rest_api.id
  resource_id          = aws_api_gateway_resource.trb_automation_rest_api_resource.id
  passthrough_behavior = "WHEN_NO_MATCH"
  http_method = aws_api_gateway_method.trb_automation_rest_api_options_method.http_method
  type = "MOCK" 
  
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

# TRB Automation Rest API Options Integration response
resource "aws_api_gateway_integration_response" "trb_automation_rest_api_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.trb_automation_rest_api.id
  resource_id = aws_api_gateway_resource.trb_automation_rest_api_resource.id
  http_method = aws_api_gateway_method.trb_automation_rest_api_options_method.http_method
  status_code = "200"

  response_templates = {
    "application/json" = ""
  }

  response_parameters = { 
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'" 
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }
}

# TRB Automation Rest API Options Method response
resource "aws_api_gateway_method_response" "trb_automation_rest_api_options_method_response" {
  rest_api_id = aws_api_gateway_rest_api.trb_automation_rest_api.id
  resource_id = aws_api_gateway_resource.trb_automation_rest_api_resource.id
  http_method = aws_api_gateway_method.trb_automation_rest_api_options_method.http_method
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }

  response_parameters = { 
    "method.response.header.Access-Control-Allow-Headers" = false
    "method.response.header.Access-Control-Allow-Methods" = false
    "method.response.header.Access-Control-Allow-Origin" = false
  }
}

# TRB Automation Rest API deployment
resource "aws_api_gateway_deployment" "trb_automation_rest_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.trb_automation_rest_api.id
  description = "TRB AMI Enablement V1.0"
  depends_on = [
    aws_api_gateway_method.trb_automation_rest_api_post_method
 ]
}

# TRB Automation Rest API stage
resource "aws_api_gateway_stage" "trb_automation_rest_api_stage" {
  deployment_id = aws_api_gateway_deployment.trb_automation_rest_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.trb_automation_rest_api.id
  stage_name    = var.trb_env_type
}

# TRB Automation Rest API method settings
resource "aws_api_gateway_method_settings" "trb_automation_rest_api_method_settings" {
  rest_api_id = aws_api_gateway_rest_api.trb_automation_rest_api.id
  stage_name  = aws_api_gateway_stage.trb_automation_rest_api_stage.stage_name
  method_path = "*/*"

  settings {
    logging_level   = "INFO"
    data_trace_enabled = true
    throttling_burst_limit = "5000"
    throttling_rate_limit = "10000"
  }
}

# TRB Automation Rest API Invoke permission for TRB Automation lambda
resource "aws_lambda_permission" "trb_automation_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.trb_automation_lambda.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:us-east-1:${var.master_account}:${aws_api_gateway_rest_api.trb_automation_rest_api.id}/*/*/*"
}

# TRB Automation Rest API Key
resource "aws_api_gateway_api_key" "trb_automation_rest_api_key" {
  name = "AWSTRBKey"
  description = "CloudFormation API Key V1"
  enabled = true
  depends_on = [
    aws_api_gateway_deployment.trb_automation_rest_api_deployment,
    aws_api_gateway_stage.trb_automation_rest_api_stage
 ]
}

# TRB Automation Rest API Gateway usage plan
resource "aws_api_gateway_usage_plan" "trb_automation_api_gateway_usage_plan" {
  name         = "TRBSnowAwsApiUsagePlan"
  description  = "Usage plan for the sake of using api key"

  api_stages {
    api_id = aws_api_gateway_rest_api.trb_automation_rest_api.id
    stage  = aws_api_gateway_stage.trb_automation_rest_api_stage.stage_name
  }

  quota_settings {
    limit  = 5000
    period = "MONTH"
  }

  throttle_settings {
    burst_limit = 200
    rate_limit  = 100
  }
}

# TRB Automation Rest API Gateway usage plan key
resource "aws_api_gateway_usage_plan_key" "trb_automation_api_gateway_usage_plan_key" {
  key_id        = aws_api_gateway_api_key.trb_automation_rest_api_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.trb_automation_api_gateway_usage_plan.id
}

# Step Function State Machine
resource "aws_sfn_state_machine" "trb_automation_state_machine" {
  name = "TRB_AMI_Exception_Management"
  role_arn = var.role_arn
  definition = data.template_file.trb_automation_step_function.rendered
  tags = {
    "platform_donotdelete" = "yes"
  }
}