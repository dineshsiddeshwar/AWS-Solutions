provider "aws" {
  region = var.aws_region
}

data "aws_organizations_organization" "org" {}

#=============================Root Layer==================================#

resource "aws_organizations_policy_attachment" "Root-Level-Restriction_1" {
  policy_id = aws_organizations_policy.Root-Level-Restriction_1.id
  target_id = var.Root
}

resource "aws_organizations_policy_attachment" "Root-Level-Restriction_2" {
  policy_id = aws_organizations_policy.Root-Level-Restriction_2.id
  target_id = var.Root
}

#=============================Prod Nested OU==================================#

#=============================Layer-1==================================#

resource "aws_organizations_policy_attachment" "Prod-Tagging-Restriction" {
  policy_id = aws_organizations_policy.Prod-Tagging-Restriction.id
  target_id = var.Prod
}

#========================Layer-2====================#

resource "aws_organizations_policy_attachment" "Prod-Private-Region-Restriction" {
  policy_id = aws_organizations_policy.Prod-Private-Region-Restriction.id
  target_id = var.PROD-Private
}

resource "aws_organizations_policy_attachment" "Prod-Hybrid-Region-Restriction" {
  policy_id = aws_organizations_policy.Prod-Hybrid-Region-Restriction.id
  target_id = var.PROD-Hybrid
}

resource "aws_organizations_policy_attachment" "Prod-Public-Region-Restriction" {
  policy_id = aws_organizations_policy.Prod-Public-Region-Restriction.id
  target_id = var.PROD-Public
}

resource "aws_organizations_policy_attachment" "Prod-Private-Deny-Restriction" {
  policy_id = aws_organizations_policy.Prod-Private-Deny-Restriction.id
  target_id = var.PROD-Private
}

resource "aws_organizations_policy_attachment" "Prod-Hybrid-Deny-Restriction" {
  policy_id = aws_organizations_policy.Prod-Hybrid-Deny-Restriction.id
  target_id = var.PROD-Hybrid
}

resource "aws_organizations_policy_attachment" "Prod-Public-Deny-Restriction" {
  policy_id = aws_organizations_policy.Prod-Public-Deny-Restriction.id
  target_id = var.PROD-Public
}

resource "aws_organizations_policy_attachment" "Prod-Private-Management-Restriction" {
  policy_id = aws_organizations_policy.Prod-Private-Management-Restriction.id
  target_id = var.PROD-Private
}

resource "aws_organizations_policy_attachment" "Prod-Hybrid-Management-Restriction" {
  policy_id = aws_organizations_policy.Prod-Hybrid-Management-Restriction.id
  target_id = var.PROD-Hybrid
}

resource "aws_organizations_policy_attachment" "Prod-Public-Management-Restriction" {
  policy_id = aws_organizations_policy.Prod-Public-Management-Restriction.id
  target_id = var.PROD-Public
}

#========================Layer-3=======================#

resource "aws_organizations_policy_attachment" "Prod-Private-BC-Service-Restriction" {
  policy_id = aws_organizations_policy.Prod-Private-BC-Service-Restriction.id
  target_id = var.PROD-Private-BC
}

resource "aws_organizations_policy_attachment" "Prod-Private-BC-DB-Restriction" {
  policy_id = aws_organizations_policy.Prod-Private-BC-DB-Restriction.id
  target_id = var.PROD-Private-BC
}

resource "aws_organizations_policy_attachment" "Prod-Private-NON-BC-Service-Restriction" {
  policy_id = aws_organizations_policy.Prod-Private-NON-BC-Service-Restriction.id
  target_id = var.PROD-Private-NON-BC
}

resource "aws_organizations_policy_attachment" "Prod-Private-NON-BC-DB-Restriction" {
  policy_id = aws_organizations_policy.Prod-Private-NON-BC-DB-Restriction.id
  target_id = var.PROD-Private-NON-BC
}

resource "aws_organizations_policy_attachment" "Prod-Private-Deviation-Service-Restriction" {
  policy_id = aws_organizations_policy.Prod-Private-Deviation-Service-Restriction.id
  target_id = var.PROD-Private-Service-Deviation
}

resource "aws_organizations_policy_attachment" "Prod-Private-Deviation-DB-Restriction" {
  policy_id = aws_organizations_policy.Prod-Private-Deviation-DB-Restriction.id
  target_id = var.PROD-Private-Service-Deviation
}

resource "aws_organizations_policy_attachment" "Prod-Hybrid-BC-Service-Restriction" {
  policy_id = aws_organizations_policy.Prod-Hybrid-BC-Service-Restriction.id
  target_id = var.PROD-Hybrid-BC
}

resource "aws_organizations_policy_attachment" "Prod-Hybrid-BC-DB-Restriction" {
  policy_id = aws_organizations_policy.Prod-Hybrid-BC-DB-Restriction.id
  target_id = var.PROD-Hybrid-BC
}

resource "aws_organizations_policy_attachment" "Prod-Hybrid-NON-BC-Service-Restriction" {
  policy_id = aws_organizations_policy.Prod-Hybrid-NON-BC-Service-Restriction.id
  target_id = var.PROD-Hybrid-NON-BC
}

resource "aws_organizations_policy_attachment" "Prod-Hybrid-NON-BC-DB-Restriction" {
  policy_id = aws_organizations_policy.Prod-Hybrid-NON-BC-DB-Restriction.id
  target_id = var.PROD-Hybrid-NON-BC
}

resource "aws_organizations_policy_attachment" "Prod-Hybrid-Deviation-Service-Restriction" {
  policy_id = aws_organizations_policy.Prod-Hybrid-Deviation-Service-Restriction.id
  target_id = var.PROD-Hybrid-Service-Deviation
}

resource "aws_organizations_policy_attachment" "Prod-Hybrid-Deviation-DB-Restriction" {
  policy_id = aws_organizations_policy.Prod-Hybrid-Deviation-DB-Restriction.id
  target_id = var.PROD-Hybrid-Service-Deviation
}

resource "aws_organizations_policy_attachment" "Prod-Public-BC-Service-Restriction" {
  policy_id = aws_organizations_policy.Prod-Public-BC-Service-Restriction.id
  target_id = var.PROD-Public-BC
}

resource "aws_organizations_policy_attachment" "Prod-Public-BC-DB-Restriction" {
  policy_id = aws_organizations_policy.Prod-Public-BC-DB-Restriction.id
  target_id = var.PROD-Public-BC
}

resource "aws_organizations_policy_attachment" "Prod-Public-NON-BC-Service-Restriction" {
  policy_id = aws_organizations_policy.Prod-Public-NON-BC-Service-Restriction.id
  target_id = var.PROD-Public-NON-BC
}

resource "aws_organizations_policy_attachment" "Prod-Public-NON-BC-DB-Restriction" {
  policy_id = aws_organizations_policy.Prod-Public-NON-BC-DB-Restriction.id
  target_id = var.PROD-Public-NON-BC
}

resource "aws_organizations_policy_attachment" "Prod-Public-Deviation-Service-Restriction" {
  policy_id = aws_organizations_policy.Prod-Public-Deviation-Service-Restriction.id
  target_id = var.PROD-Public-Service-Deviation
}

resource "aws_organizations_policy_attachment" "Prod-Public-Deviation-DB-Restriction" {
  policy_id = aws_organizations_policy.Prod-Public-Deviation-DB-Restriction.id
  target_id = var.PROD-Public-Service-Deviation
}

#=============================Non Prod Nested OU==================================#

#=============================Layer-1==================================#

resource "aws_organizations_policy_attachment" "NON-Prod-Tagging-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Tagging-Restriction.id
  target_id = var.NON-Prod
}

#========================Layer-2====================#

resource "aws_organizations_policy_attachment" "NON-Prod-Private-Region-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Private-Region-Restriction.id
  target_id = var.NON-PROD-Private
}

resource "aws_organizations_policy_attachment" "NON-Prod-Hybrid-Region-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Hybrid-Region-Restriction.id
  target_id = var.NON-PROD-Hybrid
}

resource "aws_organizations_policy_attachment" "NON-Prod-Public-Region-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Public-Region-Restriction.id
  target_id = var.NON-PROD-Public
}

resource "aws_organizations_policy_attachment" "NON-Prod-Private-Deny-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Private-Deny-Restriction.id
  target_id = var.NON-PROD-Private
}

resource "aws_organizations_policy_attachment" "NON-Prod-Hybrid-Deny-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Hybrid-Deny-Restriction.id
  target_id = var.NON-PROD-Hybrid
}

resource "aws_organizations_policy_attachment" "NON-Prod-Public-Deny-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Public-Deny-Restriction.id
  target_id = var.NON-PROD-Public
}

resource "aws_organizations_policy_attachment" "NON-Prod-Private-Management-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Private-Management-Restriction.id
  target_id = var.NON-PROD-Private
}

resource "aws_organizations_policy_attachment" "NON-Prod-Hybrid-Management-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Hybrid-Management-Restriction.id
  target_id = var.NON-PROD-Hybrid
}

resource "aws_organizations_policy_attachment" "NON-Prod-Public-Management-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Public-Management-Restriction.id
  target_id = var.NON-PROD-Public
}

#========================Layer-3=======================#

resource "aws_organizations_policy_attachment" "NON-Prod-Private-BC-Service-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Private-BC-Service-Restriction.id
  target_id = var.NON-PROD-Private-BC
}

resource "aws_organizations_policy_attachment" "NON-Prod-Private-BC-DB-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Private-BC-DB-Restriction.id
  target_id = var.NON-PROD-Private-BC
}

resource "aws_organizations_policy_attachment" "NON-Prod-Private-NON-BC-Service-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Private-NON-BC-Service-Restriction.id
  target_id = var.NON-PROD-Private-NON-BC
}

resource "aws_organizations_policy_attachment" "NON-Prod-Private-NON-BC-DB-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Private-NON-BC-DB-Restriction.id
  target_id = var.NON-PROD-Private-NON-BC
}

resource "aws_organizations_policy_attachment" "NON-Prod-Private-Deviation-Service-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Private-Deviation-Service-Restriction.id
  target_id = var.NON-PROD-Private-Service-Deviation
}

resource "aws_organizations_policy_attachment" "NON-Prod-Private-Deviation-DB-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Private-Deviation-DB-Restriction.id
  target_id = var.NON-PROD-Private-Service-Deviation
}

resource "aws_organizations_policy_attachment" "NON-Prod-Hybrid-BC-Service-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Hybrid-BC-Service-Restriction.id
  target_id = var.NON-PROD-Hybrid-BC
}

resource "aws_organizations_policy_attachment" "NON-Prod-Hybrid-BC-DB-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Hybrid-BC-DB-Restriction.id
  target_id = var.NON-PROD-Hybrid-BC
}

resource "aws_organizations_policy_attachment" "NON-Prod-Hybrid-NON-BC-Service-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Hybrid-NON-BC-Service-Restriction.id
  target_id = var.NON-PROD-Hybrid-NON-BC
}

resource "aws_organizations_policy_attachment" "NON-Prod-Hybrid-NON-BC-DB-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Hybrid-NON-BC-DB-Restriction.id
  target_id = var.NON-PROD-Hybrid-NON-BC
}

resource "aws_organizations_policy_attachment" "NON-Prod-Hybrid-Deviation-Service-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Hybrid-Deviation-Service-Restriction.id
  target_id = var.NON-PROD-Hybrid-Service-Deviation
}

resource "aws_organizations_policy_attachment" "NON-Prod-Hybrid-Deviation-DB-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Hybrid-Deviation-DB-Restriction.id
  target_id = var.NON-PROD-Hybrid-Service-Deviation
}

resource "aws_organizations_policy_attachment" "NON-Prod-Public-BC-Service-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Public-BC-Service-Restriction.id
  target_id = var.NON-PROD-Public-BC
}

resource "aws_organizations_policy_attachment" "NON-Prod-Public-BC-DB-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Public-BC-DB-Restriction.id
  target_id = var.NON-PROD-Public-BC
}

resource "aws_organizations_policy_attachment" "NON-Prod-Public-NON-BC-Service-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Public-NON-BC-Service-Restriction.id
  target_id = var.NON-PROD-Public-NON-BC
}

resource "aws_organizations_policy_attachment" "NON-Prod-Public-NON-BC-DB-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Public-NON-BC-DB-Restriction.id
  target_id = var.NON-PROD-Public-NON-BC
}

resource "aws_organizations_policy_attachment" "NON-Prod-Public-Deviation-Service-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Public-Deviation-Service-Restriction.id
  target_id = var.NON-PROD-Public-Service-Deviation
}

resource "aws_organizations_policy_attachment" "NON-Prod-Public-Deviation-DB-Restriction" {
  policy_id = aws_organizations_policy.NON-Prod-Public-Deviation-DB-Restriction.id
  target_id = var.NON-PROD-Public-Service-Deviation
}

#=============================Shared Services Nested OU==================================#

#========================Layer-2====================#

resource "aws_organizations_policy_attachment" "Shared-Services-Private-Region-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Private-Region-Restriction.id
  target_id = var.Shared-Services-Private
}

resource "aws_organizations_policy_attachment" "Shared-Services-Hybrid-Region-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Hybrid-Region-Restriction.id
  target_id = var.Shared-Services-Hybrid
}

resource "aws_organizations_policy_attachment" "Shared-Services-Public-Region-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Public-Region-Restriction.id
  target_id = var.Shared-Services-Public
}

#========================Layer-3=======================#

resource "aws_organizations_policy_attachment" "Shared-Services-Private-DataSCI-Service-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Private-DataSCI-Service-Restriction.id
  target_id = var.Shared-Services-Private-Data-Science
}

resource "aws_organizations_policy_attachment" "Shared-Services-Private-EndPoints-Service-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Private-EndPoints-Service-Restriction.id
  target_id = var.Shared-Services-Private-Endpoints
}

resource "aws_organizations_policy_attachment" "Shared-Services-Private-DataSCI-IAM-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Private-DataSCI-IAM-Restriction.id
  target_id = var.Shared-Services-Private-Data-Science
}

resource "aws_organizations_policy_attachment" "Shared-Services-Private-EndPoints-IAM-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Private-EndPoints-IAM-Restriction.id
  target_id = var.Shared-Services-Private-Endpoints
}

resource "aws_organizations_policy_attachment" "Shared-Services-Hybrid-Managed-EKS-Service-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Hybrid-Managed-EKS-Service-Restriction.id
  target_id = var.Shared-Services-Hybrid-Managed-EKS
}

resource "aws_organizations_policy_attachment" "Shared-Services-Hybrid-IACVault-Service-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Hybrid-IACVault-Service-Restriction.id
  target_id = var.Shared-Services-Hybrid-IACVault
}

resource "aws_organizations_policy_attachment" "Shared-Services-Hybrid-Data-Platform-Service-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Hybrid-Data-Platform-Service-Restriction.id
  target_id = var.Shared-Services-Hybrid-Data-Platform
}

resource "aws_organizations_policy_attachment" "Shared-Services-Hybrid-Managed-Serv-Service-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Hybrid-Managed-Serv-Service-Restriction.id
  target_id = var.Shared-Services-Hybrid-Managed-Services
}

resource "aws_organizations_policy_attachment" "Shared-Services-Hybrid-Managed-EKS-IAM-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Hybrid-Managed-EKS-IAM-Restriction.id
  target_id = var.Shared-Services-Hybrid-Managed-EKS
}

resource "aws_organizations_policy_attachment" "Shared-Services-Hybrid-IACVault-IAM-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Hybrid-IACVault-IAM-Restriction.id
  target_id = var.Shared-Services-Hybrid-IACVault
}
resource "aws_organizations_policy_attachment" "Shared-Services-Hybrid-Data-Platform-IAM-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Hybrid-Data-Platform-IAM-Restriction.id
  target_id = var.Shared-Services-Hybrid-Data-Platform
}

resource "aws_organizations_policy_attachment" "Shared-Services-Hybrid-Managed-Serv-IAM-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Hybrid-Managed-Serv-IAM-Restriction.id
  target_id = var.Shared-Services-Hybrid-Managed-Services
}

resource "aws_organizations_policy_attachment" "Shared-Services-Public-Savings-Service-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Public-Savings-Service-Restriction.id
  target_id = var.Shared-Services-Public-Savings-Plan
}

resource "aws_organizations_policy_attachment" "Shared-Services-Public-WIZ-Service-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Public-WIZ-Service-Restriction.id
  target_id = var.Shared-Services-Public-WIZ-Science
}

resource "aws_organizations_policy_attachment" "Shared-Services-Public-Savings-IAM-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Public-Savings-IAM-Restriction.id
  target_id = var.Shared-Services-Public-Savings-Plan
}

resource "aws_organizations_policy_attachment" "Shared-Services-Public-WIZ-IAM-Restriction" {
  policy_id = aws_organizations_policy.Shared-Services-Public-WIZ-IAM-Restriction.id
  target_id = var.Shared-Services-Public-WIZ-Science
}

#=============================Exceptions Nested OU==================================#

#========================Layer-1====================#

resource "aws_organizations_policy_attachment" "Exceptions-Tagging-Restriction" {
  policy_id = aws_organizations_policy.Exceptions-Tagging-Restriction.id
  target_id = var.Exception
}

resource "aws_organizations_policy_attachment" "Exceptions-Region-Restriction" {
  policy_id = aws_organizations_policy.Exceptions-Region-Restriction.id
  target_id = var.Exception
}

# resource "aws_organizations_policy_attachment" "Exceptions-IAM-Restriction" {
#   policy_id = aws_organizations_policy.Exceptions-IAM-Restriction.id
#   target_id = var.Exception
# }

resource "aws_organizations_policy_attachment" "Exceptions-Management-Restriction" {
  policy_id = aws_organizations_policy.Exceptions-Management-Restriction.id
  target_id = var.Exception
}