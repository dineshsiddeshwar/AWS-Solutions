resource "aws_dynamodb_table" "terraform-remotelock" {
  name           = "${var.env}-terraform-remotelock-pfinternal"
  hash_key       = "LockID"
  read_capacity  = 5
  write_capacity = 5

  attribute {
    name = "LockID"
    type = "S"
  }

  # Prevents Terraform from destroying or replacing this object - a great safety mechanism
  lifecycle {
    prevent_destroy = true
  }

  tags = merge(local.tags,
    {
      Name                  = "${local.resource_group}-remotelock-dynamodb"
      "Data Classification" = "Internal"
  })

}