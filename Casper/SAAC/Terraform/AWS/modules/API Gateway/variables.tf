variable "aws_region" {
  description = "Aws region where resource needs to be deployed"
  type        = string
}

# Tags used for common resource
variable "common_tags" {
  type        = map(string)
  description = "Default tags attached to all resources."
}

# Policy : Access to the Rest APIs is allowed to the trusted IP addresses only
variable "api_gateway_ip_address" {
  type = string
}
data "template_file" "api_gw_trust_id_policy" {
  template = file("policies/APIGatewayTrustIPPolicy.json")
  vars = {
    execution_arn = aws_api_gateway_rest_api.api_gateway_rest_api.execution_arn
    api_gateway_ip_address = var.api_gateway_ip_address
  }
}

variable "api_gateway_prefix" {
  type        = string
  description = "A prefix for all the resource"
}

variable "api_gateway_binary_media_types" {
  type        = list(string)
  description = "The list of binary media types supported by the RestApi. By default, the RestApi supports only UTF-8-encoded text payloads."
}

variable "api_gateway_minimum_compression_size" {
  type        = number
  description = "Minimum response size to compress for the REST API. Integer between -1 and 10485760 (10MB). Setting a value greater than -1 will enable compression, -1 disables compression (default)."
}

variable "api_gateway_types" {
  type        = list(string)
  description = "Whether to create rest api."
}

variable "api_gateway_vpc_endpoint_ids" {
  type        = set(string)
  description = "Set of VPC Endpoint identifiers. It is only supported for PRIVATE endpoint type."
}

variable "api_gateway_path_parts" {
  type        = string
  description = "The last path segment of this API resource."
}

variable "api_gateway_authorizations" {
  type        = string
  description = "The type of authorization used for the method (NONE, CUSTOM, AWS_IAM, COGNITO_USER_POOLS)."
}

variable "api_gateway_http_methods" {
  type        = string
  description = "The HTTP Method (GET, POST, PUT, DELETE, HEAD, OPTIONS, ANY)."
}

variable "api_gateway_method_path" {
  type        = string
  description = "Method path defined as {resource_path}/{http_method} for an individual method override, or */* for overriding all methods in the stage."
}

## Settings
variable "api_gateway_logging_level" {
  type        = string
  description = "Specifies the logging level for this method, which effects the log entries pushed to Amazon CloudWatch Logs. The available levels are OFF, ERROR, and INFO."
}

variable "api_gateway_data_trace_enabled" {
  type        = bool
  description = "Specifies whether data trace logging is enabled for this method, which effects the log entries pushed to Amazon CloudWatch Logs."
}

variable "api_gateway_metrics_enabled" {
  type        = bool
  description = " Specifies whether Amazon CloudWatch metrics are enabled for this method. (treu or false)"
}

variable "api_gateway_throttling_burst_limit" {
  type        = number
  description = "Specifies the throttling burst limit."
}

variable "api_gateway_throttling_rate_limit" {
  type        = number
  description = "Specifies the throttling rate limit."
}

variable "api_gateway_caching_enabled" {
  type        = bool
  description = "pecifies whether responses should be cached and returned for requests. A cache cluster must be enabled on the stage for responses to be cached."
}

variable "api_gateway_cache_ttl_in_seconds" {
  type        = number
  description = "Specifies the time to live (TTL), in seconds, for cached responses. The higher the TTL, the longer the response will be cached."
}

variable "api_gateway_cache_data_encrypted" {
  type        = bool
  description = "Specifies whether the cached responses are encrypted."
}

variable "api_gateway_require_authorization_for_cache_control" {
  type        = bool
  description = "Specifies whether authorization is required for a cache invalidation request."
}

variable "api_gateway_unauthorized_cache_control_header_strategy" {
  type        = string
  description = "Specifies how to handle unauthorized requests for cache invalidation. The available values are FAIL_WITH_403, SUCCEED_WITH_RESPONSE_HEADER, SUCCEED_WITHOUT_RESPONSE_HEADER."
}

variable "api_gateway_content_handling" {
  type        = string
  description = "Specifies how to handle request payload content type conversions. Supported values are CONVERT_TO_BINARY and CONVERT_TO_TEXT. If this property is not defined, the request payload will be passed through from the method request to integration request without modification, provided that the passthroughBehaviors is configured to support payload pass-through."
}

variable "api_gateway_integration_types" {
  type        = string
  description = "The integration input's type. Valid values are HTTP (for HTTP backends), MOCK (not calling any real backend), AWS (for AWS services), AWS_PROXY (for Lambda proxy integration) and HTTP_PROXY (for HTTP proxy integration). An HTTP or HTTP_PROXY integration with a connection_type of VPC_LINK is referred to as a private integration and uses a VpcLink to connect API Gateway to a network load balancer of a VPC."
}

variable "api_gateway_stage_name" {
  type        = string
  description = "The name of the stage."
}

variable "api_gateway_formats" {
  type        = string
  description = "The formatting and values recorded in the logs."
}

variable "cloudwatch_log_group_name" {
  type        = string
  description = " Name of the log group to send the logs to."
}

variable "api_gateway_vpc_link_names" {
  type        = string
  description = "The name used to label and identify the VPC link."
}

variable "api_gateway_vpc_link_descriptions" {
  type        = string
  description = "The description of the VPC link."
}

variable "api_gateway_target_arns" {
  type        = list(string)
  description = "The list of network load balancer arns in the VPC targeted by the VPC link. Currently AWS only supports 1 target."
}

# WAF Resource
data "aws_wafv2_web_acl" "api_gateway_wafv_web_acl" {
  name  = var.api_gateway_wafv_name
  scope = var.api_gateway_wafv_scope
}

variable "api_gateway_wafv_name" {
  type        = string
  description = "firewall name to get the deployed WAF to be intigrated with APIGW"
}

variable "api_gateway_wafv_scope" {
  type        = string
  description = "firewall scope to get the deployed WAF to be intigrated with APIGW"
}