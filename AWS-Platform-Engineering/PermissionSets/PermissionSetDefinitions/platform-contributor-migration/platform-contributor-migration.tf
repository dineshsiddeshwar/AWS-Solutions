data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "platform-contributor-migration" {
  name             = "platform-contributor-migration"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  session_duration= "PT1H"
  description = "This permission would have restrictive permissions for migration team members"
}


resource "aws_ssoadmin_managed_policy_attachment" "platform-contributor-migration" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform-contributor-migration.arn
}
resource "aws_ssoadmin_managed_policy_attachment" "platform-contributor-migration1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSSOMasterAccountAdministrator"
  permission_set_arn = aws_ssoadmin_permission_set.platform-contributor-migration.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "platform-contributor-migration2" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform-contributor-migration.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "platform-contributor-migration3" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSOrganizationsFullAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform-contributor-migration.arn
}


resource "aws_ssoadmin_permission_set_inline_policy" "platform-contributor-migration" {
  inline_policy      = templatefile("${path.module}/policy.json",{ audit_account_id = var.audit_account_id,payer_account_id=var.payer_account_id,log_archive_account_id=var.log_archive_account_id,shared_services_account_id=var.shared_services_account_id,platform_operator= var.platform_operator,platform_ContributorExternal=var.platform_ContributorExternal,platform_DashboardExternal=var.platform_DashboardExternal,platform_PIMCognitoAccess=var.platform_PIMCognitoAccess,migration_ou_id=var.migration_ou_id,ou_id=var.ou_id})
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.platform-contributor-migration.arn
}

data "aws_iam_policy" "scp-edit-policy" {
  name = "scp-edit-policy"
} 

resource "aws_ssoadmin_customer_managed_policy_attachment" "platform-contributor-migration" {
  count = var.customer_managed_policy
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.platform-contributor-migration.arn
  customer_managed_policy_reference {
    name = data.aws_iam_policy.scp-edit-policy.name
  }
}