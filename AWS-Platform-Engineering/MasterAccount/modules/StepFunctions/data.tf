# template file for network state machine
data "template_file" "network_state_machine_template" {
  template = "${file("${path.module}/Templates/NetworkProduct.json.tpl")}"

  vars = {
    account_number = var.master_account
    account_region = "us-east-1"
  }
}

# template file for network state machine
data "template_file" "avm_state_machine_template" {
  template = "${file("${path.module}/Templates/AVMStepFunction.json.tpl")}"

  vars = {
    account_number = var.master_account
    account_region = "us-east-1"
  }
}

# template file for Account Update state machine
data "template_file" "account_update_state_machine_template" {
  template = "${file("${path.module}/Templates/AccountUpdateAutomation.json.tpl")}"

  vars = {
    account_number = var.master_account
    account_region = "us-east-1"
  }
}