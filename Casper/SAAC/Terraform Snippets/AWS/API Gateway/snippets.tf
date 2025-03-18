locals {
  gw_policy_trust_id_policy = data.template_file.api_gw_trust_id_policy.rendered
  gw_policy_least_privilege_policy = data.template_file.api_gw_least_privilege_access.rendered
}

resource "aws_api_gateway_rest_api" "api_gateway_rest_api" {
  name                     = var.api_gateway_prefix
  binary_media_types       = var.api_gateway_binary_media_types

  #  Ensure Content encoding feature enabled for API Gateways
  minimum_compression_size = var.api_gateway_minimum_compression_size

  #  Ensure API Gateways are deployed with private endpoints
  # reference existing vpc endpoints
  endpoint_configuration {
    types            = var.api_gateway_types
    vpc_endpoint_ids = var.api_gateway_vpc_endpoint_ids
  }

  # if using private DNS
  # private_dns_enabled = true
}

#  Ensure that access to the Rest APIs is allowed to the trusted IP addresses only
resource "aws_api_gateway_rest_api_policy" "gw_rest_api_policy" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  policy      = local.gw_policy_trust_id_policy
}

# create API Gateway resource on AWS.

resource "aws_api_gateway_resource" "aws_api_gateway_resource" {
  parent_id   = aws_api_gateway_rest_api.api_gateway_rest_api.root_resource_id
  path_part   = var.api_gateway_path_parts
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
}

# create Api Gateway Method resource on AWS.

resource "aws_api_gateway_method" "api_gateway_method" {
  authorization = var.api_gateway_authorizations #"NONE"
  http_method   = var.api_gateway_http_methods   #"GET"
  resource_id   = aws_api_gateway_resource.api_gateway_resource.id
  rest_api_id   = aws_api_gateway_rest_api.api_gateway_rest_api.id
}

# create API Gateway resource on AWS.

resource "aws_api_gateway_resource" "api_gateway_resource" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  parent_id   = aws_api_gateway_rest_api.api_gateway_rest_api.root_resource_id
  path_part   = var.api_gateway_path_parts
}


# create Api Gateway Method Settings resource on AWS.
resource "aws_api_gateway_method_settings" "api_gateway_method_setting" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  stage_name  = aws_api_gateway_stage.api_gateway_stage.stage_name
  method_path = var.api_gateway_method_path #"*/*"

  settings {
    logging_level                              = var.api_gateway_logging_level
    data_trace_enabled                         = var.api_gateway_data_trace_enabled
    metrics_enabled                            = var.api_gateway_metrics_enabled #  Ensure CloudWatch logging is enabled for API Gateways
    throttling_burst_limit                     = var.api_gateway_throttling_burst_limit
    throttling_rate_limit                      = var.api_gateway_throttling_rate_limit
    caching_enabled                            = var.api_gateway_caching_enabled
    cache_ttl_in_seconds                       = var.api_gateway_cache_ttl_in_seconds
    cache_data_encrypted                       = var.api_gateway_cache_data_encrypted #  Ensure all data at rest is encrypted
    require_authorization_for_cache_control    = var.api_gateway_require_authorization_for_cache_control
    unauthorized_cache_control_header_strategy = var.api_gateway_unauthorized_cache_control_header_strategy
  }
}

# create Api Gateway Integration resource on AWS.
resource "aws_api_gateway_integration" "api_gateway_integration" {
  http_method      = aws_api_gateway_method.api_gateway_method.http_method
  resource_id      = aws_api_gateway_resource.api_gateway_resource.id
  rest_api_id      = aws_api_gateway_rest_api.api_gateway_rest_api.id
  content_handling = var.api_gateway_content_handling
  type             = var.api_gateway_integration_types #"MOCK"
  depends_on       = [aws_api_gateway_method.api_gateway_method]
}


# create Api Gateway Deployment resource on AWS.

resource "aws_api_gateway_deployment" "api_gateway_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id

  triggers = {
    # NOTE: The configuration below will satisfy ordering considerations,
    #       but not pick up all future REST API changes. More advanced patterns
    #       are possible, such as using the filesha1() function against the
    #       Terraform configuration file(s) or removing the .id references to
    #       calculate a hash against whole resources. Be aware that using whole
    #       resources will show a difference after the initial implementation.
    #       It will stabilize to only change when resources change afterwards.
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.api_gateway_resource.id,
      aws_api_gateway_method.api_gateway_method.id,
      aws_api_gateway_integration.api_gateway_integration.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

# create Api Gateway Stage resource on AWS.

resource "aws_api_gateway_stage" "api_gateway_stage" {

  rest_api_id   = aws_api_gateway_rest_api.api_gateway_rest_api.id
  deployment_id = aws_api_gateway_deployment.api_gateway_deployment.id
  stage_name    = var.api_gateway_stage_names
}

# create Api Gateway Stage resource on AWS with logs enabled.

resource "aws_api_gateway_stage" "api_gateway_stage_with_log" {

  rest_api_id   = aws_api_gateway_rest_api.api_gateway_rest_api.id
  deployment_id = aws_api_gateway_deployment.api_gateway_deployment.id
  stage_name    = var.api_gateway_stage_names
  access_log_settings {
    destination_arn = var.api_gateway_destination_arns # "${aws_cloudwatch_log_group.example.arn}"
    format          = var.api_gateway_formats
  }
}

#  Ensure API Gateway resource policies enforce least privilege 

resource "aws_iam_policy" "api_gateway_user_policy" {
  name   = var.api_gateway_user_policy

  #  Ensure all data at transit is encrypted, implemented inside policy
  policy =  local.gw_policy_least_privilege_policy
}
resource "aws_iam_user_policy_attachment" "api_gateway_policy_attach" {
  user       = var.api_gateway_user_name
  policy_arn = aws_iam_policy.api_gateway_user_policy.arn
}

# create Api Gateway VPC Link resource on AWS.

resource "aws_api_gateway_vpc_link" "api_gateway_vpc_link" {

  name        = var.api_gateway_vpc_link_names
  description = var.api_gateway_vpc_link_descriptions

  # Ensure Network Load Balancer (NLB) is deployed with Private Link for access to internal resources
  target_arns = var.api_gateway_target_arns
}

# Ensure CloudTrail logging enabled 
# Cosidering  Cloudtrail deployed at the time of organization environment setup

# Ensure API gateway is integrated with AWS WAF to protect against common web exploits

resource "aws_wafv2_web_acl_association" "api_gateway_wafv_web_acl_association" {
  resource_arn = aws_api_gateway_stage.api_gateway_stage_with_log.arn
  web_acl_arn  = data.aws_wafv2_web_acl.api_gateway_wafv_web_acl.arn
}
