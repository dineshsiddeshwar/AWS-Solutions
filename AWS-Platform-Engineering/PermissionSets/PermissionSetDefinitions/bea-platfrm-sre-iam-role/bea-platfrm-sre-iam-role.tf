data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "bea-platfrm-sre-iam-role" {
  name             = "bea-platfrm-sre-iam-role"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  session_duration = "PT1H"
  description      = "Be.Agile Permission set for the platform"
  tags = {
    "platform_donotdelete" = "yes"
  }
}


resource "aws_ssoadmin_managed_policy_attachment" "bea-platfrm-sre-iam-role" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/PowerUserAccess"
  permission_set_arn = aws_ssoadmin_permission_set.bea-platfrm-sre-iam-role.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "bea-platfrm-sre-iam-role1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.bea-platfrm-sre-iam-role.arn
}

resource "aws_ssoadmin_permission_set_inline_policy" "bea-platfrm-sre-iam-role" {
  inline_policy      = file("${path.module}/policy.json")
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.bea-platfrm-sre-iam-role.arn
}