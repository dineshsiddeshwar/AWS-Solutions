resource "aws_ssm_association" "create_install_flexera_agent_association_linux_pvt_us" {
  count               =  data.aws_region.current.name == "us-east-1" && var.Connectivity == "PVT" ? 1 : 0

  name = "AWS-RunRemoteScript"
  schedule_expression = "rate(240 minutes)"

  parameters = {
    commandLine      = var.SSMParameters.platform_flexera_linux_filename
    executionTimeout = var.SSMParameters.platform_execution_timeout
    sourceInfo       = jsonencode({path = replace(var.SSMParameters.platform_pvt_flexera_linuxpath_us, "\"","")})
    sourceType       = "S3"
    workingDirectory = var.SSMParameters.platform_linux_dirpath
  }
  
  targets {
    key    = "tag:platform_flexera_linux"
    values = ["yes"]
  }

  association_name = "platform_InstallFlexeraAgent-Linux"
}

resource "aws_ssm_association" "create_install_flexera_agent_association_linux_pvt_eu" {
  count               = data.aws_region.current.name == "eu-west-1" && var.Connectivity == "PVT" ? 1 : 0

  name = "AWS-RunRemoteScript"
  schedule_expression = "rate(240 minutes)"

  parameters = {
    commandLine      = var.SSMParameters.platform_flexera_linux_filename
    executionTimeout = var.SSMParameters.platform_execution_timeout
    sourceInfo       = jsonencode({path = replace(var.SSMParameters.platform_pvt_flexera_linuxpath_eu , "\"", "")})
    sourceType       = "S3"
    workingDirectory = var.SSMParameters.platform_linux_dirpath
  }

  targets {
    key    = "tag:platform_flexera_linux"
    values = ["yes"]
  }

  association_name = "platform_InstallFlexeraAgent-Linux"
}
  
resource "aws_ssm_association" "create_install_flexera_agent_association_linux_pvt_sg" {
  count               =  data.aws_region.current.name == "ap-southeast-1" && var.Connectivity == "PVT" ? 1 : 0

  name = "AWS-RunRemoteScript"
  schedule_expression = "rate(240 minutes)"

  parameters = {
    commandLine      = var.SSMParameters.platform_flexera_linux_filename
    executionTimeout = var.SSMParameters.platform_execution_timeout
    sourceInfo       = jsonencode({path = replace(var.SSMParameters.platform_pvt_flexera_linuxpath_sg, "\"", "")})
    sourceType       = "S3"
    workingDirectory = var.SSMParameters.platform_linux_dirpath
  }
  targets {
    key    = "tag:platform_flexera_linux"
    values = ["yes"]
  }

  association_name = "platform_InstallFlexeraAgent-Linux"
}

resource "aws_ssm_association" "create_install_flexera_agent_association_linux_pub" {
  count               =  var.Connectivity == "PUB" ? 1 : 0

  name = "AWS-RunRemoteScript"
  schedule_expression = "rate(240 minutes)"

  parameters = {
    commandLine      = var.SSMParameters.platform_flexera_linux_filename
    executionTimeout = var.SSMParameters.platform_execution_timeout
    sourceInfo       = jsonencode({path = replace(var.SSMParameters.platform_pub_flexera_linuxpath, "\"", "")})
    sourceType       = "S3"
    workingDirectory = var.SSMParameters.platform_linux_dirpath
  }
  targets {
    key    = "tag:platform_flexera_linux"
    values = ["yes"]
  }

  association_name = "platform_InstallFlexeraAgent-Linux"
}

resource "aws_ssm_association" "create_install_flexera_agent_association_windows_pvt_us" {
  count               =  data.aws_region.current.name == "us-east-1" && var.Connectivity == "PVT" ? 1 : 0

  name = "AWS-RunRemoteScript"
  schedule_expression = "rate(240 minutes)"

  parameters = {
    commandLine      = var.SSMParameters.platform_flexera_win_filename
    executionTimeout = var.SSMParameters.platform_execution_timeout
    sourceInfo       = jsonencode({path = replace(var.SSMParameters.platform_pvt_flexera_winpath_us, "\"", "")})
    sourceType       = "S3"
    workingDirectory = var.SSMParameters.platform_win_dirpath
  }
  
  targets {
    key    = "tag:platform_flexera_windows"
    values = ["yes"]
  }

  association_name = "platform_InstallFlexeraAgent-Windows"
}

resource "aws_ssm_association" "create_install_flexera_agent_association_windows_pvt_eu" {
  count               =  data.aws_region.current.name == "eu-west-1" && var.Connectivity == "PVT" ? 1 : 0

  name = "AWS-RunRemoteScript"
  schedule_expression = "rate(240 minutes)"

  parameters = {
    commandLine      = var.SSMParameters.platform_flexera_win_filename
    executionTimeout = var.SSMParameters.platform_execution_timeout
    sourceInfo       = jsonencode({path = replace(var.SSMParameters.platform_pvt_flexera_winpath_eu, "\"", "")})
    sourceType       = "S3"
    workingDirectory = var.SSMParameters.platform_win_dirpath
  }
  
  targets {
    key    = "tag:platform_flexera_windows"
    values = ["yes"]
  }

  association_name = "platform_InstallFlexeraAgent-Windows"
}

resource "aws_ssm_association" "create_install_flexera_agent_association_windows_pvt_sg" {
  count               = data.aws_region.current.name == "ap-southeast-1" && var.Connectivity == "PVT" ? 1 : 0

  name = "AWS-RunRemoteScript"
  schedule_expression = "rate(240 minutes)"

  parameters = {
    commandLine      = var.SSMParameters.platform_flexera_win_filename
    executionTimeout = var.SSMParameters.platform_execution_timeout
    sourceInfo       = jsonencode({path = replace(var.SSMParameters.platform_pvt_flexera_winpath_sg, "\"", "")})
    sourceType       = "S3"
    workingDirectory = var.SSMParameters.platform_win_dirpath
  }
  
  targets {
    key    = "tag:platform_flexera_windows"
    values = ["yes"]
  }

  association_name = "platform_InstallFlexeraAgent-Windows"
}

resource "aws_ssm_association" "create_install_flexera_agent_association_windows_pub" {
  count               =  var.Connectivity == "PUB" ? 1 : 0

  name = "AWS-RunRemoteScript"
  schedule_expression = "rate(240 minutes)"

  parameters = {
    commandLine      = var.SSMParameters.platform_flexera_win_filename
    executionTimeout = var.SSMParameters.platform_execution_timeout
    sourceInfo       = jsonencode({path = replace(var.SSMParameters.platform_pub_flexera_winpath, "\"","")})
    sourceType       = "S3"
    workingDirectory = var.SSMParameters.platform_win_dirpath
  }
  
  targets {
    key    = "tag:platform_flexera_windows"
    values = ["yes"]
  }

  association_name = "platform_InstallFlexeraAgent-Windows"
}