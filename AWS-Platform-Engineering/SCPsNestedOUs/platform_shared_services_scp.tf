#========================Layer-2====================#

resource "aws_organizations_policy" "Shared-Services-Private-Region-Restriction" {
  name = "platform_nested_ou_shared_services_private_region_restriction"
  description = "This SCP is for restrictions on Region. "
  content = file("SCPDefinitions/SCPD0040-SharedServicesPrivateRegionRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Shared-Services-Hybrid-Region-Restriction" {
  name = "platform_nested_ou_shared_services_hybrid_region_restriction"
  description = "This SCP is for restrictions on Region. "
  content = file("SCPDefinitions/SCPD0041-SharedServicesHybridRegionRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Shared-Services-Public-Region-Restriction" {
  name = "platform_nested_ou_shared_services_public_region_restriction"
  description = "This SCP is for restrictions on Region. "
  content = file("SCPDefinitions/SCPD0042-SharedServicesPublicRegionRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

#========================Layer-3=======================#

resource "aws_organizations_policy" "Shared-Services-Private-DataSCI-Service-Restriction" {
  name = "platform_nested_ou_shared_services_private_data_science_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0043-SharedServicesPrivateDataScienceServiceRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Shared-Services-Private-EndPoints-Service-Restriction" {
  name = "platform_nested_ou_shared_services_private_endpoints_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0044-SharedServicesPrivateEndpointServiceRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}


resource "aws_organizations_policy" "Shared-Services-Private-DataSCI-IAM-Restriction" {
  name = "platform_nested_ou_shared_services_private_data_science_iam_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0051-SharedServicesPrivateDataScienceIAMRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Shared-Services-Private-EndPoints-IAM-Restriction" {
  name = "platform_nested_ou_shared_services_private_endpoints_iam_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0052-SharedServicesPrivateEndpointIAMRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Shared-Services-Hybrid-Managed-EKS-Service-Restriction" {
  name = "platform_nested_ou_shared_services_hybrid_managed_eks_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0045-SharedServicesHybridManagedEKSServiceRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Shared-Services-Hybrid-IACVault-Service-Restriction" {
  name = "platform_nested_ou_shared_services_hybrid_iac_vault_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0046-SharedServicesHybridIaCVaultServiceRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Shared-Services-Hybrid-Data-Platform-Service-Restriction" {
  name = "platform_nested_ou_shared_services_hybrid_data_platform_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0047-SharedServicesHybridDataPlatformServiceRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Shared-Services-Hybrid-Managed-Serv-Service-Restriction" {
  name = "platform_nested_ou_shared_services_hybrid_managed_services_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0048-SharedServicesHybridManagedServicesServiceRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Shared-Services-Hybrid-Managed-EKS-IAM-Restriction" {
  name = "platform_nested_ou_shared_services_hybrid_managed_eks_iam_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0053-SharedServicesHybridManagedEKSIAMRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}


resource "aws_organizations_policy" "Shared-Services-Hybrid-IACVault-IAM-Restriction" {
  name = "platform_nested_ou_shared_services_hybrid_iac_vault_iam_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0054-SharedServicesHybridIaCVaultIAMRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Shared-Services-Hybrid-Data-Platform-IAM-Restriction" {
  name = "platform_nested_ou_shared_services_hybrid_data_platform_iam_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0055-SharedServicesHybridDataPlatformIAMRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Shared-Services-Hybrid-Managed-Serv-IAM-Restriction" {
  name = "platform_nested_ou_shared_services_hybrid_managed_services_iam_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0056-SharedServicesHybridManagedServicesIAMRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Shared-Services-Public-Savings-Service-Restriction" {
  name = "platform_nested_ou_shared_services_public_savings_plan_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0049-SharedServicesPublicSavingPlanServiceRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Shared-Services-Public-WIZ-Service-Restriction" {
  name = "platform_nested_ou_shared_services_public_wiz_service_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0050-SharedServicesPublicWizServiceRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Shared-Services-Public-Savings-IAM-Restriction" {
  name = "platform_nested_ou_shared_services_public_savings_plan_iam_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0057-SharedServicesPublicSavingPlanIAMRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Shared-Services-Public-WIZ-IAM-Restriction" {
  name = "platform_nested_ou_shared_services_public_wiz_iam_restriction"
  description = "This SCP is for restrictions on Service. "
  content = file("SCPDefinitions/SCPD0058-SharedServicesPublicWizIAMRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

