data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business_Renewable_Energy" {
  name             = "business_Renewable_Energy"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  description = "This  assume role is for SRS migrated accounts"
  session_duration= "PT1H"
}

resource "aws_ssoadmin_permission_set_inline_policy" "business_Renewable_Energy" {
  inline_policy      = file("${path.module}/policy.json")
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.business_Renewable_Energy.arn
}