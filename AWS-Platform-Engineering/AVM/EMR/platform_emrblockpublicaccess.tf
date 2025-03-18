resource "aws_emr_block_public_access_configuration" "platform_security_emr_block_public" {
  count               = length(var.SSMParameters) == 0 ? 0 : 1

  block_public_security_group_rules = true

}