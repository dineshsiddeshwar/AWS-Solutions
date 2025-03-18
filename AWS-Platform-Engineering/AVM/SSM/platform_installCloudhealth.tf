resource "aws_ssm_association" "create_install_cloudhealth_agent_association_linux_pvt" {
  count               =  contains(split(",", var.SSMParameters.whitelisted_regions_private), data.aws_region.current.name) && var.Connectivity == "PVT" ? 1 : 0

  name = "AWS-RunRemoteScript"
  schedule_expression = "rate(240 minutes)"

  parameters = {
    commandLine      = var.SSMParameters.platform_ch_linux_filename
    executionTimeout = var.SSMParameters.platform_execution_timeout
    sourceInfo       = jsonencode({path = replace(var.SSMParameters.platform_pvt_ch_linuxpath, "\"", "")})
    sourceType       = "S3"
    workingDirectory = var.SSMParameters.platform_linux_dirpath
  }
  
  targets {
    key    = "tag:platform_cloudhealth_linux"
    values = ["yes"]
  }

  association_name = "platform_InstallCloudhealthagent-Linux"
}

resource "aws_ssm_association" "create_install_cloudhealth_agent_association_linux_pub" {
  count               =  var.Connectivity == "PUB" ? 1 : 0

  name = "AWS-RunRemoteScript"
  schedule_expression = "rate(240 minutes)"

  parameters = {
    commandLine      = var.SSMParameters.platform_ch_linux_filename
    executionTimeout = var.SSMParameters.platform_execution_timeout
    sourceInfo       = jsonencode({path = replace(var.SSMParameters.platform_pub_ch_linuxpath, "\"", "")})
    sourceType       = "S3"
    workingDirectory = var.SSMParameters.platform_linux_dirpath
  }
  
  targets {
    key    = "tag:platform_cloudhealth_linux"
    values = ["yes"]
  }

  association_name = "platform_InstallCloudhealthagent-Linux"
}
resource "aws_ssm_association" "create_install_cloudhealth_agent_association_windows_pvt" {
  count               =  contains(split(",", var.SSMParameters.whitelisted_regions_private), data.aws_region.current.name) && var.Connectivity == "PVT" ? 1 : 0

  name = "AWS-RunRemoteScript"
  schedule_expression = "rate(240 minutes)"

  parameters = {
    commandLine      = var.SSMParameters.platform_ch_win_filename
    executionTimeout = var.SSMParameters.platform_execution_timeout
    sourceInfo       = jsonencode({path = replace(var.SSMParameters.platform_pvt_ch_winpath, "\"", "")})
    sourceType       = "S3"
    workingDirectory = var.SSMParameters.platform_win_dirpath
  }
  
  targets {
    key    = "tag:platform_cloudhealth_windows"
    values = ["yes"]
  }

  association_name = "platform_InstallCloudhealthagent-Windows"
}

resource "aws_ssm_association" "create_install_cloudhealth_agent_association_windows_pub" {
  count               =  var.Connectivity == "PUB" ? 1 : 0

  name = "AWS-RunRemoteScript"
  schedule_expression = "rate(240 minutes)"

  parameters = {
    commandLine      = var.SSMParameters.platform_ch_win_filename
    executionTimeout = var.SSMParameters.platform_execution_timeout
    sourceInfo       = jsonencode({path = replace(var.SSMParameters.platform_pub_ch_winpath,"\"", "")})
    sourceType       = "S3"
    workingDirectory = var.SSMParameters.platform_win_dirpath
  }
  
  targets {
    key    = "tag:platform_cloudhealth_windows"
    values = ["yes"]
  }

  association_name = "platform_InstallCloudhealthagent-Windows"
}