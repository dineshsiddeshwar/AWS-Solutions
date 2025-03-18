data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business_SecurityPrivate" {
  name             = "business_SecurityPrivate"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  description = "Security personnel with specific access to specific service"
  session_duration= "PT1H"
}
resource "aws_ssoadmin_permission_set_inline_policy" "business_SecurityPrivate" {
  inline_policy      = file("${path.module}/policy.json")
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.business_SecurityPrivate.arn
}