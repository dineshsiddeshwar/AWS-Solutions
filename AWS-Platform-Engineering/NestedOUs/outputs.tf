## Outputs are listed here
output "aws_organizations_organizational_unit_Prod" {
  description = "Prod aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Prod.arn]
}

output "aws_organizations_organizational_unit_NON-Prod" {
  description = "NON-Prod aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.NON-Prod.arn]
}

output "aws_organizations_organizational_unit_Shared-Services" {
  description = "Shared-Services aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Shared-Services.arn]
}

output "aws_organizations_organizational_unit_Exceptions" {
  description = "Exceptions aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Exceptions.arn]
}

output "aws_organizations_organizational_unit_RESPC-Migration" {
  description = "RESPC-Migration aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.RESPC-Migration.arn]
}

#=================Layer-2========================#
output "aws_organizations_organizational_unit_Prod-Private" {
  description = "Prod-Private aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Prod-Private.arn]
}

output "aws_organizations_organizational_unit_Prod-Public" {
  description = "Prod-Public aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Prod-Public.arn]
}

output "aws_organizations_organizational_unit_Prod-Hybrid" {
  description = "Prod-Hybrid aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Prod-Hybrid.arn]
}

output "aws_organizations_organizational_unit_NON-Prod-Private" {
  description = "NON-Prod-Private aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.NON-Prod-Private.arn]
}

output "aws_organizations_organizational_unit_NON-Prod-Public" {
  description = "NON-Prod-Public aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.NON-Prod-Public.arn]
}
output "aws_organizations_organizational_unit_NON-Prod-Hybrid" {
  description = "NON-Prod-Hybrid aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.NON-Prod-Hybrid.arn]
}

output "aws_organizations_organizational_unit_Shared-Services-Private" {
  description = "Shared-Services-Private aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Shared-Services-Private.arn]
}

output "aws_organizations_organizational_unit_Shared-Services-Public" {
  description = "Shared-Services-Public aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Shared-Services-Public.arn]
}

output "aws_organizations_organizational_unit_Shared-Services-Hybrid" {
  description = "Shared-Services-Hybrid aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Shared-Services-Hybrid.arn]
}

output "aws_organizations_organizational_unit_Migration-RESPC-SES" {
  description = "Migration-RESPC-SES aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Migration-RESPC-SES.arn]
}

output "aws_organizations_organizational_unit_Migration-RESPC-SEUK" {
  description = "Migration-RESPC-SEUK aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Migration-RESPC-SEUK.arn]
}

output "aws_organizations_organizational_unit_Migration-Legacy" {
  description = "Migration-Legacy aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Migration-Legacy.arn]
}

#==============================Layer-3======================================#
output "aws_organizations_organizational_unit_Prod-Private-BC" {
  description = "Prod-Private-BC aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Prod-Private-BC.arn]
}

output "aws_organizations_organizational_unit_Prod-Private-NON-BC" {
  description = "Prod-Private-NON-BC aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Prod-Private-NON-BC.arn]
}

output "aws_organizations_organizational_unit_Prod-Private-Service-Deviation" {
  description = "Prod-Private-Service-Deviation aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Prod-Private-Service-Deviation.arn]
}

output "aws_organizations_organizational_unit_Prod-Public-BC" {
  description = "Prod-Public-BC aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Prod-Public-BC.arn]
}

output "aws_organizations_organizational_unit_Prod-Public-NON-BC" {
  description = "BC-NON-Prod-Private aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Prod-Public-NON-BC.arn]
}

output "aws_organizations_organizational_unit_Prod-Public-Service-Deviation" {
  description = "Prod-Public-Service-Deviation aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Prod-Public-Service-Deviation.arn]
}

output "aws_organizations_organizational_unit_Prod-Hybrid-BC" {
  description = "Prod-Hybrid-BC aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Prod-Hybrid-BC.arn]
}

output "aws_organizations_organizational_unit_Prod-Hybrid-NON-BC" {
  description = "Prod-Hybrid-NON-BC aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Prod-Hybrid-NON-BC.arn]
}

output "aws_organizations_organizational_unit_Prod-Hybrid-Service-Deviation" {
  description = "Prod-Hybrid-Service-Deviation aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Prod-Hybrid-Service-Deviation.arn]
}

output "aws_organizations_organizational_unit_NON-Prod-Private-BC" {
  description = "NON-Prod-Private-BC aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.NON-Prod-Private-BC.arn]
}

output "aws_organizations_organizational_unit_NON-Prod-Private-NON-BC" {
  description = "NON-PROD-Private-NON-BC aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.NON-Prod-Private-NON-BC.arn]
}

output "aws_organizations_organizational_unit_NON-Prod-Private-Service-Deviation" {
  description = "NON-Prod-Private-Service-Deviation aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.NON-Prod-Private-Service-Deviation.arn]
}

output "aws_organizations_organizational_unit_NON-Prod-Public-BC" {
  description = "NON-Prod-Public-BC aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.NON-Prod-Public-BC.arn]
}

output "aws_organizations_organizational_unit_NON-Prod-Public-NON-BC" {
  description = "NON-Prod-Public-NON-BC aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.NON-Prod-Public-NON-BC.arn]
}

output "aws_organizations_organizational_unit_NON-Prod-Public-Service-Deviation" {
  description = "NON-Prod-Public-Service-Deviation aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.NON-Prod-Public-Service-Deviation.arn]
}

output "aws_organizations_organizational_unit_NON-Prod-Hybrid-BC" {
  description = "NON-Prod-Hybrid-BC aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.NON-Prod-Hybrid-BC.arn]
}

output "aws_organizations_organizational_unit_NON-Prod-Hybrid-NON-BC" {
  description = "NON-Prod-Hybrid-NON-BC aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.NON-Prod-Hybrid-NON-BC.arn]
}

output "aws_organizations_organizational_unit_NON-Prod-Hybrid-Service-Deviation" {
  description = "NON-Prod-Hybrid-Service-Deviation aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.NON-Prod-Hybrid-Service-Deviation.arn]
}

output "aws_organizations_organizational_unit_Shared-Services-Private-Data-Science" {
  description = "Shared-Services-Private-Data-Science aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Shared-Services-Private-Data-Science.arn]
}

output "aws_organizations_organizational_unit_Shared-Services-Private-Endpoint" {
  description = "Shared-Services-Private-Endpoint aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Shared-Services-Private-Endpoint.arn]
}

output "aws_organizations_organizational_unit_Shared-Services-Public-WIZ" {
  description = "Shared-Services-Public-WIZ aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Shared-Services-Public-WIZ.arn]
}

output "aws_organizations_organizational_unit_Shared-Services-Public-Saving-Plan" {
  description = "Shared-Services-Public-Saving-Plan aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Shared-Services-Public-Saving-Plan.arn]
}

output "aws_organizations_organizational_unit_Shared-Services-Hybrid-Managed-Services" {
  description = "Shared-Services-Hybrid-Managed-Services aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Shared-Services-Hybrid-Managed-Services.arn]
}

output "aws_organizations_organizational_unit_Shared-Services-Hybrid-Managed-EKS" {
  description = "Shared-Services-Hybrid-Managed-EKS aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Shared-Services-Hybrid-Managed-EKS.arn]
}

output "aws_organizations_organizational_unit_Shared-Services-Hybrid-IAC-Vault" {
  description = "Shared-Services-Hybrid-IAC-Vault aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Shared-Services-Hybrid-IAC-Vault.arn]
}

output "aws_organizations_organizational_unit_Shared-Services-Hybrid-Data-Platform" {
  description = "Shared-Services-Hybrid-Data-Platform aws organizations organizational unit arn"
  value       = [aws_organizations_organizational_unit.Shared-Services-Hybrid-Data-Platform.arn]
}