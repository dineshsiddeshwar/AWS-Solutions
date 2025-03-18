data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business_ReadOnlyExternal" {
  name             = "business_ReadOnlyExternal"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  description = "Read Only access for the business users"
  session_duration= "PT1H"
}


resource "aws_ssoadmin_managed_policy_attachment" "business_ReadOnlyExternal" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSupportAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_ReadOnlyExternal.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "business_ReadOnlyExternal1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_ReadOnlyExternal.arn
}