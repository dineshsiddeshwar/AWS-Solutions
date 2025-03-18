data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business_IRMExternal" {
  name             = "business_IRMExternal"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  session_duration= "PT1H"
  description = "IRM personnel with Read Only access to Security Hub"
}


resource "aws_ssoadmin_managed_policy_attachment" "business_IRMExternal" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSecurityHubReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_IRMExternal.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "business_IRMExternal1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/PowerUserAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_IRMExternal.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "business_IRMExternal2" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_IRMExternal.arn
}