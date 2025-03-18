resource "aws_ssm_association" "create_association_linuxadjoin" {
  count               =  contains(split(",", var.SSMParameters.whitelisted_regions_private), data.aws_region.current.name) && var.Connectivity == "PVT" ? 1 : 0

  name = "AWS-RunRemoteScript"
  schedule_expression = "rate(60 minutes)"

  parameters = {
    commandLine      = var.SSMParameters.domainjoin_linux_mainfilename
    executionTimeout = var.SSMParameters.platform_execution_timeout
    sourceInfo       = jsonencode({path = replace(var.SSMParameters.domainjoin_linuxmainURL,"\"", "")})
    sourceType       = "S3"
    workingDirectory = var.SSMParameters.domainjoin_linuxpath
  }

  targets {
    key    = "tag:platform_domainjoin_linux"
    values = ["yes"]
  }

  association_name = "platform-Domainjoinmain-Linux"
}

resource "aws_ssm_association" "create_association_winadjoin_us" {
  count               =  data.aws_region.current.name == "us-east-1" && var.Connectivity == "PVT" ? 1 : 0
  
  name = "AWS-RunRemoteScript"
  schedule_expression = "rate(60 minutes)"

  parameters = {
    commandLine      = var.SSMParameters.domainjoin_windows_filename
    executionTimeout = var.SSMParameters.platform_execution_timeout
    sourceInfo       = jsonencode({path = replace(var.SSMParameters.domainjoin_windowsURL_us,"\"", "")})
    sourceType       = "S3"
    workingDirectory = var.SSMParameters.domainjoin_windows_path
  }

  targets {
    key    = "tag:platform_domainjoin_windows"
    values = ["yes"]
  }

  association_name = "platform-Domainjoinmain-Windows"
}

resource "aws_ssm_association" "create_association_winadjoin_eu" {
  count               =  data.aws_region.current.name == "eu-west-1" && var.Connectivity == "PVT" ? 1 : 0
  
  name = "AWS-RunRemoteScript"
  schedule_expression = "rate(60 minutes)"

  parameters = {
    commandLine      = var.SSMParameters.domainjoin_windows_filename
    executionTimeout = var.SSMParameters.platform_execution_timeout
    sourceInfo       = jsonencode({path = replace(var.SSMParameters.domainjoin_windowsURL_eu,"\"", "")})
    sourceType       = "S3"
    workingDirectory = var.SSMParameters.domainjoin_windows_path
  }

  targets {
    key    = "tag:platform_domainjoin_windows"
    values = ["yes"]
  }

  association_name = "platform-Domainjoinmain-Windows"
}

resource "aws_ssm_association" "create_association_winadjoin_sg" {
  count               =  data.aws_region.current.name == "ap-southeast-1" && var.Connectivity == "PVT" ? 1 : 0
  
  name = "AWS-RunRemoteScript"
  schedule_expression = "rate(60 minutes)"

  parameters = {
    commandLine      = var.SSMParameters.domainjoin_windows_filename
    executionTimeout = var.SSMParameters.platform_execution_timeout
    sourceInfo       = jsonencode({path = replace(var.SSMParameters.domainjoin_windowsURL_sg,"\"", "")})
    sourceType       = "S3"
    workingDirectory = var.SSMParameters.domainjoin_windows_path
  }

  targets {
    key    = "tag:platform_domainjoin_windows"
    values = ["yes"]
  }

  association_name = "platform-Domainjoinmain-Windows"
}
resource "aws_ssm_association" "create_association_aws_managed_ad_domainjoin_us" {
  count = contains(split("-", var.ProvisionedProduct.OU), "Hybrid") && var.RequestEventData.IsRESPCAccount == "Yes" && data.aws_region.current.name == "us-east-1" ? 1 : 0

  name = "AWS-JoinDirectoryServiceDomain"
  schedule_expression = "rate(60 minutes)"

  parameters = {
    directoryId       = var.SSMParameters.directoryIduseast1
    directoryName     = var.SSMParameters.directoryNameuseast1
    directoryOU       = "OU=${var.RequestEventData.HybridRESPCAccountDomainJoinOUName},OU=RESPC,OU=${split(".", var.SSMParameters.directoryNameuseast1)[0]},DC=${split(".", var.SSMParameters.directoryNameuseast1)[0]},DC=${split(".", var.SSMParameters.directoryNameuseast1)[1]},DC=${split(".", var.SSMParameters.directoryNameuseast1)[2]},DC=${split(".", var.SSMParameters.directoryNameuseast1)[3]}"
    dnsIpAddresses    = var.SSMParameters.dnsIpAddressesuseast1
  }

  targets {
    key    = "tag:platform_aws_managed_ad_domainjoin"
    values = ["yes"]
  }

  association_name = "platform-AWS-managed-AD-domainjoin"
}

resource "aws_ssm_association" "create_association_aws_managed_ad_domainjoin_eu" {
  count = contains(split("-", var.ProvisionedProduct.OU), "Hybrid") && var.RequestEventData.IsRESPCAccount == "Yes" && data.aws_region.current.name == "eu-west-1" ? 1 : 0

  name = "AWS-JoinDirectoryServiceDomain"
  schedule_expression = "rate(60 minutes)"

  parameters = {
    directoryId       = var.SSMParameters.directoryIdeuwest1
    directoryName     = var.SSMParameters.directoryNameeuwest1
    directoryOU       = "OU=${var.RequestEventData.HybridRESPCAccountDomainJoinOUName},OU=RESPC,OU=${split(".", var.SSMParameters.directoryNameeuwest1)[0]},DC=${split(".", var.SSMParameters.directoryNameeuwest1)[0]},DC=${split(".", var.SSMParameters.directoryNameeuwest1)[1]},DC=${split(".", var.SSMParameters.directoryNameeuwest1)[2]},DC=${split(".", var.SSMParameters.directoryNameeuwest1)[3]}"
    dnsIpAddresses    = var.SSMParameters.dnsIpAddresseseuwest1
  }

  targets {
    key    = "tag:platform_aws_managed_ad_domainjoin"
    values = ["yes"]
  }

  association_name = "platform-AWS-managed-AD-domainjoin"
}

resource "aws_ssm_association" "create_association_aws_managed_ad_domainjoin_sg" {
  count = contains(split("-", var.ProvisionedProduct.OU), "Hybrid") && var.RequestEventData.IsRESPCAccount == "Yes" && data.aws_region.current.name == "ap-southeast-1"? 1 : 0

  name = "AWS-JoinDirectoryServiceDomain"
  schedule_expression = "rate(60 minutes)"

  parameters = {
    directoryId       = var.SSMParameters.directoryIdapsoutheast1
    directoryName     = var.SSMParameters.directoryNameapsoutheast1
    directoryOU       = "OU=${var.RequestEventData.HybridRESPCAccountDomainJoinOUName},OU=RESPC,OU=${split(".", var.SSMParameters.directoryNameapsoutheast1)[0]},DC=${split(".", var.SSMParameters.directoryNameapsoutheast1)[0]},DC=${split(".", var.SSMParameters.directoryNameapsoutheast1)[1]},DC=${split(".", var.SSMParameters.directoryNameapsoutheast1)[2]},DC=${split(".", var.SSMParameters.directoryNameapsoutheast1)[3]}"
    dnsIpAddresses    = var.SSMParameters.dnsIpAddressesapsoutheast1
  }

  targets {
    key    = "tag:platform_aws_managed_ad_domainjoin"
    values = ["yes"]
  }

  association_name = "platform-AWS-managed-AD-domainjoin"
}