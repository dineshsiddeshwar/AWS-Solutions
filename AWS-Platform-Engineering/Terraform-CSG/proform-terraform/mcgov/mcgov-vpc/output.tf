output "terraformstate_dynamodb" {
  value = aws_dynamodb_table.terraform-remotelock.id
}