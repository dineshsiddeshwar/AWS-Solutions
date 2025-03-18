data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business_IRMPrivate" {
  name             = "business_IRMPrivate"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  description      = "IRM personnel with Read Only access to Security Hub"
  session_duration = "PT1H"
}

resource "aws_ssoadmin_permission_set_inline_policy" "business_IRMPrivate" {
  inline_policy      = file("${path.module}/policy.json")
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.business_IRMPrivate.arn
}