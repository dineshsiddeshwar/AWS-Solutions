provider "aws" {
  region = var.aws_region
}

data "aws_organizations_organization" "org" {}

##==================== Layer-1 OU Structure =======================================
## Prod OU
resource "aws_organizations_organizational_unit" "Prod" {
  name      = "Prod"
  parent_id = data.aws_organizations_organization.org.roots[0].id
}

## NON-Prod OU
resource "aws_organizations_organizational_unit" "NON-Prod" {
  name      = "NON-Prod"
  parent_id = data.aws_organizations_organization.org.roots[0].id
}

## Shared-Services OU
resource "aws_organizations_organizational_unit" "Shared-Services" {
  name      = "Shared-Services"
  parent_id = data.aws_organizations_organization.org.roots[0].id
}

## Exceptions OU
resource "aws_organizations_organizational_unit" "Exceptions" {
  name      = "Exceptions"
  parent_id = data.aws_organizations_organization.org.roots[0].id
}

## RESPC-Migration OU
resource "aws_organizations_organizational_unit" "RESPC-Migration" {
  name      = "RESPC-Migration"
  parent_id = data.aws_organizations_organization.org.roots[0].id
}
##============================================================================

##==================== Layer-2 OU Structure ==================================
## Prod-Private OU
resource "aws_organizations_organizational_unit" "Prod-Private" {
  name      = "Prod-Private"
  parent_id = aws_organizations_organizational_unit.Prod.id
}

## Prod-Public OU
resource "aws_organizations_organizational_unit" "Prod-Public" {
  name      = "Prod-Public"
  parent_id = aws_organizations_organizational_unit.Prod.id
}

## Prod-Hybrid OU
resource "aws_organizations_organizational_unit" "Prod-Hybrid" {
  name      = "Prod-Hybrid"
  parent_id = aws_organizations_organizational_unit.Prod.id
}

## NON-Prod-Private OU
resource "aws_organizations_organizational_unit" "NON-Prod-Private" {
  name      = "NON-Prod-Private"
  parent_id = aws_organizations_organizational_unit.NON-Prod.id
}

## NON-Prod-Public OU
resource "aws_organizations_organizational_unit" "NON-Prod-Public" {
  name      = "NON-Prod-Public"
  parent_id = aws_organizations_organizational_unit.NON-Prod.id
}

## NON-Prod-Hybrid OU
resource "aws_organizations_organizational_unit" "NON-Prod-Hybrid" {
  name      = "NON-Prod-Hybrid"
  parent_id = aws_organizations_organizational_unit.NON-Prod.id
}

## Shared-Services-Private OU
resource "aws_organizations_organizational_unit" "Shared-Services-Private" {
  name      = "Shared-Services-Private"
  parent_id = aws_organizations_organizational_unit.Shared-Services.id
}

## Shared-Services-Public OU
resource "aws_organizations_organizational_unit" "Shared-Services-Public" {
  name      = "Shared-Services-Public"
  parent_id = aws_organizations_organizational_unit.Shared-Services.id
}

## Shared-Services-Hybrid OU
resource "aws_organizations_organizational_unit" "Shared-Services-Hybrid" {
  name      = "Shared-Services-Hybrid"
  parent_id = aws_organizations_organizational_unit.Shared-Services.id
}

## Migration-SES OU
resource "aws_organizations_organizational_unit" "Migration-RESPC-SES" {
  name      = "Migration-RESPC-SES"
  parent_id = aws_organizations_organizational_unit.RESPC-Migration.id
}

## Migration-SEUK OU
resource "aws_organizations_organizational_unit" "Migration-RESPC-SEUK" {
  name      = "Migration-RESPC-SEUK"
  parent_id = aws_organizations_organizational_unit.RESPC-Migration.id
}

## Migration-Legacy OU
resource "aws_organizations_organizational_unit" "Migration-Legacy" {
  name      = "Migration-Legacy"
  parent_id = aws_organizations_organizational_unit.RESPC-Migration.id
}
##============================================================================

##==================== Layer-3 OU Structure ==================================
## PROD-Private-BC OU
resource "aws_organizations_organizational_unit" "Prod-Private-BC" {
  name      = "Prod-Private-BC"
  parent_id = aws_organizations_organizational_unit.Prod-Private.id
}

## PROD-Private-NON-BC OU
resource "aws_organizations_organizational_unit" "Prod-Private-NON-BC" {
  name      = "Prod-Private-NON-BC"
  parent_id = aws_organizations_organizational_unit.Prod-Private.id
}

## PROD-Private-Service-Deviation OU
resource "aws_organizations_organizational_unit" "Prod-Private-Service-Deviation" {
  name      = "Prod-Private-Service-Deviation"
  parent_id = aws_organizations_organizational_unit.Prod-Private.id
}

## PROD-Public-BC OU
resource "aws_organizations_organizational_unit" "Prod-Public-BC" {
  name      = "Prod-Public-BC"
  parent_id = aws_organizations_organizational_unit.Prod-Public.id
}

## PROD-Public-NON-BC OU
resource "aws_organizations_organizational_unit" "Prod-Public-NON-BC" {
  name      = "Prod-Public-NON-BC"
  parent_id = aws_organizations_organizational_unit.Prod-Public.id
}

## PROD-Public-Service-Deviation OU
resource "aws_organizations_organizational_unit" "Prod-Public-Service-Deviation" {
  name      = "Prod-Public-Service-Deviation"
  parent_id = aws_organizations_organizational_unit.Prod-Public.id
}

## PROD-Hybrid-BC OU
resource "aws_organizations_organizational_unit" "Prod-Hybrid-BC" {
  name      = "Prod-Hybrid-BC"
  parent_id = aws_organizations_organizational_unit.Prod-Hybrid.id
}

## PROD-Hybrid-NON-BC OU
resource "aws_organizations_organizational_unit" "Prod-Hybrid-NON-BC" {
  name      = "Prod-Hybrid-NON-BC"
  parent_id = aws_organizations_organizational_unit.Prod-Hybrid.id
}

## PROD-Hybrid-Service-Deviation OU
resource "aws_organizations_organizational_unit" "Prod-Hybrid-Service-Deviation" {
  name      = "Prod-Hybrid-Service-Deviation"
  parent_id = aws_organizations_organizational_unit.Prod-Hybrid.id
}

## NON-PROD-Private-BC OU
resource "aws_organizations_organizational_unit" "NON-Prod-Private-BC" {
  name      = "NON-Prod-Private-BC"
  parent_id = aws_organizations_organizational_unit.NON-Prod-Private.id
}

## NON-PROD-Private-NON-BC OU
resource "aws_organizations_organizational_unit" "NON-Prod-Private-NON-BC" {
  name      = "NON-Prod-Private-NON-BC"
  parent_id = aws_organizations_organizational_unit.NON-Prod-Private.id
}

## NON-PROD-Private-Service-Deviation OU
resource "aws_organizations_organizational_unit" "NON-Prod-Private-Service-Deviation" {
  name      = "NON-Prod-Private-Service-Deviation"
  parent_id = aws_organizations_organizational_unit.NON-Prod-Private.id
}

## NON-PROD-Public-BC OU
resource "aws_organizations_organizational_unit" "NON-Prod-Public-BC" {
  name      = "NON-Prod-Public-BC"
  parent_id = aws_organizations_organizational_unit.NON-Prod-Public.id
}

## NON-PROD-Public-NON-BC OU
resource "aws_organizations_organizational_unit" "NON-Prod-Public-NON-BC" {
  name      = "NON-Prod-Public-NON-BC"
  parent_id = aws_organizations_organizational_unit.NON-Prod-Public.id
}

## NON-PROD-Public-Service-Deviation OU
resource "aws_organizations_organizational_unit" "NON-Prod-Public-Service-Deviation" {
  name      = "NON-Prod-Public-Service-Deviation"
  parent_id = aws_organizations_organizational_unit.NON-Prod-Public.id
}

## NON-PROD-Hybrid-BC OU
resource "aws_organizations_organizational_unit" "NON-Prod-Hybrid-BC" {
  name      = "NON-Prod-Hybrid-BC"
  parent_id = aws_organizations_organizational_unit.NON-Prod-Hybrid.id
}

## NON-PROD-Hybrid-NON-BC OU
resource "aws_organizations_organizational_unit" "NON-Prod-Hybrid-NON-BC" {
  name      = "NON-Prod-Hybrid-NON-BC"
  parent_id = aws_organizations_organizational_unit.NON-Prod-Hybrid.id
}

## NON-PROD-Hybrid-Service-Deviation OU
resource "aws_organizations_organizational_unit" "NON-Prod-Hybrid-Service-Deviation" {
  name      = "NON-Prod-Hybrid-Service-Deviation"
  parent_id = aws_organizations_organizational_unit.NON-Prod-Hybrid.id
}

## Shared-Services-Hybrid-Data-Platform OU
resource "aws_organizations_organizational_unit" "Shared-Services-Hybrid-Data-Platform" {
  name      = "Shared-Services-Hybrid-Data-Platform"
  parent_id = aws_organizations_organizational_unit.Shared-Services-Hybrid.id
}

## Shared-Services-Hybrid-Managed-Services OU
resource "aws_organizations_organizational_unit" "Shared-Services-Hybrid-Managed-Services" {
  name      = "Shared-Services-Hybrid-Managed-Services"
  parent_id = aws_organizations_organizational_unit.Shared-Services-Hybrid.id
}

## Shared-Services-Hybrid-IAC-Vault OU
resource "aws_organizations_organizational_unit" "Shared-Services-Hybrid-IAC-Vault" {
  name      = "Shared-Services-Hybrid-IAC-Vault"
  parent_id = aws_organizations_organizational_unit.Shared-Services-Hybrid.id
}

## Shared-Services-Hybrid-Managed-EKS OU
resource "aws_organizations_organizational_unit" "Shared-Services-Hybrid-Managed-EKS" {
  name      = "Shared-Services-Hybrid-Managed-EKS"
  parent_id = aws_organizations_organizational_unit.Shared-Services-Hybrid.id
}

## Shared-Services-Private-Endpoint OU
resource "aws_organizations_organizational_unit" "Shared-Services-Private-Endpoint" {
  name      = "Shared-Services-Private-Endpoint"
  parent_id = aws_organizations_organizational_unit.Shared-Services-Private.id
}

## Shared-Services-Hybrid-Data-Science OU
resource "aws_organizations_organizational_unit" "Shared-Services-Private-Data-Science" {
  name      = "Shared-Services-Private-Data-Science"
  parent_id = aws_organizations_organizational_unit.Shared-Services-Private.id
}

## Shared-Services-Public-WIZ OU
resource "aws_organizations_organizational_unit" "Shared-Services-Public-WIZ" {
  name      = "Shared-Services-Public-WIZ"
  parent_id = aws_organizations_organizational_unit.Shared-Services-Public.id
}

## Shared-Services-Public-Saving-Plan OU
resource "aws_organizations_organizational_unit" "Shared-Services-Public-Saving-Plan" {
  name      = "Shared-Services-Public-Saving-Plan"
  parent_id = aws_organizations_organizational_unit.Shared-Services-Public.id
}
##============================================================================