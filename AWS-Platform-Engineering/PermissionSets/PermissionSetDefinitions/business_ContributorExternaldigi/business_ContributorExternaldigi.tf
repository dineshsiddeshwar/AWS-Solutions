data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business_ContributorExternaldigi" {
  name             = "business_ContributorExternaldigi"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  session_duration= "PT12H"
  description = "Custom permission set for account DIGI-AMERICAS to use sage maker"
}


resource "aws_ssoadmin_managed_policy_attachment" "business_ContributorExternaldigi" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_ContributorExternaldigi.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "business_ContributorExternaldigi1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSupportAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_ContributorExternaldigi.arn
}

resource "aws_ssoadmin_permission_set_inline_policy" "business_ContributorExternaldigi" {
  inline_policy      = file("${path.module}/policy.json")
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.business_ContributorExternaldigi.arn
}