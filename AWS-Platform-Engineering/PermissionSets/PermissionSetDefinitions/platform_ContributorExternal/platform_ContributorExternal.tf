data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "platform_ContributorExternal" {
  name             = "platform_ContributorExternal"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  description = "High privileged access for platform administrator."
  session_duration= "PT1H"
}


resource "aws_ssoadmin_managed_policy_attachment" "platform_ContributorExternal" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_ContributorExternal.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "platform_ContributorExternal1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSupportAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_ContributorExternal.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "platform_ContributorExternal2" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/job-function/Billing"
  permission_set_arn = aws_ssoadmin_permission_set.platform_ContributorExternal.arn
}

