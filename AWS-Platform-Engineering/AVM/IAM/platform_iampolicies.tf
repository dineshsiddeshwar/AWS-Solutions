data "template_file" "policy_platform_cloud_health_policy_template" {
  template = "${file("IAM/Policies/IAMP0001-PlatformCloudHealthPolicy/policy.json.tpl")}"

  vars = {
    cloudhealthbucket = "${var.platform_cloudhealth_bucket}"
  }
}

resource "aws_iam_policy" "policy_platform_cloud_health_policy" {
  name        = "platform_cloud_health_policy"
  path        = "/"
  description = "platform_cloud_health_policy"

  policy = data.template_file.policy_platform_cloud_health_policy_template.rendered
}

data "template_file" "policy_platform_inflation_policy_template" {
  template = "${file("IAM/Policies/IAMP0002-PlatformInflationPolicy/policy.json.tpl")}"

  vars = {
    childaccount = "${var.child_accountnumber}"
  }
}

resource "aws_iam_policy" "policy_platform_inflation_policy" {
  name        = "platform_inflation_policy"
  path        = "/"
  description = "platform_inflation_policy"

  policy = data.template_file.policy_platform_inflation_policy_2_template.rendered
}

data "template_file" "policy_platform_inflation_policy_2_template" {
  template = "${file("IAM/Policies/IAMP0003-PlatformInflationPolicy2/policy.json.tpl")}"

  vars = {
    childaccount = "${var.child_accountnumber}"
  }
}

resource "aws_iam_policy" "policy_platform_inflation_policy_2" {
  name        = "platform_inflation_policy_2"
  path        = "/"
  description = "platform_inflation_policy_2"

  policy = data.template_file.policy_platform_inflation_policy_2_template.rendered
}

resource "aws_iam_policy" "policy_platform_iam_pass_role_policy" {
  name        = "platform_iam_pass_role_policy"
  path        = "/"
  description = "Policy to pass IAM Role for Maintenance Window Task Orchestration"

  policy = file("IAM/Policies/IAMP0004-PlatformIamPassRolePolicy/policy.json")
}

resource "aws_iam_policy" "policy_platform_sts_full_access_policy" {
  name        = "platform_sts_full_access"
  path        = "/"
  description = "Policy to give full access to assume the role"

  policy = file("IAM/Policies/IAMP0005-PlatformStsFullAccessPolicy/policy.json")
}

resource "aws_iam_policy" "policy_platform_sts_ec2instance_policy" {
  name        = "platform_ec2instance_policy"
  path        = "/"
  description = "Policy to give full access to assume the role"

  policy = file("IAM/Policies/IAMP0006-PlatformEC2Instance${var.Env_type}Policy/policy.json")
}

resource "aws_iam_policy" "policy_platform_ITOM_Discovery_Child_Policy" {
  name        = "ServiceNow_ITOM_Discovery_Child_Policy"
  path        = "/"

  policy = file("IAM/Policies/IAMP0007-PlatformSnowITOMDiscoveryChildPolicy/policy.json")
}

resource "aws_iam_policy" "IOT_Stackset_Execution_Child_Policy" {
  name        = "IOT_Stackset_Execution_Child_Policy"
  path        = "/"
  description = "platform IOT Stackset Execution Child Policy"

  policy = file("IAM/Policies/IAMP0008-PlatfromIOTStacksetExecutionChildPolicy/policy.json")
}

resource "aws_iam_policy" "platform_SnowOrganizationAccountAccessPolicy" {
  name        = "platform_SnowOrganizationAccountAccessPolicy"
  path        = "/"
  description = "platform_SnowOrganizationAccountAccessPolicy"

  policy = file("IAM/Policies/IAMP0009-PlatformSnowOrganizationAccountAccessPolicy/policy.json")
}

resource "aws_iam_policy" "platform_ListEC2ForFNMSPolicy" {
  name        = "platform_ListEC2ForFNMSPolicy${local.AccountType}"
  path        = "/"
  description = "platform_ListEC2ForFNMSPolicy${local.AccountType}"

  policy = file("IAM/Policies/IAMP0010-PlatformListEC2ForFNMSPolicy${local.AccountType}/policy.json")
}
