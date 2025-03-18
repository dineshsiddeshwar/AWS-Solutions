data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business_ContributorExternal" {
  name             = "business_ContributorExternal"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  session_duration= "PT1H"
  description = "Privileged access for business account operators. Allows ability to create and modify resources but not delete or terminate"
}


resource "aws_ssoadmin_managed_policy_attachment" "business_ContributorExternal" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_ContributorExternal.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "business_ContributorExternal1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_ContributorExternal.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "business_ContributorExternal2" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSupportAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_ContributorExternal.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "business_ContributorExternal3" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/job-function/Billing"
  permission_set_arn = aws_ssoadmin_permission_set.business_ContributorExternal.arn
}

resource "aws_ssoadmin_permission_set_inline_policy" "business_ContributorExternal" {
  inline_policy      = file("${path.module}/policy.json")
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.business_ContributorExternal.arn
}