output "vpc_id" {
  description = "The ID of the VPC in which the specific VPC Endpoint is used"
  value       = aws_vpc_endpoint.ses_vpc_endpoint_id.id
}
