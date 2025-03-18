#====================Layer-1===================#

resource "aws_organizations_policy" "Prod-Tagging-Restriction" {
  name = "platform_nested_ou_prod_tagging_restriction"
  description = "This SCP is for restrictions on tagging. "
  content = file("SCPDefinitions/SCPD0002-ProdTaggingRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

#========================Layer-2====================#

resource "aws_organizations_policy" "Prod-Private-Region-Restriction" {
  name = "platform_nested_ou_prod_private_region_restriction"
  description = "This SCP is for restrictions on Region. "
  content = file("SCPDefinitions/SCPD0003-ProdPrivateRegionRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Hybrid-Region-Restriction" {
  name = "platform_nested_ou_prod_hybrid_region_restriction"
  description = "This SCP is for restrictions on Region. "
  content = file("SCPDefinitions/SCPD0004-ProdHybridRegionRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Public-Region-Restriction" {
  name = "platform_nested_ou_prod_public_region_restriction"
  description = "This SCP is for restrictions on Region. "
  content = file("SCPDefinitions/SCPD0005-ProdPublicRegionRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Private-Deny-Restriction" {
  name = "platform_nested_ou_prod_private_deny_restriction"
  description = "This SCP is for restrictions on OU Level actions. "
  content = file("SCPDefinitions/SCPD0006-ProdPrivateDenyRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Hybrid-Deny-Restriction" {
  name = "platform_nested_ou_prod_hybrid_deny_restriction"
  description = "This SCP is for restrictions on OU Level actions. "
  content = file("SCPDefinitions/SCPD0007-ProdHybridDenyRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Public-Deny-Restriction" {
  name = "platform_nested_ou_prod_public_deny_restriction"
  description = "This SCP is for restrictions on OU Level actions. "
  content = file("SCPDefinitions/SCPD0008-ProdPublicDenyRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Private-Management-Restriction" {
  name = "platform_nested_ou_prod_private_management_restriction"
  description = "This SCP is for restrictions by Management. "
  content = file("SCPDefinitions/SCPD0009-ProdPrivateManagementRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Hybrid-Management-Restriction" {
  name = "platform_nested_ou_prod_hybrid_management_restriction"
  description = "This SCP is for restrictions by Management. "
  content = file("SCPDefinitions/SCPD0010-ProdHybridManagementRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Public-Management-Restriction" {
  name = "platform_nested_ou_prod_public_management_restriction"
  description = "This SCP is for restrictions by Management. "
  content = file("SCPDefinitions/SCPD0011-ProdPublicManagementRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

#========================Layer-3=======================#

resource "aws_organizations_policy" "Prod-Private-BC-Service-Restriction" {
  name = "platform_nested_ou_prod_private_bc_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0012-ProdPrivateBCServiceRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Private-BC-DB-Restriction" {
  name = "platform_nested_ou_prod_private_bc_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0012-ProdPrivateBCServiceRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Private-NON-BC-Service-Restriction" {
  name = "platform_nested_ou_prod_private_non_bc_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0013-ProdPrivateNONBCServiceRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Private-NON-BC-DB-Restriction" {
  name = "platform_nested_ou_prod_private_non_bc_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0013-ProdPrivateNONBCServiceRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Private-Deviation-Service-Restriction" {
  name = "platform_nested_ou_prod_private_deviation_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0014-ProdPrivateDeviationServiceRestriction/scp_1.json")   #Need to create SCP for Prod-Private Service Deviation#
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Private-Deviation-DB-Restriction" {
  name = "platform_nested_ou_prod_private_deviation_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0014-ProdPrivateDeviationServiceRestriction/scp_2.json")   #Need to create SCP for Prod-Private Service Deviation#
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Hybrid-BC-Service-Restriction" {
  name = "platform_nested_ou_prod_hybrid_bc_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0015-ProdHybridBCServiceRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Hybrid-BC-DB-Restriction" {
  name = "platform_nested_ou_prod_hybrid_bc_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0015-ProdHybridBCServiceRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Hybrid-NON-BC-Service-Restriction" {
  name = "platform_nested_ou_prod_hybrid_non_bc_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0016-ProdHybridNONBCServiceRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Hybrid-NON-BC-DB-Restriction" {
  name = "platform_nested_ou_prod_hybrid_non_bc_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0016-ProdHybridNONBCServiceRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Hybrid-Deviation-Service-Restriction" {
  name = "platform_nested_ou_prod_hybrid_deviation_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0017-ProdHybridDeviationServiceRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Hybrid-Deviation-DB-Restriction" {
  name = "platform_nested_ou_prod_hybrid_deviation_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0017-ProdHybridDeviationServiceRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Public-BC-Service-Restriction" {
  name = "platform_nested_ou_prod_public_bc_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0018-ProdPublicBCServiceRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Public-BC-DB-Restriction" {
  name = "platform_nested_ou_prod_public_bc_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0018-ProdPublicBCServiceRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Public-NON-BC-Service-Restriction" {
  name = "platform_nested_ou_prod_public_non_bc_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0019-ProdPublicNONBCServiceRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Public-NON-BC-DB-Restriction" {
  name = "platform_nested_ou_prod_public_non_bc_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0019-ProdPublicNONBCServiceRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Public-Deviation-Service-Restriction" {
  name = "platform_nested_ou_prod_public_deviation_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0020-ProdPublicDeviationServiceRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Prod-Public-Deviation-DB-Restriction" {
  name = "platform_nested_ou_prod_public_deviation_db_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0020-ProdPublicDeviationServiceRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}