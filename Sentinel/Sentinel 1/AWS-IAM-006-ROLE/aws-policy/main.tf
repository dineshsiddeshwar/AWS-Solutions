/***********************************************************/
// Terraform Sentinel AWS-IAM-ROLE-006
// Author: Karthik Vijay Jirlimath
// Description: Detect and alert if AWS:IAM policy has resource "*" and effect "allow".
/***********************************************************/

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.20"
    }
  }
}

# //Non-complaint-1 terraform aws_iam_role_policy resource block policy
# resource "aws_iam_role_policy" "casper_policy_1" {
#   name = "test_policy"
#   role = aws_iam_role.test_role_1.id

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = "ec2:DescribeInstances"
#         Effect = "Allow"
#         Resource = "*"
#       },
#     ]
#   })
# }

# resource "aws_iam_role" "test_role_1" {
#   name = "test_role"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = "ec2:DescribeInstances"
#         Effect = "Allow"
#         Principal = {
#           Service = "ec2.amazonaws.com"
#         }
#       },
#     ]
#   })
# }
# // ENDOF Non-complaint-1

# //Non-complaint-2 terraform aws_iam_role_policy resource block policy with multiple statements
# resource "aws_iam_role_policy" "casper_policy_2" {
#   name = "test_policy"
#   role = aws_iam_role.test_role_2.id

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = "ec2:DescribeInstances"
#         Effect = "Allow"
#         Resource = ["*"]
#       },
#       {
#         Action = "ec2:DescribeInstances"
#         Effect = "Allow"
#         Resource = "arn:aws:s3:::my_corporate_bucket/*"
#       }
#     ]
#   })
# }

# resource "aws_iam_role" "test_role_2" {
#   name = "test_role"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = "ec2:DescribeInstances"
#         Effect = "Allow"
#         Principal = {
#           Service = "ec2.amazonaws.com"
#         }
#       },
#     ]
#   })

# }
# // ENDOF Non-complaint-2


# // Complaint-1: multiple statements in resource aws_iam_role_policy
# resource "aws_iam_role_policy" "casper_policy_3" {
#   name = "test_policy"
#   role = aws_iam_role.test_role_3.id

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = "ec2:DescribeInstances"
#         Effect = "Deny"
#         Resource = ["*"]
#       },
#       {
#         Action = [
#          "ec2:DescribeInstances",
#          "ec2:DescribeInstanceTypes"
#         ]
#         Effect = "Allow"
#         Resource = "arn:aws:s3:::my_corporate_bucket/*"
#       }
#     ]
#   })
# }

# resource "aws_iam_role" "test_role_3" {
#   name = "test_role"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = "ec2:DescribeInstances"
#         Effect = "Allow"
#         Sid    = ""
#         Principal = {
#           Service = "ec2.amazonaws.com"
#         }
#       },
#     ]
#   })
# }
# // ENDOF Complaint-1

// Complaint-2: single statement in resource aws_iam_role_policy
resource "aws_iam_role_policy" "casper_policy_4" {
  name = "test_policy"
  role = aws_iam_role.test_role_4.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "ec2:DescribeInstances"
        Effect = "Deny"
        Resource = ["*"]
      },
    ]
  })
}

resource "aws_iam_role" "test_role_4" {
  name = "test_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "ec2:DescribeInstances"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}
// ENDOF Complaint-2