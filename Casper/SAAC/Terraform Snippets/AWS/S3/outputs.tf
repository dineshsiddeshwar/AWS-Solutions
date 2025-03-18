output "stack_status" {
  description = "stack status"
  value       = aws_s3_bucket.s3_bucket.bucket
}
