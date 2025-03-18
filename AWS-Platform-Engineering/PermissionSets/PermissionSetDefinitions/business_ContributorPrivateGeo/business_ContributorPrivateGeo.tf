data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business_ContributorPrivateGeo" {
  name             = "business_ContributorPrivateGeo"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  description      = "High Level access for Administrator with additional GetIDOpenConnector related values"
  session_duration = "PT1H"
}

resource "aws_ssoadmin_managed_policy_attachment" "business_ContributorPrivateGeo" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_ContributorPrivateGeo.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "business_ContributorPrivateGeo1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSupportAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_ContributorPrivateGeo.arn
}
