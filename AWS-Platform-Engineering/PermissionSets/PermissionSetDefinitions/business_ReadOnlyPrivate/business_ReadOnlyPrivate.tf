data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business_ReadOnlyPrivate" {
  name             = "business_ReadOnlyPrivate"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  description = "Read Only Access for the business users"
  session_duration= "PT1H"
}


resource "aws_ssoadmin_managed_policy_attachment" "business_ReadOnlyPrivate" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSupportAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_ReadOnlyPrivate.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "business_ReadOnlyPrivate1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_ReadOnlyPrivate.arn
}