#----------------------------------------------------------------------
# SSM Parameter store 
#----------------------------------------------------------------------
# SSM Parameter store 
resource "aws_ssm_parameter" "private_prod_ou_id_parameter" {
  name  = "platform_private_ou_id"
  type  = "String"
  value = var.private_production_ou
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_ssm_parameter" "public_prod_ou_id_parameter" {
  name  = "platform_public_ou_id"
  type  = "String"
  value = var.public_production_ou
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_ssm_parameter" "hybrid_prod_ou_id_parameter" {
  name  = "platform_hybrid_ou_id"
  type  = "String"
  value = var.hybrid_account_ou
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_ssm_parameter" "private_exception_ou_id_parameter" {
  name  = "platform_private_exception_ou_id"
  type  = "String"
  value = var.private_exception_ou
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_ssm_parameter" "public_exception_ou_id_parameter" {
  name  = "platform_public_exception_ou_id"
  type  = "String"
  value = var.public_exception_ou
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_ssm_parameter" "main_policy_id_public_parameter" {
  name  = "platform_service_whitelist_policy_public"
  type  = "String"
  value = var.main_policy_id_public
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_ssm_parameter" "main_policy_id_private_parameter" {
  name  = "platform_service_whitelist_policy_private"
  type  = "String"
  value = var.main_policy_id_private
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_ssm_parameter" "main_policy_id_hybrid_parameter" {
  name  = "platform_service_whitelist_policy_hybrid"
  type  = "String"
  value = var.main_policy_id_hybrid
  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_ssm_parameter" "titan_dl_parameter" {
  name  = "tital_dl"
  type  = "String"
  value = var.titan_team_dl
  tags = {
    "platform_donotdelete" = "yes"
  }
}

#----------------------------------------------------------------------
#-----------------------------------------------------------------------
# API Gateway resources and Receiver Lambda
#-----------------------------------------------------------------------

# requests Lambda Layer
resource "aws_lambda_layer_version" "scp_exception_requests_lambda_layer" {
  filename   = "${path.module}/LambdaLayerZippedFiles/python.zip"
  layer_name = "SCPRequests"
  description = "SCP Exception HTTPS Requests Layer"
  skip_destroy = true
  compatible_runtimes = ["python3.10"]
}

# SCP Exception Receiver Lambda
resource "aws_lambda_function" "scp_exception_receiver_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_scp_exception_reciever.zip"
  function_name = "platform_scp_exception_reciever"
  role          = var.role_arn
  handler       = "platform_scp_exception_reciever.lambda_handler"
  source_code_hash = data.archive_file.scp_exception_receiver_lambda_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900

  layers = [aws_lambda_layer_version.scp_exception_requests_lambda_layer.arn]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SCP Exception Rest API
resource "aws_api_gateway_rest_api" "scp_exception_rest_api" {
  name = "SCPSnowAPI"
  description = "APIs used for service-now Service whitelisting at SCP"
  api_key_source = "AUTHORIZER"
  depends_on = [
    aws_lambda_function.scp_exception_receiver_lambda
 ]
}

# SCP Exception Rest API Policy
resource "aws_api_gateway_rest_api_policy" "scp_exception_rest_api_policy" {
  rest_api_id = aws_api_gateway_rest_api.scp_exception_rest_api.id
  policy      = data.aws_iam_policy_document.data_scp_exception_rest_api_policy.json
}

# SCP Exception Rest API Resource
resource "aws_api_gateway_resource" "scp_exception_rest_api_resource" {
  rest_api_id = aws_api_gateway_rest_api.scp_exception_rest_api.id
  parent_id   = aws_api_gateway_rest_api.scp_exception_rest_api.root_resource_id
  path_part   = "SCPResource"
}

# SCP Exception Rest API Authorizer
resource "aws_api_gateway_authorizer" "scp_exception_rest_api_authorizer" {
  name                   = "api_key_authorizer"
  rest_api_id            = aws_api_gateway_rest_api.scp_exception_rest_api.id
  authorizer_uri         = "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:${var.master_account}:function:platform_snow_integration_authorizer/invocations"
  identity_source =  "method.request.querystring.apiKey"
  type = "REQUEST"
}

# SCP Exception Rest API Post Method
resource "aws_api_gateway_method" "scp_exception_rest_api_post_method" {
  rest_api_id   = aws_api_gateway_rest_api.scp_exception_rest_api.id
  resource_id   = aws_api_gateway_resource.scp_exception_rest_api_resource.id
  authorizer_id = aws_api_gateway_authorizer.scp_exception_rest_api_authorizer.id
  http_method   = "POST"
  authorization = "CUSTOM"
  api_key_required = true
}

# SCP Exception Rest API Post Integration
resource "aws_api_gateway_integration" "scp_exception_rest_api_post_integration" {
  rest_api_id          = aws_api_gateway_rest_api.scp_exception_rest_api.id
  resource_id          = aws_api_gateway_resource.scp_exception_rest_api_resource.id
  http_method = aws_api_gateway_method.scp_exception_rest_api_post_method.http_method
  integration_http_method = "POST"
  passthrough_behavior = "WHEN_NO_TEMPLATES"
  type = "AWS" 
  uri = "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/${aws_lambda_function.scp_exception_receiver_lambda.arn}/invocations"
}

# SCP Exception Rest API Post Integration response
resource "aws_api_gateway_integration_response" "scp_exception_rest_api_post_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.scp_exception_rest_api.id
  resource_id = aws_api_gateway_resource.scp_exception_rest_api_resource.id
  http_method = "POST"
  status_code = "200"

  response_templates = {
    "application/json" = ""
  }
}

# SCP Exception Rest API Post Method response
resource "aws_api_gateway_method_response" "scp_exception_rest_api_post_method_response" {
  rest_api_id = aws_api_gateway_rest_api.scp_exception_rest_api.id
  resource_id = aws_api_gateway_resource.scp_exception_rest_api_resource.id
  http_method = "POST"
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }
}

# SCP Exception Rest API Options Method
resource "aws_api_gateway_method" "scp_exception_rest_api_options_method" {
  rest_api_id   = aws_api_gateway_rest_api.scp_exception_rest_api.id
  resource_id   = aws_api_gateway_resource.scp_exception_rest_api_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

# SCP Exception Rest API Options Integration
resource "aws_api_gateway_integration" "scp_exception_rest_api_options_integration" {
  rest_api_id          = aws_api_gateway_rest_api.scp_exception_rest_api.id
  resource_id          = aws_api_gateway_resource.scp_exception_rest_api_resource.id
  http_method = aws_api_gateway_method.scp_exception_rest_api_options_method.http_method
  passthrough_behavior = "WHEN_NO_MATCH"
  type = "MOCK" 
  
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

# SCP Exception Rest API Options Integration response
resource "aws_api_gateway_integration_response" "scp_exception_rest_api_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.scp_exception_rest_api.id
  resource_id = aws_api_gateway_resource.scp_exception_rest_api_resource.id
  http_method = "OPTIONS"
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

# SCP Exception Rest API Options Method response
resource "aws_api_gateway_method_response" "scp_exception_rest_api_options_method_response" {
  rest_api_id = aws_api_gateway_rest_api.scp_exception_rest_api.id
  resource_id = aws_api_gateway_resource.scp_exception_rest_api_resource.id
  http_method = "OPTIONS"
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

# SCP Exception Rest API deployment
resource "aws_api_gateway_deployment" "scp_exception_rest_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.scp_exception_rest_api.id
  depends_on = [
    aws_api_gateway_method.scp_exception_rest_api_post_method
 ]
}

# SCP Exception Rest API stage
resource "aws_api_gateway_stage" "scp_exception_rest_api_stage" {
  deployment_id = aws_api_gateway_deployment.scp_exception_rest_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.scp_exception_rest_api.id
  stage_name    = var.scp_env_type
}

# SCP Exception Rest API method settings
resource "aws_api_gateway_method_settings" "scp_exception_rest_api_method_settings" {
  rest_api_id = aws_api_gateway_rest_api.scp_exception_rest_api.id
  stage_name  = aws_api_gateway_stage.scp_exception_rest_api_stage.stage_name
  method_path = "*/*"

  settings {
    logging_level   = "INFO"
    data_trace_enabled = true
    throttling_burst_limit = "5000"
    throttling_rate_limit = "10000"
  }
}

# SCP Exception Rest API Invoke permission for Receiver lambda
resource "aws_lambda_permission" "scp_exception_receiver_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scp_exception_receiver_lambda.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:us-east-1:${var.master_account}:${aws_api_gateway_rest_api.scp_exception_rest_api.id}/*/*/*"
}

# SCP Exception Rest API Invoke permission for Authorizer lambda
resource "aws_lambda_permission" "scp_exception_authorizer_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = "arn:aws:lambda:us-east-1:${var.master_account}:function:platform_snow_integration_authorizer"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:us-east-1:${var.master_account}:${aws_api_gateway_rest_api.scp_exception_rest_api.id}/authorizers/${aws_api_gateway_authorizer.scp_exception_rest_api_authorizer.id}"
}

# SCP Exception Rest API Key
resource "aws_api_gateway_api_key" "scp_exception_rest_api_key" {
  name = "AWSSCPKey"
  description = "CloudFormation API Key V1"
  enabled = true
  depends_on = [
    aws_api_gateway_deployment.scp_exception_rest_api_deployment,
    aws_api_gateway_stage.scp_exception_rest_api_stage
 ]
}

# SCP Exception Rest API Gateway usage plan
resource "aws_api_gateway_usage_plan" "scp_exception_api_gateway_usage_plan" {
  name         = "SCPSnowAwsApiUsagePlan"
  description  = "Usage plan for the sake of using api key"

  api_stages {
    api_id = aws_api_gateway_rest_api.scp_exception_rest_api.id
    stage  = aws_api_gateway_stage.scp_exception_rest_api_stage.stage_name
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

# SCP Exception Rest API Gateway usage plan key
resource "aws_api_gateway_usage_plan_key" "scp_exception_api_gateway_usage_plan_key" {
  key_id        = aws_api_gateway_api_key.scp_exception_rest_api_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.scp_exception_api_gateway_usage_plan.id
}

#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
# SQS queue
#-------------------------------------------------------------------------

# SCP Exception Request Box FIFO Queue
resource "aws_sqs_queue" "scp_exception_request_box_fifo_queue" {
  name                      = "platform_scp_snow_request_box.fifo"
  fifo_queue                = true
  visibility_timeout_seconds  = 3960
  content_based_deduplication  = true

  tags = {
    "platform_donotdelete" = "yes"
  }
}

#------------------------------------------------------------------------

#------------------------------------------------------------------------
# Invoker lambda and the event rule
#------------------------------------------------------------------------

# SCP Exception invoker lambda
resource "aws_lambda_function" "scp_exception_invoker_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_scp_exception_management_invoker.zip"
  function_name = "platform_scp_exception_management_invoker"
  role          = var.role_arn
  handler       = "platform_scp_exception_management_invoker.lambda_handler"
  source_code_hash = data.archive_file.scp_exception_invoker_lambda_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SCP Exception Invoker Lambda Schedule
resource "aws_cloudwatch_event_rule" "scp_exception_invoker_lambda_schedule" {
  name = "platform_SCP_Management_schedule"
  description = "Scheduled to run the lambda every 5 minutes"
  schedule_expression = "rate(5 minutes)"
  is_enabled = true
}

resource "aws_cloudwatch_event_target" "scp_exception_invoker_lambda_target" {
  rule      = aws_cloudwatch_event_rule.scp_exception_invoker_lambda_schedule.name
  target_id = "TargetFunctionV1"
  arn       = aws_lambda_function.scp_exception_invoker_lambda.arn
}

resource "aws_lambda_permission" "scp_exception_invoker_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scp_exception_invoker_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scp_exception_invoker_lambda_schedule.arn
}

#-------------------------------------------------------------------------------------
# Expiration handler resources
#-------------------------------------------------------------------------------------

# SCP Exception Expiry handler Lambda
resource "aws_lambda_function" "scp_exception_expiry_handler_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_scp_exception_expiry_handler.zip"
  function_name = "platform_scp_exception_expiry_handler"
  role          = var.role_arn
  handler       = "platform_scp_exception_expiry_handler.lambda_handler"
  source_code_hash = data.archive_file.scp_exception_expiry_handler_lambda_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SCP Exception Expiry handler Lambda Schedule
resource "aws_cloudwatch_event_rule" "scp_exception_expiry_handler_lambda_schedule" {
  name = "platform_SCP_Management_Expiration_schedule"
  description = "Scheduled to run the lambda every Day at 10AM"
  schedule_expression = "cron(0 10 * * ? *)"
  is_enabled = true
}

resource "aws_cloudwatch_event_target" "scp_exception_expiry_handler_lambda_target" {
  rule      = aws_cloudwatch_event_rule.scp_exception_expiry_handler_lambda_schedule.name
  target_id = "TargetFunctionV1"
  arn       = aws_lambda_function.scp_exception_expiry_handler_lambda.arn
}

resource "aws_lambda_permission" "scp_exception_expiry_handler_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scp_exception_expiry_handler_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scp_exception_expiry_handler_lambda_schedule.arn
}

#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------
# Creation of Dynamo DB table
#-------------------------------------------------------------------------------------

# SCP Management Table 
resource "aws_dynamodb_table" "scp_mgmnt_dynamodb_table" {
  name           = "SCP_Exception_Management"
  read_capacity  = 10
  write_capacity = 10
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

#-----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------
# state machine resource lambda
#-----------------------------------------------------------------------------------------

# SCP Exception Get OU details Lambda
resource "aws_lambda_function" "scp_exception_get_ou_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_scp_get_ou_details.zip"
  function_name = "platform_scp_get_ou_details"
  role          = var.role_arn
  handler       = "platform_scp_get_ou_details.lambda_handler"
  source_code_hash = data.archive_file.scp_exception_get_ou_lambda_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SCP Exception adhoc Lambda
resource "aws_lambda_function" "scp_exception_adhoc_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_adhoc_scp_exception_management.zip"
  function_name = "platform_adhoc_scp_exception_management"
  role          = var.role_arn
  handler       = "platform_adhoc_scp_exception_management.lambda_handler"
  source_code_hash = data.archive_file.scp_exception_adhoc_lambda_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SCP Exception Move Account Lambda
resource "aws_lambda_function" "scp_exception_move_account_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_scp_move_account.zip"
  function_name = "platform_scp_move_account"
  role          = var.role_arn
  handler       = "platform_scp_move_account.lambda_handler"
  source_code_hash = data.archive_file.scp_exception_move_account_lambda_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SCP Exception check ou Lambda
resource "aws_lambda_function" "scp_exception_check_ou_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_scp_check_ou.zip"
  function_name = "platform_scp_check_ou"
  role          = var.role_arn
  handler       = "platform_scp_check_ou.lambda_handler"
  source_code_hash = data.archive_file.scp_exception_check_ou_lambda_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SCP Exception check status Lambda
resource "aws_lambda_function" "scp_exception_check_status_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_scp_check_status.zip"
  function_name = "platform_scp_check_status"
  role          = var.role_arn
  handler       = "platform_scp_check_status.lambda_handler"
  source_code_hash = data.archive_file.scp_exception_check_status_lambda_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SCP Exception create policy Lambda
resource "aws_lambda_function" "scp_exception_create_policy_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_scp_create_policy.zip"
  function_name = "platform_scp_create_policy"
  role          = var.role_arn
  handler       = "platform_scp_create_policy.lambda_handler"
  source_code_hash = data.archive_file.scp_exception_create_policy_lambda_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SCP Exception update policy Lambda
resource "aws_lambda_function" "scp_exception_update_policy_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_scp_update_policy.zip"
  function_name = "platform_scp_update_policy"
  role          = var.role_arn
  handler       = "platform_scp_update_policy.lambda_handler"
  source_code_hash = data.archive_file.scp_exception_update_policy_lambda_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SCP Exception update db Lambda
resource "aws_lambda_function" "scp_exception_update_db_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_scp_update_db.zip"
  function_name = "platform_scp_update_db"
  role          = var.role_arn
  handler       = "platform_scp_update_db.lambda_handler"
  source_code_hash = data.archive_file.scp_exception_update_db_lambda_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SCP Exception snow response Lambda
resource "aws_lambda_function" "scp_exception_snow_response_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_scp_send_snow_response.zip"
  function_name = "platform_scp_send_snow_response"
  role          = var.role_arn
  handler       = "platform_scp_send_snow_response.lambda_handler"
  source_code_hash = data.archive_file.scp_exception_snow_response_lambda_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900

  layers = [aws_lambda_layer_version.scp_exception_requests_lambda_layer.arn]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SCP Exception send success email Lambda
resource "aws_lambda_function" "scp_exception_send_success_email_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_scp_send_success_email.zip"
  function_name = "platform_scp_send_success_email"
  role          = var.role_arn
  handler       = "platform_scp_send_success_email.lambda_handler"
  source_code_hash = data.archive_file.scp_exception_send_success_email_lambda_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900
  
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SCP Exception send failed email Lambda
resource "aws_lambda_function" "scp_exception_send_failed_email_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_scp_send_failure_email.zip"
  function_name = "platform_scp_send_failure_email"
  role          = var.role_arn
  handler       = "platform_scp_send_failure_email.lambda_handler"
  source_code_hash = data.archive_file.scp_exception_send_failed_email_lambda_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900
  
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SCP Exception valiadate ou Lambda
resource "aws_lambda_function" "scp_exception_validate_ou_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_scp_validate_ou.zip"
  function_name = "platform_scp_validate_ou"
  role          = var.role_arn
  handler       = "platform_scp_validate_ou.lambda_handler"
  source_code_hash = data.archive_file.scp_exception_validate_ou_lambda_zip.output_base64sha256

  runtime = "python3.10"
  memory_size = 128
  timeout = 900
  
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SCP Exception State Machine
resource "aws_sfn_state_machine" "scp_exception_state_machine" {
  name     = "platform_SCPStatemachine"
  role_arn = var.role_arn

  definition = data.template_file.scp_exception_state_machine_template.rendered
  type = "STANDARD" 
  tags = {
    "platform_donotdelete" = "yes"
  }
}