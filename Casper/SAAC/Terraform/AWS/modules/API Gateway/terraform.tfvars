# Aws region where resource needs to be deployed
aws_region = "__AWS_REGION__"

# A prefix for all the resource
api_gateway_prefix = "__API_GATEWAY_PREFIX__"

api_gateway_ip_address = "__API_GATEWAY_IP_ADDRESS__"

# The list of binary media types supported by the RestApi. By default, the RestApi supports only UTF-8-encoded text payloads.
api_gateway_binary_media_types = ["__API_GATEWAY_BINARY_MEDIA_TYPES__"]

# Minimum response size to compress for the REST API. Integer between -1 and 10485760 (10MB). Setting a value greater than -1 will enable compression, -1 disables compression (default).
api_gateway_minimum_compression_size = 0

# Whether to create rest api.
api_gateway_types = ["__API_GATEWAY_TYPES__"]

# Set of VPC Endpoint identifiers. It is only supported for PRIVATE endpoint type.
api_gateway_vpc_endpoint_ids = ["__API_GATEWAY_VPC_ENDPOINT_IDS__"]

# The last path segment of this API resource.
api_gateway_path_parts = "__API_GATEWAY_PATH_PARTS__"

# The HTTP Method (GET, POST, PUT, DELETE, HEAD, OPTIONS, ANY).
api_gateway_http_methods = "__API_GATEWAY_HTTP_METHODS__"

# The type of authorization used for the method (NONE, CUSTOM, AWS_IAM, COGNITO_USER_POOLS).
api_gateway_authorizations = "__API_GATEWAY_AUTHORIZATIONS__"

# The integration input's type. Valid values are HTTP (for HTTP backends), MOCK (not calling any real backend), AWS (for AWS services), AWS_PROXY (for Lambda proxy integration) and HTTP_PROXY (for HTTP proxy integration). An HTTP or HTTP_PROXY integration with a connection_type of VPC_LINK is referred to as a private integration and uses a VpcLink to connect API Gateway to a network load balancer of a VPC.
api_gateway_integration_types = "__API_GATEWAY_INTEGRATION_TYPES__"

# The name of the stage.
api_gateway_stage_name = "__API_GATEWAY_STAGE_NAME__"

# Name of the log group to send the logs to.
cloudwatch_log_group_name = "__cloudwatch_log_group_name__"

# The formatting and values recorded in the logs.
api_gateway_formats = "__API_GATEWAY_FORMATS__"

# The name used to label and identify the VPC link.
api_gateway_vpc_link_names = "__API_GATEWAY_VPC_LINK_NAMES__"

# The description of the VPC link.
api_gateway_vpc_link_descriptions = "__API_GATEWAY_VPC_LINK_DESCRIPTIONS__"

# The list of network load balancer arns in the VPC targeted by the VPC link. Currently AWS only supports 1 target.
api_gateway_target_arns = ["__API_GATEWAY_TARGET_ARNS__"]

# Method path defined as {resource_path}/{http_method} for an individual method override, or */* for overriding all methods in the stage.
api_gateway_method_path = "__API_GATEWAY_METHOD_PATH__"

#  Specifies whether Amazon CloudWatch metrics are enabled for this method. (treu or false)
api_gateway_metrics_enabled = false

# Specifies the logging level for this method, which effects the log entries pushed to Amazon CloudWatch Logs. The available levels are OFF, ERROR, and INFO.
api_gateway_logging_level = "__API_GATEWAY_LOGGING_LEVEL__"

# Specifies whether data trace logging is enabled for this method, which effects the log entries pushed to Amazon CloudWatch Logs.
api_gateway_data_trace_enabled = false

# Specifies the throttling burst limit.
api_gateway_throttling_burst_limit = -1

# Specifies the throttling rate limit.
api_gateway_throttling_rate_limit = -1

# pecifies whether responses should be cached and returned for requests. A cache cluster must be enabled on the stage for responses to be cached.
api_gateway_caching_enabled = false

# Specifies the time to live (TTL), in seconds, for cached responses. The higher the TTL, the longer the response will be cached.
api_gateway_cache_ttl_in_seconds = 0

# Specifies whether the cached responses are encrypted.
api_gateway_cache_data_encrypted = true

# Specifies whether authorization is required for a cache invalidation request.
api_gateway_require_authorization_for_cache_control = true

# Specifies how to handle unauthorized requests for cache invalidation. The available values are FAIL_WITH_403, SUCCEED_WITH_RESPONSE_HEADER, SUCCEED_WITHOUT_RESPONSE_HEADER.
api_gateway_unauthorized_cache_control_header_strategy = "__API_GATEWAY_UNAUTHORIZED_CACHE_CONTROL_HEADER_STRATEGY__"

# Specifies how to handle request payload content type conversions. Supported values are CONVERT_TO_BINARY and CONVERT_TO_TEXT. If this property is not defined, the request payload will be passed through from the method request to integration request without modification, provided that the passthroughBehaviors is configured to support payload pass-through.
api_gateway_content_handling = "__API_GATEWAY_CONTENT_HANDLING__"

# firewall name to get the deployed WAF to be intigrated with APIGW
api_gateway_wafv_name = "__API_GATEWAY_WAFV2_NAME__"

# firewall scope to get the deployed WAF to be intigrated with APIGW
api_gateway_wafv_scope = "__API_GATEWAY_WAFV2_SCOPE__"

common_tags = {
    env-type = "__ENV_TYPE__" # "dev"  - For example only, Replace it with Application specific value
}
