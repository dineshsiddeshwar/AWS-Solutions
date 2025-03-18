# AWS Provider variable
data "aws_caller_identity" "current" {}

# VPC Input Variables
data "aws_vpc" "api_gateway_vpc" {
  id = var.api_gateway_vpc_id
}

variable "aws_region" {
  description = "Aws region where resource needs to be deployed"
  type        = string
}

variable "api_gateway_key_arn" {
  description = "The name of the key arn"
  type        = string
}

variable "api_gateway_alias_name" {
  description = "The name of the key alias"
  type        = string
}

# Tags used for common resource
variable "common_tags" {
  type        = map(string)
  description = "Default tags attached to all resources."
}

variable "api_gateway_prefix" {
  type        = string
  description = "A prefix for all the resource"
}

variable "api_gateway_vpc_id" {
  type        = string
  description = "VPC Id of the deployed VPC, can be found on Confluence page AWS VPC CIDR Deployed (Auto updated)"
}

variable "api_gateway_user_name" {
  type        = string
  description = "the iam user name of the gateway user"
}

variable "api_gateway_service_name" {
  type        = string
  description = "Enter service name for VPC endpoint"
}

variable "api_gateway_vpc_endpoint_type" {
  type        = string
  description = "Enter type of VPC endpoint like Interface , Gateway etc"
}

# Policy : Access to the Rest APIs is allowed to the trusted IP addresses only
data "template_file" "api_gw_trust_id_policy" {
  template = file("policies/APIGatewayTrustIPPolicy.json")
  vars = {
    execution_arn = aws_api_gateway_rest_api.api_gateway_rest_api.execution_arn
    api_gateway_ip_address = var.api_gateway_ip_address
  }
}

variable "api_gateway_ip_address" {
  type = string
}

variable "api_gateway_bucket" {
  type        = string
  description = "The name of the bucket. If omitted, Terraform will assign a random, unique name."
}

variable "api_gateway_expiration_days" {
  description = "The number of days log files will stay in the bucket"
}

variable "api_gateway_waf_metric_name" {
  type = string
}


variable "api_gateway_description" {
  type        = string
  description = "The description of the REST API "
}

variable "api_gateway_binary_media_types" {
  type        = list(string)
  description = "The list of binary media types supported by the RestApi. By default, the RestApi supports only UTF-8-encoded text payloads."
}

variable "api_gateway_minimum_compression_size" {
  type        = number
  description = "Minimum response size to compress for the REST API. Integer between -1 and 10485760 (10MB). Setting a value greater than -1 will enable compression, -1 disables compression (default)."
}

variable "api_gateway_api_key_source" {
  type        = string
  description = "The source of the API key for requests. Valid values are HEADER (default) and AUTHORIZER."
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

# Policy : API Gateway resource policies enforce least privilege 
data "template_file" "api_gw_least_privilege_access" {
  template = file("policies/APIGatewayLeastPrivilegeAccess.json")
  vars = {
    api_gateway_role         = var.api_gateway_role
    api_gateway_arn          = var.api_gateway_arn
    api_gateway_specific_api = var.api_gateway_specific_api
    vpc_endpoint_id          = data.aws_vpc.api_gateway_vpc.id
  }
}

variable "api_gateway_role" {
  type        = string
  description = "Enter the name for api gateway user principal."
}

variable "api_gateway_arn" {
  type        = string
  description = "Enter the name for api gateway resource arn"
}

variable "api_gateway_user_policy" {
  type        = string
  description = "Enter the name for api gateway user policy."
}

variable "api_gateway_specific_api" {
  type        = string
  description = "Enter the name for api gateway specific apis "
}

variable "api_gateway_stage_name" {
  type        = string
  description = "The name of the stage. If the specified stage already exists, it will be updated to point to the new deployment. If the stage does not exist, a new one will be created and point to this deployment."
}

variable "api_gateway_stage_description" {
  type        = string
  description = "The description of the stage."
}

variable "api_gateway_variables" {
  type        = map(string)
  description = "A map that defines variables for the stage."
}

variable "api_gateway_http_methods" {
  type        = string
  description = "The HTTP Method (GET, POST, PUT, DELETE, HEAD, OPTIONS, ANY)."
}

variable "api_gateway_authorizations" {
  type        = string
  description = "The type of authorization used for the method (NONE, CUSTOM, AWS_IAM, COGNITO_USER_POOLS)."
}

variable "api_gateway_integration_http_methods" {
  type        = string
  description = "The integration HTTP method (GET, POST, PUT, DELETE, HEAD, OPTIONs, ANY, PATCH) specifying how API Gateway will interact with the back end. Required if type is AWS, AWS_PROXY, HTTP or HTTP_PROXY. Not all methods are compatible with all AWS integrations. e.g. Lambda function can only be invoked via POST."
}

variable "api_gateway_integration_types" {
  type        = string
  description = "The integration input's type. Valid values are HTTP (for HTTP backends), MOCK (not calling any real backend), AWS (for AWS services), AWS_PROXY (for Lambda proxy integration) and HTTP_PROXY (for HTTP proxy integration). An HTTP or HTTP_PROXY integration with a connection_type of VPC_LINK is referred to as a private integration and uses a VpcLink to connect API Gateway to a network load balancer of a VPC."
}

variable "api_gateway_connection_types" {
  type        = string
  description = "The integration input's connectionType. Valid values are INTERNET (default for connections through the public routable internet), and VPC_LINK (for private connections between API Gateway and a network load balancer in a VPC)."
}

variable "api_gateway_stage_names" {
  type        = string
  description = "The name of the stage."
}


variable "api_gateway_destination_arns" {
  type        = string
  description = "ARN of the log group to send the logs to. Automatically removes trailing :* if present."
}

variable "api_gateway_formats" {
  type        = string
  description = "The formatting and values recorded in the logs."
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

variable "api_gateway_method_path" {
  type        = string
  description = "Method path defined as {resource_path}/{http_method} for an individual method override, or */* for overriding all methods in the stage."
}


## Settings
variable "api_gateway_metrics_enabled" {
  type        = bool
  description = " Specifies whether Amazon CloudWatch metrics are enabled for this method. (treu or false)"
}

variable "api_gateway_logging_level" {
  type        = string
  description = "Specifies the logging level for this method, which effects the log entries pushed to Amazon CloudWatch Logs. The available levels are OFF, ERROR, and INFO."
}

variable "api_gateway_data_trace_enabled" {
  type        = bool
  description = "Specifies whether data trace logging is enabled for this method, which effects the log entries pushed to Amazon CloudWatch Logs."
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

variable "api_gateway_wafv_name" {
  type        = string
  description = "firewall name to get the deployed WAF to be intigrated with APIGW"
}

variable "api_gateway_wafv_scope" {
  type        = string
  description = "firewall scope to get the deployed WAF to be intigrated with APIGW"
}

# WAF Resource
data "aws_wafv2_web_acl" "api_gateway_wafv_web_acl" {
  name  = var.api_gateway_wafv_name
  scope = var.api_gateway_wafv_scope
}
