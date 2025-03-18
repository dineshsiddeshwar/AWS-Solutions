data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "platform_IRM" {
  name             = "platform_IRM"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  description = "Provide access to core AWS platform services and resources not users and group management"
  session_duration= "PT2H"
}

resource "aws_ssoadmin_managed_policy_attachment" "platform_IRM" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSupportAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_IRM.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "platform_IRM1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/PowerUserAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_IRM.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "platform_IRM2" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_IRM.arn
}