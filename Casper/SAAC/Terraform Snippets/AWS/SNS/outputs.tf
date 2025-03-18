output "instance_id" {
  description = "aws_vpc_endpoint id"
  value       = aws_vpc_endpoint.sns_vpc_endpoint_id.id
}
