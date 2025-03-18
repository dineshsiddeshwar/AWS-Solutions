resource "aws_ebs_encryption_by_default" "platform_security_enable_ebs_encryption" {
  count               = length(var.SSMParameters) == 0 ? 0 : 1
  
  enabled = true
}