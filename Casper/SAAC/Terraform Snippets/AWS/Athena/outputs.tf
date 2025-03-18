output "instance_id" {
  description = "ID of the athena database"
  value       = aws_athena_database.athena_database_name.id
}
