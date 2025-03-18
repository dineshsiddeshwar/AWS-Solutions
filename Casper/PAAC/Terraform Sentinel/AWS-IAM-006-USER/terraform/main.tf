/***********************************************************/
// Terraform Sentinel AWS-IAM-USER-006
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

provider "aws" {
  region     = "us-west-1"
}

// Non-Compliant 1
resource "aws_iam_user_policy" "user_policy" {
  name = "test_user_policy"
  user = aws_iam_user.casper_iam.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:CreateBucket",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}
// ENDOF Non-Compliant 1

// Non-Compliant 2
data "aws_iam_policy_document" "casper_policy" {
  version = "2012-10-17"

  statement {
    sid = "AWS IAM overprivileged access"
    principals {
      type        = "AWS"
      identifiers = ["${aws_iam_user.casper_iam.arn}"]
    }
    effect    = "Allow"
    actions   = ["*"]
    resources = ["*"]

  }
}

resource "aws_iam_user_policy" "casper_testing_policy" {
  name = "casper_check_policy"
  user = aws_iam_user.casper_iam.name

  policy = data.aws_iam_policy_document.casper_policy.json
}
//ENDOF Non-Compliant 2

// Non-Compliant 3: multiple statements
resource "aws_iam_user_policy" "user_policy" {
  name = "test_user_policy"
  user = aws_iam_user.casper_iam.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:CreateBucket",
        ]
        Effect   = "Allow"
        Resource = "arn:aws:s3::test-bucket"
      },
      {
        Action = [
          "s3:CreateBucket",
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}
// ENDOF Non-Compliant 3

// Compliant-1: Effect Deny
resource "aws_iam_user_policy" "user_policy" {
  name = "test_user_policy"
  user = aws_iam_user.casper_iam.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:CreateBucket",
        ]
        Effect   = "Deny"
        Resource = "*"
      },
    ]
  })
}
// ENDOF Compliant-1

resource "aws_iam_user" "casper_iam" {
  name = "casper_iam"
  path = "/system/"

  tags = {
    environment = "test"
  }
}
