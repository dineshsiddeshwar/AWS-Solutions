# platform admin role 
output "platform_admin_role_arn" {
  value = module.iam_master_account.platform_admin_role_arn
}