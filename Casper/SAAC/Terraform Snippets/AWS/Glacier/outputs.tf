output "glacier_bucket_id" {
  description = "ID of the glacier S3 bucket"
  value       = aws_s3_bucket_metric.glacier-bucket.id
}
