data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "Platform_SecurityIncident" {
  name             = "Platform_SecurityIncident"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  description = "High privileged access for platform SecurityIncident."
  session_duration= "PT1H"
}


resource "aws_ssoadmin_managed_policy_attachment" "Platform_SecurityIncident" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  permission_set_arn = aws_ssoadmin_permission_set.Platform_SecurityIncident.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "Platform_SecurityIncident1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSupportAccess"
  permission_set_arn = aws_ssoadmin_permission_set.Platform_SecurityIncident.arn
}
resource "aws_ssoadmin_permission_set_inline_policy" "Platform_SecurityIncident" {
  inline_policy      = file("${path.module}/policy.json")
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.Platform_SecurityIncident.arn
}