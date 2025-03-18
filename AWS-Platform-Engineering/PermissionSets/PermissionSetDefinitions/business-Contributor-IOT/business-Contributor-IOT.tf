data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business-Contributor-IOT" {
  name             = "Bussiness-Contributor-IOT"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  description = "Contains more Restrictive policy including Business-Contributor-External"
  session_duration= "PT1H"
}

resource "aws_ssoadmin_managed_policy_attachment" "business-Contributor-IOT" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business-Contributor-IOT.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "business-Contributor-IOT1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business-Contributor-IOT.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "business-Contributor-IOT2" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/job-function/Billing"
  permission_set_arn = aws_ssoadmin_permission_set.business-Contributor-IOT.arn
}

resource "aws_ssoadmin_permission_set_inline_policy" "business-Contributor-IOT" {
  inline_policy      = file("${path.module}/policy.json")
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.business-Contributor-IOT.arn
}