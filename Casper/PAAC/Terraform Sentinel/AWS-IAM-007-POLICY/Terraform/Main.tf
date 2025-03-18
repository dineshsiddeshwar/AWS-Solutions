terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "5.22.0"
    }
  }
}

provider "aws" {
  region = "us-west-1"
}

# ##Compliant 1

# resource "aws_iam_policy" "policy" {
#   name        = "test_policy"
#   path        = "/"
#   description = "My test policy"

#   # Terraform's "jsonencode" function converts a
#   # Terraform expression result to valid JSON syntax.
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = [
#           "iam:*"
#         ]
#         Effect   = "Deny"
#         Resource = "*"
#       },
#     ]
#   })
# }


##Compliant 2

# resource "aws_iam_policy" "policy" {
#   name        = "test_policy"
#   path        = "/"
#   description = "My test policy"

#   # Terraform's "jsonencode" function converts a
#   # Terraform expression result to valid JSON syntax.
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = [
#           "ec2:Describe*"
#         ]
#         Effect   = "Allow"
#         Resource = "*"
#       },
#     ]
#   })
# }

# ##Compliant 3

# resource "aws_iam_policy" "policy" {
#   name        = "test_policy"
#   path        = "/"
#   description = "My test policy"

#   # Terraform's "jsonencode" function converts a
#   # Terraform expression result to valid JSON syntax.
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = [
#           "ec2:Describe*"
#         ]
#         Effect   = "Allow"
#         Resource = "*"
#       },
#       {
#         Action = [
#           "iam:*"
#         ]
#         Effect   = "Deny"
#         Resource = "*"
#       }
#     ]
#   })
# }

# ##Non Compliant 1

# resource "aws_iam_policy" "policy" {
#   name        = "test_policy"
#   path        = "/"
#   description = "My test policy"

#   # Terraform's "jsonencode" function converts a
#   # Terraform expression result to valid JSON syntax.
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = [
#           "iam:*"
#         ]
#         Effect   = "Allow"
#         Resource = "*"
#       },
#     ]
#   })
# }

# ##Non Compliant 2

resource "aws_iam_policy" "policy" {
  name        = "test_policy"
  path        = "/"
  description = "My test policy"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "iam:*"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action = [
          "s3:*"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}