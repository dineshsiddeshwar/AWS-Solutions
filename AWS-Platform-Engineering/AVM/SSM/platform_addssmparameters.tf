data "aws_region" "current" {}
locals {
  Platform-Tag = {
    platform_STC = var.RequestEventData.SoldToCode
    platform_LOB = var.RequestEventData.LOB
    platform_IsRESPCAccount = var.RequestEventData.IsRESPCAccount
    platform_Apexid = var.RequestEventData.ApexID
    platform_RequestNo = var.RequestEventData.RequestNo
    platform_Custodian = var.RequestEventData.CustodianUser
    platform_DL = var.RequestEventData.SupportDL
    platform_AccountType = var.ProvisionedProduct.OU
    platform_WhitelistedRegions = var.Connectivity == "PVT" ? var.SSMParameters.whitelisted_regions_private : var.SSMParameters.whitelisted_regions
    platform_SOX = var.RequestEventData.SOXrelevant,
    platform_BIA = var.RequestEventData.ActiveBIAid,
    platform_DataClassification = var.RequestEventData.DataClassification,
    platform_Tenancy = var.RequestEventData.AccountTenancy
  }
  Backup-Tag = {
    platform_backup = "Yes"
  }

}
resource "aws_ssm_parameter" "create_account_level_ssm_parameters_us" {
  for_each = local.Platform-Tag

  name      = "/Platform-Tag/${each.key}"
  type      = "String"
  value     = each.value
}

resource "aws_ssm_parameter" "create_account_level_ssm_parameters_backup" {
  name      = "/Platform-Backup-Tag/platform_Backup"
  type      = "String"
  value     = "Yes"
}

resource "aws_ssm_parameter" "create_account_level_ssm_parameters_amiowners" {
  count =  data.aws_region.current.name == "us-east-1" ? 1: 0

  name      = "platform_ami_owner_account"
  type      = "StringList"
  value     = var.SSMParameters.ami_owner_account
}

resource "aws_ssm_parameter" "create_account_level_ssm_parameters_amitag" {
  count =  data.aws_region.current.name == "us-east-1" ? 1: 0

  name      = "platform_ami_tags"
  type      = "StringList"
  value     = var.SSMParameters.ami_tags 
}

resource "aws_ssm_parameter" "create_account_level_ssm_parameters_amilist" {
  count =  data.aws_region.current.name == "us-east-1" ? 1: 0

  name      = "platform_TOE_Complaint_OS_list"
  type      = "StringList"
  value     = var.Connectivity == "PVT" ? var.SSMParameters.TOE_Complaint_OS_Flavours_Private : var.SSMParameters.TOE_Complaint_OS_Flavours_Public
}

resource "aws_ssm_parameter" "create_account_level_ssm_parameters_regions" {
  count =  data.aws_region.current.name == "us-east-1" ? 1: 0

  name      = "platform_whitelisted_regions"
  type      = "String"
  value     = var.Connectivity == "PVT" ? var.SSMParameters.whitelisted_regions_private : var.SSMParameters.whitelisted_regions
}


resource "aws_ssm_parameter" "create_account_level_ssm_parameters_accounttype" {
  count =  data.aws_region.current.name == "us-east-1" ? 1: 0

  name      = "platform_account_type"
  type      = "String"
  value     = contains(split("-", var.ProvisionedProduct.OU), "Private") ? "private" : (contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "hybrid" : "public")
}