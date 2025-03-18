data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "platform_MasterContributorAccess" {
  name             = "platform_MasterContributorAccess"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  session_duration= "PT1H"
  description = "Permission set used by TEAM app to gain privileged access"
}


resource "aws_ssoadmin_managed_policy_attachment" "platform_MasterContributorAccess" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_MasterContributorAccess.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "platform_MasterContributorAccess1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSupportAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_MasterContributorAccess.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "platform_MasterContributorAccess2" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/job-function/Billing"
  permission_set_arn = aws_ssoadmin_permission_set.platform_MasterContributorAccess.arn
}
