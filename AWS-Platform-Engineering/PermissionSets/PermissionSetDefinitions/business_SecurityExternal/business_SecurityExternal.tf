data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business_SecurityExternal" {
  name             = "business_SecurityExternal"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  description = "Security personnel with specific access to EC2 . To be assigned to security personnel in case of a security incident"
  session_duration= "PT1H"
}

resource "aws_ssoadmin_permission_set_inline_policy" "business_SecurityExternal" {
  inline_policy      = file("${path.module}/policy.json")
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.business_SecurityExternal.arn
}