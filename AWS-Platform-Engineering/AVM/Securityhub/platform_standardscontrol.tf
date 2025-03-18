data "aws_region" "currentregion" {}

resource "aws_securityhub_standards_control" "cis_securityhub_controls" {
  for_each              = toset(var.cis_securityhub_controls)
  standards_control_arn = "arn:aws:securityhub:${data.aws_region.currentregion.name}:${var.current_account_number}:control/cis-aws-foundations-benchmark/v/1.2.0/${each.value}"
  control_status        = "DISABLED"
  disabled_reason       = "As part of security hub refinement"

}

resource "aws_securityhub_standards_control" "aws_securityhub_controls" {
  for_each              = toset(var.aws_securityhub_controls)
  standards_control_arn = "arn:aws:securityhub:${data.aws_region.currentregion.name}:${var.current_account_number}:control/aws-foundational-security-best-practices/v/1.0.0/${each.value}"
  control_status        = each.value == "SSM.1" ? "ENABLED" : "DISABLED"
  disabled_reason       = each.value == "SSM.1" ? "" : "As part of security hub refinement"

}
