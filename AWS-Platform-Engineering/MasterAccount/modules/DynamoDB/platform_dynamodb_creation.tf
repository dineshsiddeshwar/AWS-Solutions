# Account Details DynamoDB Table 
resource "aws_dynamodb_table" "account_details_dynamodb_table" {
  name           = "Account_Details"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "AccountNumber"
  point_in_time_recovery { 
    enabled = true 
  }

  attribute {
    name = "AccountNumber"
    type = "S"
  }
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Instance Patch Compliance DynamoDB Table
resource "aws_dynamodb_table" "instance_patch_compliance_dynamodb_table" {
  name           = "Instance_PatchCompliance"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "ResourceId"
  point_in_time_recovery { 
    enabled = true 
  }

  attribute {
    name = "ResourceId"
    type = "S"
  }

  attribute {
    name = "AccountNumber"
    type = "S"
  }

  attribute {
    name = "Month_Year"
    type = "S"
  }

  global_secondary_index {
    name               = "AccountNumber-Month_Year-index"
    hash_key           = "AccountNumber"
    range_key          = "Month_Year"
    write_capacity     = 5
    read_capacity      = 5
    projection_type    = "INCLUDE"
    non_key_attributes = ["ResourceId"]
  }
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# IP Management DynamoDB Table
resource "aws_dynamodb_table" "ip_management_dynamodb_table" {
  name           = "IPMGMTTable"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "cidr"
  point_in_time_recovery { 
    enabled = true 
  }

  attribute {
    name = "cidr"
    type = "S"
  }

  attribute {
    name = "consolidated_key"
    type = "S"
  }

  attribute {
    name = "is_allocated"
    type = "S"
  }

  global_secondary_index {
    name               = "IPMGMTGSI"
    hash_key           = "consolidated_key"
    range_key          = "is_allocated"
    write_capacity     = 5
    read_capacity      = 5
    projection_type    = "ALL"
  }
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Network DynamoDB Table
resource "aws_dynamodb_table" "network_dynamodb_table" {
  name           = "Network_Details_Table"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "VPC_Id"
  point_in_time_recovery { 
    enabled = true 
  }

  attribute {
    name = "VPC_Id"
    type = "S"
  }
  tags = {
    "platform_donotdelete" = "yes"
  }
}

# ATL Terraform Backend DynamoDB Table
resource "aws_dynamodb_table" "atl_terraform_backend_dynamodb_table" {
  name           = var.atl_terraform_backend_dynamodb
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"
  point_in_time_recovery { 
    enabled = true 
  }

  attribute {
    name = "LockID"
    type = "S"
  }
  tags = {
    "platform_donotdelete" = "yes"
  }
}

