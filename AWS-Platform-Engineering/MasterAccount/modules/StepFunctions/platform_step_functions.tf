# Network State Machine
resource "aws_sfn_state_machine" "network_state_machine" {
  name     = "platform_Network_Statemachine"
  role_arn = var.role_arn

  definition = data.template_file.network_state_machine_template.rendered

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# AVM State Machine
resource "aws_sfn_state_machine" "avm_state_machine" {
  name     = "platform_AVMStatemachine"
  role_arn = var.role_arn

  definition = data.template_file.avm_state_machine_template.rendered

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# Account Update State Machine
resource "aws_sfn_state_machine" "account_update_state_machine" {
  name     = "platform_AccountUpdateAutomation"
  role_arn = var.role_arn

  definition = data.template_file.account_update_state_machine_template.rendered

  tags = {
    "platform_donotdelete" = "yes"
  }
}