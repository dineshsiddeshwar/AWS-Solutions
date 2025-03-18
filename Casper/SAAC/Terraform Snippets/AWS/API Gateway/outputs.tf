output "aws_api_gateway_resource_path" {
  description = "The complete path for this API resource, including all parent paths."
  value       = aws_api_gateway_resource.api_gateway_resource.path
}
