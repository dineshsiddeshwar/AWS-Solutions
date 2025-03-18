#Release Integration Log SSM
resource "aws_ssm_parameter" "vpc_snow_network_vpc_integration_log_bucket_parameter" {
  name  = "SnowNerworkVPCIntegrationLogBucket"
  type  = "String"
  value = var.SnowNerworkVPCIntegrationLogBucket
  tags = {
    "platform_donotdelete" = "yes"
  }
}
#VPC SNOW Integration Logging Bucket
resource "aws_s3_bucket" "vpc_snow_integration_logging_bucket" {
  bucket = var.SnowNerworkVPCIntegrationLogBucket

  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_s3_bucket_public_access_block" "vpc_snow_integration_logging_bucket_block_public_access" {
  bucket = aws_s3_bucket.vpc_snow_integration_logging_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "vpc_snow_integration_logging_bucket_lifecycle_configuration" {
  bucket = aws_s3_bucket.vpc_snow_integration_logging_bucket.id

  rule {
    id = "InventoryGlacierRule"

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

# requests Lambda Layer
resource "aws_lambda_layer_version" "vpc_snow_integration_lambda_layer" {
  filename   = "${path.module}/LambdaLayerZippedFiles/python.zip"
  layer_name = "SNOWVPCIntegrationRequests"
  description = "Requests Layer"
  skip_destroy = true
  compatible_runtimes = ["python3.9"]
}

# vpcVPC SNOW integration invoker lambda
resource "aws_lambda_function" "vpc_snow_integration_invoker_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_snow_networkvpc_integration_invoker.zip"
  function_name = "platform_snow_networkvpc_integration_invoker"
  role          = var.role_arn
  handler       = "platform_snow_networkvpc_integration_invoker.lambda_handler"
  source_code_hash = data.archive_file.vpc_snow_integration_invoker_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 128
  timeout = 900

  layers = [aws_lambda_layer_version.vpc_snow_integration_lambda_layer.arn]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

#VPC SNOW Integration Processing Lambda
resource "aws_lambda_function" "vpc_snow_integration_processing_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_snow_networkvpc_integration_processing.zip"
  function_name = "platform_snow_networkvpc_integration_processing"
  role          = var.role_arn
  handler       = "platform_snow_networkvpc_integration_processing.lambda_handler"
  source_code_hash = data.archive_file.vpc_snow_integration_processing_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 128
  timeout = 900

  layers = [aws_lambda_layer_version.vpc_snow_integration_lambda_layer.arn]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

#VPC SNOW Integration Receiver Lambda
resource "aws_lambda_function" "vpc_snow_integration_receiver_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_snow_networkvpc_integration_receiver.zip"
  function_name = "platform_snow_networkvpc_integration_receiver"
  role          = var.role_arn
  handler       = "platform_snow_networkvpc_integration_receiver.lambda_handler"
  source_code_hash = data.archive_file.vpc_snow_integration_receiver_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 128
  timeout = 900

  layers = [aws_lambda_layer_version.vpc_snow_integration_lambda_layer.arn]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

#VPC SNOW Intgeration Response Lambda
resource "aws_lambda_function" "vpc_snow_integration_response_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_snow_networkvpc_integration_response.zip"
  function_name = "platform_snow_networkvpc_integration_response"
  role          = var.role_arn
  handler       = "platform_snow_networkvpc_integration_response.lambda_handler"
  source_code_hash = data.archive_file.vpc_snow_integration_response_lambda_zip.output_base64sha256

  runtime = "python3.9"
  memory_size = 128
  timeout = 900

  layers = [aws_lambda_layer_version.vpc_snow_integration_lambda_layer.arn]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

#VPC SNOW Intgeration Authorizer Lambda
resource "aws_lambda_function" "vpc_snow_integration_authorizer_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_snow_networkvpc_integration_authorizer.zip"
  function_name = "platform_snow_networkvpc_integration_authorizer"
  role          = var.role_arn
  handler       = "platform_snow_networkvpc_integration_authorizer.lambda_handler"
  source_code_hash = data.archive_file.vpc_snow_integration_authorizer_lambda_zip.output_base64sha256
  
  runtime = "python3.9"
  memory_size = 128
  timeout = 900

  layers = [aws_lambda_layer_version.vpc_snow_integration_lambda_layer.arn]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

#VPC SNOW Integration Invoker Lambda Schedule
resource "aws_cloudwatch_event_rule" "vpc_snow_integration_invoker_lambda_schedule" {
  name = "platform_networkvpc_invoker_lamba_schedule"
  description = "Scheduled to run the lambda every 5 minutes"
  schedule_expression = "rate(5 minutes)"
  is_enabled = true
}

resource "aws_cloudwatch_event_target" "vpc_snow_integration_invoker_lambda_target" {
  rule      = aws_cloudwatch_event_rule.vpc_snow_integration_invoker_lambda_schedule.name
  target_id = "TargetFunctionV1"
  arn       = aws_lambda_function.vpc_snow_integration_invoker_lambda.arn
}

resource "aws_lambda_permission" "vpc_snow_integration_invoker_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.vpc_snow_integration_invoker_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.vpc_snow_integration_invoker_lambda_schedule.arn
}

#Snow Integration State Machine
resource "aws_sfn_state_machine" "vpc_snow_integration_state_machine" {
  name     = "platform_snow_networkvpc_integration_state_machine"
  role_arn = var.role_arn

  definition = data.template_file.vpc_snow_integration_state_machine_template.rendered
  type = "STANDARD" 
  tags = {
    "platform_donotdelete" = "yes"
  }
}

#VPC SNOW Request Box FIFO Queue
resource "aws_sqs_queue" "vpc_snow_request_box_fifo_queue" {
  name                      = "platform_snow_networkvpc_request_box.fifo"
  fifo_queue                = true
  visibility_timeout_seconds  = 3960
  content_based_deduplication  = true

  tags = {
    "platform_donotdelete" = "yes"
  }
}

#VPC SNOW Response Box FIFO Queue
resource "aws_sqs_queue" "vpc_snow_response_box_fifo_queue" {
  name                      = "platform_snow_networkvpc_response_box.fifo"
  fifo_queue                = true
  visibility_timeout_seconds  = 3960
  content_based_deduplication  = true

  tags = {
    "platform_donotdelete" = "yes"
  }
}

#VPC SNOW Lambda Function Event Source Mapping
resource "aws_lambda_event_source_mapping" "vpc_snow_integration_event_source_mapping" {
  event_source_arn = aws_sqs_queue.vpc_snow_response_box_fifo_queue.arn
  function_name    = aws_lambda_function.vpc_snow_integration_response_lambda.arn
  batch_size = 1
  enabled = true
}

#VPC SNOW Integration Rest API
resource "aws_api_gateway_rest_api" "vpc_snow_integration_rest_api" {
  name = "snow-networkvpc-api"
  description = "APIs used for Network provisioning from service-now requests"
  api_key_source = "AUTHORIZER"
  depends_on = [
    aws_lambda_function.vpc_snow_integration_invoker_lambda,
    aws_lambda_function.vpc_snow_integration_processing_lambda,
    aws_lambda_function.vpc_snow_integration_receiver_lambda,
    aws_lambda_function.vpc_snow_integration_authorizer_lambda,
    aws_lambda_function.vpc_snow_integration_response_lambda
 ]
}

#VPC SNOW Integration Rest API Policy
resource "aws_api_gateway_rest_api_policy" "vpc_snow_integration_rest_api_policy" {
  rest_api_id = aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id
  policy      = data.aws_iam_policy_document.data_vpc_snow_integration_rest_api_policy.json
}

#VPC SNOW Integration Rest API Resource
resource "aws_api_gateway_resource" "vpc_snow_integration_rest_api_resource" {
  rest_api_id = aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id
  parent_id   = aws_api_gateway_rest_api.vpc_snow_integration_rest_api.root_resource_id
  path_part   = "aws-networkvpc"
}

#VPC SNOW Integration Rest API Authorizer
resource "aws_api_gateway_authorizer" "vpc_snow_integration_rest_api_authorizer" {
  name                   = "api_key_authorizer"
  rest_api_id            = aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id
  authorizer_uri         = "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/${aws_lambda_function.vpc_snow_integration_authorizer_lambda.arn}/invocations"
  identity_source =  "method.request.querystring.apiKey"
  type = "REQUEST"
}

#VPC SNOW Integration Rest API Post Method
resource "aws_api_gateway_method" "vpc_snow_integration_rest_api_post_method" {
  rest_api_id   = aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id
  resource_id   = aws_api_gateway_resource.vpc_snow_integration_rest_api_resource.id
  authorizer_id = aws_api_gateway_authorizer.vpc_snow_integration_rest_api_authorizer.id
  http_method   = "POST"
  authorization = "CUSTOM"
  api_key_required = true
}

#VPC SNOW Integration Rest API Post Integration
resource "aws_api_gateway_integration" "vpc_snow_integration_rest_api_post_integration" {
  rest_api_id          = aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id
  resource_id          = aws_api_gateway_resource.vpc_snow_integration_rest_api_resource.id
  http_method = aws_api_gateway_method.vpc_snow_integration_rest_api_post_method.http_method
  integration_http_method = "POST"
  passthrough_behavior = "WHEN_NO_TEMPLATES"
  type = "AWS" 
  uri = "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/${aws_lambda_function.vpc_snow_integration_receiver_lambda.arn}/invocations"

  request_templates = {
    "application/json" = "#set($allParams=$input.params()){\"body-json\":$input.json('$'),\"params\":{#foreach($type in $allParams.keySet())#set($params=$allParams.get($type))\"$type\":{#foreach($paramName in $params.keySet())\"$paramName\":\"$util.escapeJavaScript($params.get($paramName))\"#if($foreach.hasNext),#end #end}#if($foreach.hasNext),#end #end},\"stage-variables\":{#foreach($key in $stageVariables.keySet())\"$key\":\"$util.escapeJavaScript($stageVariables.get($key))\"#if($foreach.hasNext),#end #end},\"context\":{\"account-id\":\"$context.identity.accountId\",\"api-id\":\"$context.apiId\",\"api-key\":\"$context.identity.apiKey\",\"authorizer-principal-id\":\"$context.authorizer.principalId\",\"caller\":\"$context.identity.caller\",\"cognito-authentication-provider\":\"$context.identity.cognitoAuthenticationProvider\",\"cognito-authentication-type\":\"$context.identity.cognitoAuthenticationType\",\"cognito-identity-id\":\"$context.identity.cognitoIdentityId\",\"cognito-identity-pool-id\":\"$context.identity.cognitoIdentityPoolId\",\"http-method\":\"$context.httpMethod\",\"stage\":\"$context.stage\",\"source-ip\":\"$context.identity.sourceIp\",\"user\":\"$context.identity.user\",\"user-agent\":\"$context.identity.userAgent\",\"user-arn\":\"$context.identity.userArn\",\"request-id\":\"$context.requestId\",\"resource-id\":\"$context.resourceId\",\"resource-path\":\"$context.resourcePath\"}}"
  } 

  depends_on = [ aws_api_gateway_method.vpc_snow_integration_rest_api_post_method ]
}

#VPC SNOW Integration Rest API Post Integration response
resource "aws_api_gateway_integration_response" "vpc_snow_integration_rest_api_post_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id
  resource_id = aws_api_gateway_resource.vpc_snow_integration_rest_api_resource.id
  http_method = aws_api_gateway_method.vpc_snow_integration_rest_api_post_method.http_method
  status_code = "200"

  response_templates = {
    "application/json" = ""
  }

  depends_on = [ aws_api_gateway_integration.vpc_snow_integration_rest_api_post_integration ]

  }

#VPC SNOW Integration Rest API Post Method response
resource "aws_api_gateway_method_response" "vpc_snow_integration_rest_api_post_method_response" {
  rest_api_id = aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id
  resource_id = aws_api_gateway_resource.vpc_snow_integration_rest_api_resource.id
  http_method = aws_api_gateway_method.vpc_snow_integration_rest_api_post_method.http_method
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }

  }

#VPC SNOW Integration Rest API Options Method
resource "aws_api_gateway_method" "vpc_snow_integration_rest_api_options_method" {
  rest_api_id   = aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id
  resource_id   = aws_api_gateway_resource.vpc_snow_integration_rest_api_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

#VPC SNOW Integration Rest API Options Integration
resource "aws_api_gateway_integration" "vpc_snow_integration_rest_api_options_integration" {
  rest_api_id          = aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id
  resource_id          = aws_api_gateway_resource.vpc_snow_integration_rest_api_resource.id
  http_method = aws_api_gateway_method.vpc_snow_integration_rest_api_options_method.http_method
  passthrough_behavior = "WHEN_NO_MATCH"
  type = "MOCK" 
  
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }

}

#VPC SNOW Integration Rest API Options Integration response
resource "aws_api_gateway_integration_response" "vpc_snow_integration_rest_api_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id
  resource_id = aws_api_gateway_resource.vpc_snow_integration_rest_api_resource.id
  http_method = aws_api_gateway_method.vpc_snow_integration_rest_api_options_method.http_method
  status_code = "200"

  response_templates = {
    "application/json" = ""
  }

  response_parameters = { 
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'" 
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }

  depends_on = [ aws_api_gateway_integration.vpc_snow_integration_rest_api_options_integration ]

  }

#VPC SNOW Integration Rest API Options Method response
resource "aws_api_gateway_method_response" "vpc_snow_integration_rest_api_options_method_response" {
  rest_api_id = aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id
  resource_id = aws_api_gateway_resource.vpc_snow_integration_rest_api_resource.id
  http_method = aws_api_gateway_method.vpc_snow_integration_rest_api_options_method.http_method
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

#VPC SNOW Integration Rest API deployment
resource "aws_api_gateway_deployment" "vpc_snow_integration_rest_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id
  lifecycle {
    create_before_destroy = true
  }

  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.vpc_snow_integration_rest_api.body))
  }
  depends_on = [
    aws_api_gateway_method.vpc_snow_integration_rest_api_post_method, aws_api_gateway_integration.vpc_snow_integration_rest_api_post_integration

 ]
}

#VPC SNOW Integration Rest API stage
resource "aws_api_gateway_stage" "vpc_snow_integration_rest_api_stage" {
  deployment_id = aws_api_gateway_deployment.vpc_snow_integration_rest_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id
  stage_name    = var.vpc_flow_bucket_env_type
}

#VPC SNOW Integration Rest API method settings
resource "aws_api_gateway_method_settings" "vpc_snow_integration_rest_api_method_settings" {
  rest_api_id = aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id
  stage_name  = aws_api_gateway_stage.vpc_snow_integration_rest_api_stage.stage_name
  method_path = "*/*"

  settings {
    logging_level   = "INFO"
    data_trace_enabled = true
    throttling_burst_limit = "5000"
    throttling_rate_limit = "10000"
  }
}

#VPC SNOW Integration Rest API Invoke permission for Receiver lambda
resource "aws_lambda_permission" "vpc_snow_integration_receiver_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.vpc_snow_integration_receiver_lambda.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:us-east-1:${var.master_account}:${aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id}/*/*/*"
}

#VPC SNOW Integration Rest API Invoke permission for Authorizer lambda
resource "aws_lambda_permission" "vpc_snow_integration_authorizer_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.vpc_snow_integration_authorizer_lambda.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:us-east-1:${var.master_account}:${aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id}/authorizers/${aws_api_gateway_authorizer.vpc_snow_integration_rest_api_authorizer.id}"
}

#VPC SNOW Integration Rest API Key
resource "aws_api_gateway_api_key" "vpc_snow_integration_rest_api_key" {
  name = "SnowToAwsNetworkVPCApiKey"
  description = "CloudFormation API Key V1"
  enabled = true
  depends_on = [
    aws_api_gateway_deployment.vpc_snow_integration_rest_api_deployment,
    aws_api_gateway_stage.vpc_snow_integration_rest_api_stage
 ]
}

#VPC SNOW Integration Rest API Gateway usage plan
resource "aws_api_gateway_usage_plan" "vpc_snow_integration_api_gateway_usage_plan" {
  name         = "SnowAwsNetworkVPCApiUsagePlan"
  description  = "Usage plan for the sake of using api key"

  api_stages {
    api_id = aws_api_gateway_rest_api.vpc_snow_integration_rest_api.id
    stage  = aws_api_gateway_stage.vpc_snow_integration_rest_api_stage.stage_name
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

#VPC SNOW Integration Rest API Gateway usage plan key
resource "aws_api_gateway_usage_plan_key" "vpc_snow_integration_api_gateway_usage_plan_key" {
  key_id        = aws_api_gateway_api_key.vpc_snow_integration_rest_api_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.vpc_snow_integration_api_gateway_usage_plan.id
}
