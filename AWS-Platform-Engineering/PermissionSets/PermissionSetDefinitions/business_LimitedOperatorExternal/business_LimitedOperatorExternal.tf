data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business_LimitedOperatorExternal" {
  name             = "business_LimitedOperatorExternal"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  session_duration= "PT1H"
  description = "Ability to start and stop whitelisted services"
}


resource "aws_ssoadmin_managed_policy_attachment" "business_LimitedOperatorExternal" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSupportAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_LimitedOperatorExternal.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "business_LimitedOperatorExternal1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_LimitedOperatorExternal.arn
}


resource "aws_ssoadmin_permission_set_inline_policy" "business_LimitedOperatorExternal" {
  inline_policy      = file("${path.module}/policy.json")
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.business_LimitedOperatorExternal.arn
}