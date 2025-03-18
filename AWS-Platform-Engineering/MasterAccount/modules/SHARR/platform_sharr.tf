#----------------------------------------------------------------------
#(SO0111R) AWS Security Hub Automated Response & Remediation Roles, v2.0.0. Resources needed for exception handling mechanism
#----------------------------------------------------------------------
# SHARR Exception Resources
#----------------------------------------------------------------------

# SHARR Exception EC213 Role 
resource "aws_iam_role" "sharr_exception_ec2_13_role" {
  name                =  "platform-sharr-exception-ec2-13-role"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::${var.audit_account}:role/SO0111-SHARR-Orchestrator-Admin"
                        },
                        "Action": "sts:AssumeRole",
                    }
                ]
            })
}

resource "aws_iam_role_policy" "sharr_exception_ec2_13_role_inline_policy" {
  name = "SHARR_Exception_EC2_13_Policy"
  role = aws_iam_role.sharr_exception_ec2_13_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "DDBQueryAccess"
        Action = [
          "dynamodb:Query"
        ]
        Effect   = "Allow"
        Resource = aws_dynamodb_table.sharr_port_exception_table.arn
      }
    ]
  })
}

# Port Exception Table
resource "aws_dynamodb_table" "sharr_port_exception_table" {
  name           = "platform_EC213ExceptionTable"

  billing_mode   = "PAY_PER_REQUEST"
  deletion_protection_enabled = true

  server_side_encryption {
    enabled = false
  }

  hash_key       = "SecurityGroupID"
  range_key      = "AccountID"

  point_in_time_recovery { 
    enabled = true 
  }

  attribute {
    name = "SecurityGroupID"
    type = "S"
  }

  attribute {
    name = "AccountID"
    type = "S"
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}
