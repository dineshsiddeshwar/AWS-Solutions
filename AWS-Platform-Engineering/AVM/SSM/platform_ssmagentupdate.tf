resource "aws_ssm_association" "create_ssm_agent_update_association_pvt" {
  count               =  contains(split(",", var.SSMParameters.whitelisted_regions_private), data.aws_region.current.name) && var.Connectivity == "PVT" ? 1 : 0
  
  name = "AWS-UpdateSSMAgent"
  schedule_expression = "cron(0 2 ? * SUN *)"
  
  targets {
    key    = "tag:platform_ssminstall"
    values = ["yes"]
  }

  association_name = "platform_update_ssm_agent"
}

resource "aws_ssm_association" "create_ssm_agent_update_association_pub" {
  count               =  var.Connectivity == "PUB" ? 1 : 0
  
  name = "AWS-UpdateSSMAgent"
  schedule_expression = "cron(0 2 ? * SUN *)"
  
  targets {
    key    = "tag:platform_ssminstall"
    values = ["yes"]
  }

  association_name = "platform_update_ssm_agent"
}