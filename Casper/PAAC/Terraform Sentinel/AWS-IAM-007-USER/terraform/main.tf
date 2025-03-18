terraform {
  required_providers {
    aws = {
      version = "~> 5.0"
      source = "hashicorp/aws"
      }
    }
  }

provider "aws" {
  region = "us-east-1"
}

# # Non-Compliant 1
# resource "aws_iam_user_policy" "user_policy" {
#   name = "test_user_policy"
#   user = aws_iam_user.user.name
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = [
#           "iam:*",
#         ]
#         Effect   = "Allow"
#         Resource = "*"
        
#       },
#     ]
#   })
# }
# # ENDOF Non-compliant-1


# # Non-Compliant 2
# resource "aws_iam_user_policy" "user_policy" {
#   name = "test_user_policy"
#   user = aws_iam_user.user.name
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = [
#           "iam:*",
#         ]
#         Effect   = "Allow"
#         Resource = ["*"]
#       },
#     ]
#   })
# }
# # ENDOF Non-compliant-2

# # Non Compliant-3 multiple statements
# resource "aws_iam_user_policy" "user_policy" {
#   name = "test_user_policy"
#   user = aws_iam_user.user.name
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = [
#           "s3:CreateBucket",
#         ]
#         Effect   = "Allow"
#         Resource = "arn:aws:s3::test-bucket"
#       },
#       {
#         Action = [
#           "iam:*",
#         ]
#         Effect   = "Allow"
#         Resource = "*"
#       }
#     ]
#   })
# }
# # ENDOF Non-complaint-3

# # Compliant-1  Action is not wildcard like iam:*
# resource "aws_iam_user_policy" "user_policy" {
#   name = "test_user_policy"
#   user = aws_iam_user.user.name
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = [
#           "s3:CreateBucket",
#         ]
#         Effect   = "Allow"
#         Resource = "arn:aws:s3::test-bucket"
#       },
#     ]
#   })
# }
# # ENDOF Compliant-1


# Compliant-2 Effect Deny
resource "aws_iam_user_policy" "user_policy" {
  name = "test_user_policy"
  user = aws_iam_user.user.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "iam:*",
        ]
        Effect   = "Deny"
        Resource = "*"
      },
    ]
  })
}
# ENDOF Compliant-2

resource "aws_iam_user" "user" {
  name = "test_user"
  path = "/system/"
}
