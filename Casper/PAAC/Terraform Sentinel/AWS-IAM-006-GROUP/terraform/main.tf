/***********************************************************/
// Terraform Sentinel AWS-IAM-GROUP-006
// Author: Karthik Vijay Jirlimath
// Description: Detect and alert if AWS:IAM policy has resource "*" and effect "allow".
/***********************************************************/
terraform {
    required_providers {
      aws = {
        version = "~> 5.20"
        source = "hashicorp/aws"
      }
    }
}

provider "aws" {
    region = "us-west-1"
}

# //Non-complaint-1 jsonencoded policy
# resource "aws_iam_group_policy" "my_casper_policy" {
#   name  = "my_casper_policy"
#   group = "${aws_iam_group.my_casper_group.id}"

#   policy = jsonencode(
#         {
#         "Version": "2012-10-17",
#         "Statement": [
#             {
#             "Action": [
#                 "iam:*"
#             ],
#             "Effect": "Allow",
#             "Resource": ["*"]
#             }
#         ]
#         })
# }
# // ENDOF Non-complaint-1

# //Non-complaint-2 jsonencoded policy with multiple statements
# resource "aws_iam_group_policy" "my_casper_policy" {
#   name  = "my_casper_policy"
#   group = "${aws_iam_group.my_casper_group.id}"

#   policy = jsonencode(
#         {
#         "Version": "2012-10-17",
#         "Statement": [
#             {
#             "Action": [
#                 "iam:*"
#             ],
#             "Effect": "Allow",
#             "Resource": "arn:aws:s3::test-bucket"
#             },
#             {
#             "Action": [
#                 "ec2:Describe*"
#             ],
#             "Effect": "Allow",
#             "Resource": "*"
#             }
#         ]
#         })
# }
# // ENDOF Non-complaint-2

# // Compliant-1: Effect Deny
# resource "aws_iam_group_policy" "group_policy" {
#   name = "my_casper_policy"
#   group = aws_iam_group.my_casper_group.name
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = [
#           "iam:*",
#         ]
#         Effect   = "Deny"
#         Resource = "*"
#       }
#     ]
#   })
# }
# // ENDOF Compliant-1

// Compliant-2: Effect Deny
resource "aws_iam_group_policy" "group_policy" {
  name = "my_casper_policy"
  group = aws_iam_group.my_casper_group.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:CreateBucket",
        ]
        Effect   = "Deny"
        Resource = ["*"]
      },
    ]
  })
}
// ENDOF Compliant-2

resource "aws_iam_group" "my_casper_group" {
  name = "my_casper_group"
  path = "/system/"
}