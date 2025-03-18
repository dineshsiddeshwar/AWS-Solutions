data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "platform_PIMCognitoAccess" {
  name             = "platform_PIMCognitoAccess"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  description = "platform_PIMCognitoAccess"
  session_duration= "PT1H"
}


resource "aws_ssoadmin_managed_policy_attachment" "platform_PIMCognitoAccess" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AmazonCognitoPowerUser"
  permission_set_arn = aws_ssoadmin_permission_set.platform_PIMCognitoAccess.arn
}