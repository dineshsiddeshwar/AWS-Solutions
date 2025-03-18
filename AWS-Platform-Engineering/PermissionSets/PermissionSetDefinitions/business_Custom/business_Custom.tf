data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business_Custom" {
  name             = "business_Custom"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  description      = "Allows to assume other IAM roles within the same account"
  session_duration = "PT1H"
}
resource "aws_ssoadmin_permission_set_inline_policy" "business_Custom" {
  inline_policy      = file("${path.module}/policy.json")
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.business_Custom.arn
}