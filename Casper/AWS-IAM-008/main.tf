provider "aws" {
  region = "us-west-2"
  
}

resource "aws_iam_role" "testRoleNegativeTestCase1" {
  name = "test_role"
  path="/"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Action = ["iam:CreateAccessKey","iam:CreateLoginProfile","iam:UpdateLoginProfile","iam:AttachUserPolicy","iam:AttachGroupPolicy","iam:AttachRolePolicy",
                   "iam:PutUserPolicy","iam:PutGroupPolicy","iam:PutRolePolicy","iam:CreatePolicy","iam:CreatePolicy","iam:AddUserToGroup","iam:UpdateAssumeRolePolicy",
                      "iam:CreatePolicyVersion","iam:SetDefaultPolicyVersion","iam:PassRole"]
        Effect = "Allow"
        
        Resource="*"
      },
    ]
  })
}

resource "aws_iam_role_policy" "testRoleNegativeTestCase1" {
  name = "test_policy"
  role = aws_iam_role.test_role.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Action =  ["iam:CreateAccessKey","iam:CreateLoginProfile","iam:UpdateLoginProfile","iam:AttachUserPolicy","iam:AttachGroupPolicy","iam:AttachRolePolicy",
                   "iam:PutUserPolicy","iam:PutGroupPolicy","iam:PutRolePolicy","iam:CreatePolicy","iam:CreatePolicy","iam:AddUserToGroup","iam:UpdateAssumeRolePolicy",
                      "iam:CreatePolicyVersion","iam:SetDefaultPolicyVersion","iam:PassRole"]

        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

resource "aws_iam_role" "testRoleNegativeTestCase2" {
    name = "testRole"
    path="/"

    assume_role_policy = jsonencode({
      Version = "2012-10-17"

      Statement = [
        {
          Action   = ["iam:CreateAccessKey","iam:CreateLoginProfile","iam:UpdateLoginProfile",iam:AttachUserPolicy","iam:AttachGroupPolicy","iam:AttachRolePolicy",
                      "iam:PutUserPolicy","iam:PutGroupPolicy","iam:PutRolePolicy","iam:CreatePolicy","iam:CreatePolicy","iam:AddUserToGroup","iam:UpdateAssumeRolePolicy",
                      "iam:CreatePolicyVersion","iam:SetDefaultPolicyVersion","iam:PassRole"]

          Effect   = "Allow"
          Resource = "*"
        },
      ]
    })
 

  inline_policy {
    name = "testRoleInlinePolicy"

    policy = jsonencode({
      Version = "2012-10-17"

      Statement = [
        {
          Action   =["iam:CreateAccessKey","iam:CreateLoginProfile","iam:UpdateLoginProfile",iam:AttachUserPolicy","iam:AttachGroupPolicy","iam:AttachRolePolicy",
                     "iam:PutUserPolicy","iam:PutGroupPolicy","iam:PutRolePolicy","iam:CreatePolicy","iam:CreatePolicy","iam:AddUserToGroup","iam:UpdateAssumeRolePolicy",
                     "iam:CreatePolicyVersion","iam:SetDefaultPolicyVersion","iam:PassRole"]

          Effect   = "Allow"
          Resource = "*"
        },
      ]
    })
  }
}

