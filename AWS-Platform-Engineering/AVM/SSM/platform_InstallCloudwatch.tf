resource "aws_ssm_association" "create_cloudwatch_agent_install_association_pvt" {
  count               =  contains(split(",", var.SSMParameters.whitelisted_regions_private), data.aws_region.current.name) && var.Connectivity == "PVT" ? 1 : 0

  name = "AWS-ConfigureAWSPackage"
  schedule_expression = "rate(240 minutes)"
  
  parameters = {
    action      = "Install"
    version     = "latest"
    name        = "AmazonCloudWatchAgent"
  }

  targets {
    key    = "tag:platform_cloudwatch"
    values = ["yes"]
  }

  association_name = "platform_InstallCloudWatchAgent"
}

resource "aws_ssm_association" "create_cloudwatch_agent_install_association_pub" {
  count               =  var.Connectivity == "PUB" ? 1 : 0

  name = "AWS-ConfigureAWSPackage"
  schedule_expression = "rate(240 minutes)"
  
  parameters = {
    action      = "Install"
    version     = "latest"
    name        = "AmazonCloudWatchAgent"
  }

  targets {
    key    = "tag:platform_cloudwatch"
    values = ["yes"]
  }

  association_name = "platform_InstallCloudWatchAgent"
}

resource "aws_ssm_association" "create_cloudwatch_agent_configuration_association_linux_pvt" {
  count               =  contains(split(",", var.SSMParameters.whitelisted_regions_private), data.aws_region.current.name) && var.Connectivity == "PVT" ? 1 : 0

  name = "AmazonCloudWatch-ManageAgent"
  schedule_expression = "rate(240 minutes)"
  
  parameters = {
    action      = "configure"
    optionalConfigurationSource     = "ssm"
    optionalConfigurationLocation   = "platform_AmazonCloudWatch-Linux"
    optionalRestart   = "yes"
    mode   = "ec2"
  }

  targets {
    key    = "tag:platform_cloudwatch_linux"
    values = ["yes"]
  }

  association_name = "platform_AmazonCloudWatch-Linux"
}

resource "aws_ssm_association" "create_cloudwatch_agent_configuration_association_linux_pub" {
  count               =  var.Connectivity == "PUB" ? 1 : 0

  name = "AmazonCloudWatch-ManageAgent"
  schedule_expression = "rate(240 minutes)"
  
  parameters = {
    action      = "configure"
    optionalConfigurationSource     = "ssm"
    optionalConfigurationLocation   = "platform_AmazonCloudWatch-Linux"
    optionalRestart   = "yes"
    mode   = "ec2"
  }

  targets {
    key    = "tag:platform_cloudwatch_linux"
    values = ["yes"]
  }

  association_name = "platform_AmazonCloudWatch-Linux"
}


resource "aws_ssm_association" "create_ssm_agent_configuration_association_windows_pvt" {
  count               =  contains(split(",", var.SSMParameters.whitelisted_regions_private), data.aws_region.current.name) && var.Connectivity == "PVT" ? 1 : 0
  
  name = "AmazonCloudWatch-ManageAgent"
  schedule_expression = "rate(240 minutes)"
  
  parameters = {
    action      = "configure"
    optionalConfigurationSource     = "ssm"
    optionalConfigurationLocation   = "platform_AmazonCloudWatch-windows"
    optionalRestart   = "yes"
    mode   = "ec2"
  }

  targets {
    key    = "tag:platform_cloudwatch_windows"
    values = ["yes"]
  }

  association_name = "platform_AmazonCloudWatch-windows"
}

resource "aws_ssm_association" "create_ssm_agent_configuration_association_windows_pub" {
  count               =  var.Connectivity == "PUB" ? 1 : 0
  
  name = "AmazonCloudWatch-ManageAgent"
  schedule_expression = "rate(240 minutes)"
  
  parameters = {
    action      = "configure"
    optionalConfigurationSource     = "ssm"
    optionalConfigurationLocation   = "platform_AmazonCloudWatch-windows"
    optionalRestart   = "yes"
    mode   = "ec2"
  }

  targets {
    key    = "tag:platform_cloudwatch_windows"
    values = ["yes"]
  }

  association_name = "platform_AmazonCloudWatch-windows"
}