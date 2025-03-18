output "stack_status" {
  description = "Created vpc with ID"
  value       = aws_vpc.primary_vpc.id
}
