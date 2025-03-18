# platform admin role 
output "platform_admin_role_arn" {
  value = aws_iam_role.platform_admin_role.arn
}
