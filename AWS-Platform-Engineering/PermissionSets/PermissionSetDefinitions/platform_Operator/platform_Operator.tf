data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "platform_Operator" {
  name             = "platform_Operator"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  session_duration = "PT1H"
  description      = "Privileged role for the platform operations team, with ability to create, update and delete accounts. Create SSO users and apply permission sets."
}


resource "aws_ssoadmin_managed_policy_attachment" "platform_Operator" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_Operator.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "platform_Operator1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_Operator.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "platform_Operator2" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSCloudTrail_FullAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_Operator.arn
}
resource "aws_ssoadmin_managed_policy_attachment" "platform_Operator3" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSLambda_FullAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_Operator.arn
}
resource "aws_ssoadmin_managed_policy_attachment" "platform_Operator4" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSecurityHubFullAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_Operator.arn
}
resource "aws_ssoadmin_managed_policy_attachment" "platform_Operator5" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSServiceCatalogAdminFullAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_Operator.arn
}
resource "aws_ssoadmin_managed_policy_attachment" "platform_Operator6" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSSOMasterAccountAdministrator"
  permission_set_arn = aws_ssoadmin_permission_set.platform_Operator.arn
}
resource "aws_ssoadmin_managed_policy_attachment" "platform_Operator7" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSStepFunctionsConsoleFullAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_Operator.arn
}
resource "aws_ssoadmin_managed_policy_attachment" "platform_Operator8" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSupportAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_Operator.arn
}
resource "aws_ssoadmin_managed_policy_attachment" "platform_Operator9" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_Operator.arn
}

data "aws_ssoadmin_permission_set" "platform_Operator" {
  instance_arn = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  name         = "platform_Operator"
}

data "aws_ssoadmin_permission_set" "platform_ContributorExternal" {
  instance_arn = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  name         = "platform_ContributorExternal"
}

data "aws_ssoadmin_permission_set" "platform_DashboardExternal" {
  instance_arn = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  name         = "platform_DashboardExternal"
}

data "aws_ssoadmin_permission_set" "platform_PIMCognitoAccess" {
  instance_arn = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  name         = "platform_PIMCognitoAccess"
}


resource "aws_ssoadmin_permission_set_inline_policy" "platform_Operator" {
  inline_policy      = templatefile("${path.module}/policy.json",{ audit_account_id = var.audit_account_id,payer_account_id=var.payer_account_id,log_archive_account_id=var.log_archive_account_id,shared_services_account_id=var.shared_services_account_id,platform_operator= var.platform_operator,platform_ContributorExternal=var.platform_ContributorExternal,platform_DashboardExternal=var.platform_DashboardExternal,platform_PIMCognitoAccess=var.platform_PIMCognitoAccess})
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.platform_Operator.arn
}