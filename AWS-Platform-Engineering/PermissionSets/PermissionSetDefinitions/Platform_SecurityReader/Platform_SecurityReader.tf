data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "Platform_SecurityReader" {
  name             = "Platform_SecurityReader"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  session_duration = "PT1H"
  description      = "permission set for platform readonly"
  tags = {
    "platform_donotdelete" = "yes"
  }
}


resource "aws_ssoadmin_managed_policy_attachment" "Platform_SecurityReader1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.Platform_SecurityReader.arn
}