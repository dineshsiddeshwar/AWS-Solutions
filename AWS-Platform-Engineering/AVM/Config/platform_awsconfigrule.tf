locals {
  platform_tag = {
    platform_donotdelete = "yes"
  }

  Platform-Tags = {
    "tag1Key"   = "platform_STC"
    "tag1Value" = var.RequestEventData.SoldToCode
    "tag2Key"   = "platform_LOB"
    "tag2Value" = var.RequestEventData.LOB
    "tag3Key"   = "platform_IsRESPCAccount"
    "tag3Value" = var.RequestEventData.IsRESPCAccount
    "tag4Key"   = "platform_Apexid"
    "tag4Value" = var.RequestEventData.ApexID
    "tag5Key"   = "platform_RequestNo"
    "tag5Value" = var.RequestEventData.RequestNo
    "tag6Key"   = "platform_Custodian"
    "tag6Value" = var.RequestEventData.CustodianUser
  }
  Backup-Tag = {
    "tag1Key" = "platform_Backup"
  }
}

data "aws_region" "current" {}

resource "aws_config_config_rule" "aws_config_auto_tag_pvt" {
  count               =  contains(split(",", var.SSMParameters.whitelisted_regions_private), data.aws_region.current.name) && var.Connectivity == "PVT" ? 1 : 0
  
  name = "platform_Auto-Tag"

  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }
  tags = local.platform_tag
  input_parameters = jsonencode(local.Platform-Tags)
}

resource "aws_config_config_rule" "aws_config_auto_tag_pub" {
  count               =  var.Connectivity == "PUB" ? 1 : 0
  
  name = "platform_Auto-Tag"

  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }
  tags = local.platform_tag
  input_parameters = jsonencode(local.Platform-Tags)
}


resource "aws_config_config_rule" "aws_config_auto_tag_backup_pvt" {
  count               =  contains(split(",", var.SSMParameters.whitelisted_regions_private), data.aws_region.current.name) && var.Connectivity == "PVT" ? 1 : 0
  
  name = "platform_Auto-Backup-Tag"
  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }
  tags = local.platform_tag
  input_parameters = jsonencode(local.Backup-Tag)
}

resource "aws_config_config_rule" "aws_config_auto_tag_backup_pub" {
  count               =  var.Connectivity == "PUB" ? 1 : 0
  
  name = "platform_Auto-Backup-Tag"
  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }
  tags = local.platform_tag
  input_parameters = jsonencode(local.Backup-Tag)
}

