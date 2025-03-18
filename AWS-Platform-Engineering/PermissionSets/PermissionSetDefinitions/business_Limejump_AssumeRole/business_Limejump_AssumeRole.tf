data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business_Limejump_AssumeRole" {
  name             = "business_Limejump_AssumeRole"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  session_duration= "PT1H"
  description = "business_Limejump_AssumeRole"
}

resource "aws_ssoadmin_permission_set_inline_policy" "business_Limejump_AssumeRole" {
  inline_policy      = file("${path.module}/policy.json")
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.business_Limejump_AssumeRole.arn
}