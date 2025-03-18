# Requests Lambda Layer for Non Interactive Users
resource "aws_lambda_layer_version" "NonInteractiveUser_Layer" {
  compatible_runtimes = ["python3.8"]
  description         = "NonInteractiveUser HTTPS Requests Layer"
  filename            = "${path.module}/LambdaLayerZippedFiles/python.zip"
  layer_name          = "NonInteractiveUserRequests"
}

# Payer Lambda for Non Interactive Users
resource "aws_lambda_function" "NonInteractiveUser_Lambda_Payer" {
  function_name = "platform_noninteractive_user_payer"
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_noninteractive_user_payer.zip"
  handler       = "platform_noninteractive_user_payer.lambda_handler"
  source_code_hash = data.archive_file.platform_noninteractive_user_payer_zip.output_base64sha256

  layers        = [aws_lambda_layer_version.NonInteractiveUser_Layer.arn]
  memory_size   = 128
  package_type  = "Zip"
  role          = var.master_admin_role_arn
  runtime       = "python3.10"
  tags = {
    platform_donotdelete = "yes"
  }
  timeout = 900
}

# Invoker Lambda for Non Interactive Users
resource "aws_lambda_function" "NonInteractiveUser_Lambda_Invoker" {
  function_name = "platform_noninteractive_user_invoker"
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_noninteractive_user_invoker.zip"
  handler       = "platform_noninteractive_user_invoker.lambda_handler"
  source_code_hash = data.archive_file.platform_noninteractive_user_invoker_zip.output_base64sha256

  memory_size   = 128
  package_type  = "Zip"
  role          = var.master_admin_role_arn
  runtime       = "python3.8"
  tags = {
    platform_donotdelete = "yes"
  }
  timeout = 900
}

# Receiver Lambda for Non Interactive Users
resource "aws_lambda_function" "NonInteractiveUser_Lambda_Receiver" {
  function_name = "platform_noninteractive_user_receiver"
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_noninteractive_user_receiver.zip"
  handler       = "platform_noninteractive_user_receiver.lambda_handler"
  source_code_hash = data.archive_file.platform_noninteractive_user_receiver_zip.output_base64sha256

  layers        = [aws_lambda_layer_version.NonInteractiveUser_Layer.arn]
  memory_size   = 128
  package_type  = "Zip"
  role          = var.master_admin_role_arn
  runtime       = "python3.8"
  tags = {
    platform_donotdelete = "yes"
  }
  timeout = 900
  depends_on = [
    aws_lambda_layer_version.NonInteractiveUser_Layer
  ]
}

# Response Lambda for Non Interactive Users
resource "aws_lambda_function" "NonInteractiveUser_Lambda_Response" {
  function_name = "platform_noninteractive_user_response"
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_noninteractive_user_response.zip"
  handler       = "platform_noninteractive_user_response.lambda_handler"
  source_code_hash = data.archive_file.platform_noninteractive_user_response_zip.output_base64sha256

  layers        = [aws_lambda_layer_version.NonInteractiveUser_Layer.arn]
  memory_size   = 128
  package_type  = "Zip"
  role          = var.master_admin_role_arn
  runtime       = "python3.10"
  tags = {
    platform_donotdelete = "yes"
  }
  timeout = 900
}

# Rest API Invoke permission for Invoker lambda for Non Interactive Users
resource "aws_lambda_permission" "NonInteractiveUserInvoker_Lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = "arn:aws:lambda:${local.region}:${local.accountid}:function:platform_noninteractive_user_invoker"
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.NonInteractive_User_Schedule.arn
  statement_id  = var.NonInteractiveUser_Lambda_Invoker_permission_statement_id
  depends_on = [
    aws_cloudwatch_event_rule.NonInteractive_User_Schedule
  ]
}

# Rest API Invoke permission for Authorizer lambda for Non Interactive Users
resource "aws_lambda_permission" "NonInteractiveUser_Lambda_ApiAuth_permission" {
  action        = "lambda:InvokeFunction"
  function_name = "arn:aws:lambda:${local.region}:${local.accountid}:function:platform_snow_integration_authorizer"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${local.region}:${local.accountid}:${aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id}/authorizers/${aws_api_gateway_authorizer.NonInteractiveUser_ApiAuthorizer.id}"
  statement_id  = var.NonInteractiveUser_Lambda_ApiAuth_permission_statement_id

  depends_on = [  
    aws_api_gateway_authorizer.NonInteractiveUser_ApiAuthorizer
  ]
}

# Rest API Invoke permission for Receiver lambda for Non Interactive Users
resource "aws_lambda_permission" "NonInteractiveUser_Receiver_Lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = "arn:aws:lambda:${local.region}:${local.accountid}:function:platform_noninteractive_user_receiver"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${local.region}:${local.accountid}:${aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id}/*/*/*"
  statement_id  = var.NonInteractiveUser_Lambda_Receiver_permission_statement_id

  depends_on = [
    aws_api_gateway_deployment.NonInteractiveUser_Deployment,
    aws_api_gateway_stage.stage,
    aws_lambda_function.NonInteractiveUser_Lambda_Receiver
  ]
}

# Rest API Authorizer for Non Interactive Users
resource "aws_api_gateway_authorizer" "NonInteractiveUser_ApiAuthorizer" {
  authorizer_uri  = "arn:aws:apigateway:${local.region}:lambda:path/2015-03-31/functions/arn:aws:lambda:${local.region}:${local.accountid}:function:platform_snow_integration_authorizer/invocations"
  identity_source = "method.request.querystring.apiKey"
  name            = "api_key_authorizer"
  rest_api_id     = aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id
  type            = "REQUEST"
  depends_on = [
    aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi
  ]
}

# Usage plan for Non Interactive Users
resource "aws_api_gateway_usage_plan" "NonInteractiveUser_ApiUsagePlan" {
  description = "Usage plan for the sake of using api key"
  name        = "NonInteractiveUserSnowAwsApiUsagePlan"

  api_stages {
    api_id = aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id
    stage  = aws_api_gateway_stage.stage.stage_name
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

# Rest API Gateway usage plan key for Non Interactive Users
resource "aws_api_gateway_usage_plan_key" "key" {
  key_id        = aws_api_gateway_api_key.NonInteractiveUser_Key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.NonInteractiveUser_ApiUsagePlan.id
}

# Rest API Options Method for Non Interactive Users
resource "aws_api_gateway_method" "NonInteractiveUser_OptionsMethod" {
  api_key_required = false
  authorization    = "NONE"
  http_method      = "OPTIONS"
  resource_id      = aws_api_gateway_resource.NonInteractiveUser_Resource.id
  rest_api_id      = aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id
}

# Rest API Options Integration for Non Interactive Users
resource "aws_api_gateway_integration" "non_interactive_user_snow_rest_api_options_integration" {
  rest_api_id          = aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id
  resource_id          = aws_api_gateway_resource.NonInteractiveUser_Resource.id
  http_method          = aws_api_gateway_method.NonInteractiveUser_OptionsMethod.http_method
  passthrough_behavior = "WHEN_NO_MATCH"
  type                 = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

# Rest API Options Integration for Non Interactive Users response
resource "aws_api_gateway_integration_response" "non_interactive_user_snow_rest_api_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id
  resource_id = aws_api_gateway_resource.NonInteractiveUser_Resource.id
  http_method = "OPTIONS"
  status_code = "200"

  response_templates = {
    "application/json" = ""
  }

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# Rest API Options Method response for Non Interactive Users response
resource "aws_api_gateway_method_response" "non_interactive_user_snow_rest_api_options_method_response" {
  rest_api_id = aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id
  resource_id = aws_api_gateway_resource.NonInteractiveUser_Resource.id
  http_method = "OPTIONS"
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = false
    "method.response.header.Access-Control-Allow-Methods" = false
    "method.response.header.Access-Control-Allow-Origin"  = false
  }
}

# Rest API POST Method for Non Interactive Users
resource "aws_api_gateway_method" "NonInteractiveUser_PostMethod" {
  api_key_required = true
  authorization    = "CUSTOM"
  authorizer_id    = aws_api_gateway_authorizer.NonInteractiveUser_ApiAuthorizer.id
  http_method      = "POST"
  resource_id      = aws_api_gateway_resource.NonInteractiveUser_Resource.id
  rest_api_id      = aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id
  depends_on = [
    aws_lambda_function.NonInteractiveUser_Lambda_Receiver,
    aws_api_gateway_authorizer.NonInteractiveUser_ApiAuthorizer,
    aws_api_gateway_resource.NonInteractiveUser_Resource
  ]
}

# Rest API POST Integration for Non Interactive Users
resource "aws_api_gateway_integration" "non_interactive_user_snow_rest_api_post_integration" {
  rest_api_id             = aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id
  resource_id             = aws_api_gateway_resource.NonInteractiveUser_Resource.id
  http_method             = aws_api_gateway_method.NonInteractiveUser_PostMethod.http_method
  integration_http_method = "POST"
  passthrough_behavior    = "WHEN_NO_TEMPLATES"
  type                    = "AWS"
  uri                     = "arn:aws:apigateway:${local.region}:lambda:path/2015-03-31/functions/arn:aws:lambda:${local.region}:${local.accountid}:function:platform_noninteractive_user_receiver/invocations"

  # request_templates = {
  #   "application/json" = 
  # }
}

# Rest API POST Integration for Non Interactive Users response
resource "aws_api_gateway_integration_response" "non_interactive_user_snow_rest_api_post_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id
  resource_id = aws_api_gateway_resource.NonInteractiveUser_Resource.id
  http_method = "POST"
  status_code = "200"

  response_templates = {
    "application/json" = ""
  }
}

# Rest API Post Method response for Non Interactive Users
resource "aws_api_gateway_method_response" "non_interactive_user_snow_rest_api_post_method_response" {
  rest_api_id = aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id
  resource_id = aws_api_gateway_resource.NonInteractiveUser_Resource.id
  http_method = "POST"
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }
}

# Rest API Gateway Resource for Non Interactive Users
resource "aws_api_gateway_resource" "NonInteractiveUser_Resource" {
  parent_id   = aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.root_resource_id
  path_part   = "NonInteractiveUserResource"
  rest_api_id = aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id
  depends_on = [
    aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi
  ]
}

# Rest API for Non Interactive Users
resource "aws_api_gateway_rest_api" "NonInteractiveUser_SnowAwsApi" {
  api_key_source = "AUTHORIZER"
  description    = "APIs used for NonInteractiveUser"
  name           = "NonInteractiveUserAuth"
}

# Rest API Policy for Non Interactive Users
resource "aws_api_gateway_rest_api_policy" "noninteractive_user_snow_integartion_rest_api_policy" {
  rest_api_id = aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id
  policy      = data.aws_iam_policy_document.data_noninteractive_user_snow_integartion_rest_api_policy.json
}

# Rest API Key for Non Interactive Users
resource "aws_api_gateway_api_key" "NonInteractiveUser_Key" {
  description = "CloudFormation API Key V1"
  enabled     = true
  name        = "AWSNonInteractiveUserKey"
  depends_on = [
    aws_api_gateway_deployment.NonInteractiveUser_Deployment,
    aws_api_gateway_stage.stage
  ]
}

# Rest API stage for Non Interactive Users
resource "aws_api_gateway_stage" "stage" {
  cache_cluster_enabled = false
  deployment_id         = aws_api_gateway_deployment.NonInteractiveUser_Deployment.id
  rest_api_id           = aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id
  stage_name            = var.api_stage
  xray_tracing_enabled  = false
  depends_on = [
    aws_api_gateway_deployment.NonInteractiveUser_Deployment
  ]
}

# Rest API deployment for Non Interactive Users
resource "aws_api_gateway_deployment" "NonInteractiveUser_Deployment" {
  rest_api_id = aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id
  depends_on = [
    aws_api_gateway_method.NonInteractiveUser_PostMethod
  ]
}

# Rest API method settings for Non Interactive Users 
resource "aws_api_gateway_method_settings" "NonInteractiveUser_rest_api_method_settings" {
  rest_api_id = aws_api_gateway_rest_api.NonInteractiveUser_SnowAwsApi.id
  stage_name  = aws_api_gateway_stage.stage.stage_name
  method_path = "*/*"

  settings {
    logging_level   = "INFO"
    data_trace_enabled = true
    throttling_burst_limit = "5000"
    throttling_rate_limit = "10000"
  }
}

# Dynamo DB Table for Non Interactive Users
resource "aws_dynamodb_table" "NonInteractiveUserManagement_Table" {
  billing_mode   = "PROVISIONED"
  hash_key       = "RequestNumber"
  name           = "NonInteractiveUser_Management"
  range_key      = null
  read_capacity  = 10
  write_capacity = 10
  stream_enabled = false
  table_class    = "STANDARD"
  tags = {
    platform_donotdelete = "yes"
  }
  tags_all = {
    platform_donotdelete = "yes"
  }
  attribute {
    name = "RequestNumber"
    type = "S"
  }
  point_in_time_recovery {
    enabled = true
  }
}

# Snow Request Box FIFO Queue for Non Interactive Users
resource "aws_sqs_queue" "NonInteractiveUser_FIFOQueue" {
  content_based_deduplication       = true
  deduplication_scope               = "queue"
  delay_seconds                     = 0
  fifo_queue                        = true
  fifo_throughput_limit             = "perQueue"
  kms_data_key_reuse_period_seconds = 300
  max_message_size                  = 262144
  message_retention_seconds         = 345600
  name                              = "platform_noninteractive_user_snow_request_box.fifo"
  receive_wait_time_seconds         = 0
  sqs_managed_sse_enabled           = true
  tags = {
    platform_donotdelete = "yes"
  }
  tags_all = {
    platform_donotdelete = "yes"
  }
  visibility_timeout_seconds = 3960
}

# Eventbridge rule for Non Interactive Users
resource "aws_cloudwatch_event_rule" "NonInteractive_User_Schedule" {
  description         = "Scheduled to run the lambda every 5 minutes"
  is_enabled          = true
  name                = "platform_noninteractive_user_schedule"
  schedule_expression = "rate(5 minutes)"
  depends_on = [
    aws_lambda_function.NonInteractiveUser_Lambda_Invoker
  ]
}

resource "aws_cloudwatch_event_target" "NonInteractiveUser_Lambda_invoker_target" {
  rule      = aws_cloudwatch_event_rule.NonInteractive_User_Schedule.name
  target_id = var.cloudwatch_event_target_id
  arn       = aws_lambda_function.NonInteractiveUser_Lambda_Invoker.arn
}


