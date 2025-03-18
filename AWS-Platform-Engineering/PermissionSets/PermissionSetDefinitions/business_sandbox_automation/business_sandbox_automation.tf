data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business_sandbox_automation" {
  name             = "business_sandbox_automation"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  description = "Provisioned for users in AWS-TST-PUB-411520-ITY-Sandbox-Automation"
  session_duration= "PT1H"
}

resource "aws_ssoadmin_permission_set_inline_policy" "business_sandbox_automation" {
  inline_policy      = file("${path.module}/policy.json")
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.business_sandbox_automation.arn
}