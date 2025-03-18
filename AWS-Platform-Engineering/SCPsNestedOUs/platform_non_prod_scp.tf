#====================Layer-1===================#

resource "aws_organizations_policy" "NON-Prod-Tagging-Restriction" {
  name = "platform_nested_ou_non_prod_tagging_restriction"
  description = "This SCP is for restrictions on tagging. "
  content = file("SCPDefinitions/SCPD0021-NonProdTaggingRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

#========================Layer-2====================#

resource "aws_organizations_policy" "NON-Prod-Private-Region-Restriction" {
  name = "platform_nested_ou_non_prod_private_region_restriction"
  description = "This SCP is for restrictions on Region. "
  content = file("SCPDefinitions/SCPD0022-NonProdPrivateRegionRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Hybrid-Region-Restriction" {
  name = "platform_nested_ou_non_prod_hybrid_region_restriction"
  description = "This SCP is for restrictions on Region. "
  content = file("SCPDefinitions/SCPD0023-NonProdHybridRegionRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Public-Region-Restriction" {
  name = "platform_nested_ou_non_prod_public_region_restriction"
  description = "This SCP is for restrictions on Region. "
  content = file("SCPDefinitions/SCPD0027-NonProdPublicDenyRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Private-Deny-Restriction" {
  name = "platform_nested_ou_non_prod_private_deny_restriction"
  description = "This SCP is for restrictions on OU Level actions. "
  content = file("SCPDefinitions/SCPD0025-NonProdPrivateDenyRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Hybrid-Deny-Restriction" {
  name = "platform_nested_ou_non_prod_hybrid_deny_restriction"
  description = "This SCP is for restrictions on OU Level actions. "
  content = file("SCPDefinitions/SCPD0026-NonProdHybridDenyRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Public-Deny-Restriction" {
  name = "platform_nested_ou_non_prod_public_deny_restriction"
  description = "This SCP is for restrictions on OU Level actions. "
  content = file("SCPDefinitions/SCPD0027-NonProdPublicDenyRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Private-Management-Restriction" {
  name = "platform_nested_ou_non_prod_private_management_restriction"
  description = "This SCP is for restrictions by Management. "
  content = file("SCPDefinitions/SCPD0028-NonProdPrivateManagementRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Hybrid-Management-Restriction" {
  name = "platform_nested_ou_non_prod_hybrid_management_restriction"
  description = "This SCP is for restrictions by Management. "
  content = file("SCPDefinitions/SCPD0029-NonProdHybridManagementRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Public-Management-Restriction" {
  name = "platform_nested_ou_non_prod_public_management_restriction"
  description = "This SCP is for restrictions by Management. "
  content = file("SCPDefinitions/SCPD0030-NonProdPublicManagementRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

#========================Layer-3=======================#

resource "aws_organizations_policy" "NON-Prod-Private-BC-Service-Restriction" {
  name = "platform_nested_ou_non_prod_private_bc_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0031-NonProdPrivateBCServiceRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Private-BC-DB-Restriction" {
  name = "platform_nested_ou_non_prod_private_bc_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0031-NonProdPrivateBCServiceRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Private-NON-BC-Service-Restriction" {
  name = "platform_nested_ou_non_prod_private_non_bc_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0032-NonProdPrivateNONBCServiceRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Private-NON-BC-DB-Restriction" {
  name = "platform_nested_ou_non_prod_private_non_bc_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0032-NonProdPrivateNONBCServiceRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Private-Deviation-Service-Restriction" {
  name = "platform_nested_ou_non_prod_private_deviation_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0033-NonProdPrivateDeviationServiceRestriction/scp_1.json")   #Need to create SCP for Prod-Private Service Deviation#
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Private-Deviation-DB-Restriction" {
  name = "platform_nested_ou_non_prod_private_deviation_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0033-NonProdPrivateDeviationServiceRestriction/scp_2.json")   #Need to create SCP for Prod-Private Service Deviation#
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Hybrid-BC-Service-Restriction" {
  name = "platform_nested_ou_non_prod_hybrid_bc_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0034-NonProdHybridBCServiceRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Hybrid-BC-DB-Restriction" {
  name = "platform_nested_ou_non_prod_hybrid_bc_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0034-NonProdHybridBCServiceRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Hybrid-NON-BC-Service-Restriction" {
  name = "platform_nested_ou_non_prod_hybrid_non_bc_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0035-NonProdHybridNONBCServiceRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Hybrid-NON-BC-DB-Restriction" {
  name = "platform_nested_ou_non_prod_hybrid_non_bc_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0035-NonProdHybridNONBCServiceRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Hybrid-Deviation-Service-Restriction" {
  name = "platform_nested_ou_non_prod_hybrid_deviation_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0036-NonProdHybridDeviationServiceRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Hybrid-Deviation-DB-Restriction" {
  name = "platform_nested_ou_non_prod_hybrid_deviation_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0036-NonProdHybridDeviationServiceRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Public-BC-Service-Restriction" {
  name = "platform_nested_ou_non_prod_public_bc_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0037-NonProdPublicBCServiceRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Public-BC-DB-Restriction" {
  name = "platform_nested_ou_non_prod_public_bc_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0037-NonProdPublicBCServiceRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Public-NON-BC-Service-Restriction" {
  name = "platform_nested_ou_non_prod_public_non_bc_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0038-NonProdPublicNONBCServiceRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Public-NON-BC-DB-Restriction" {
  name = "platform_nested_ou_non_prod_public_non_bc_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0038-NonProdPublicNONBCServiceRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Public-Deviation-Service-Restriction" {
  name = "platform_nested_ou_non_prod_public_deviation_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0039-NonProdPublicDeviationServiceRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "NON-Prod-Public-Deviation-DB-Restriction" {
  name = "platform_nested_ou_non_prod_public_deviation_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0039-NonProdPublicDeviationServiceRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}