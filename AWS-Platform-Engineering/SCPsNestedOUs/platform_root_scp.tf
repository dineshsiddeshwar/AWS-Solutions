
#====================Root===================#

resource "aws_organizations_policy" "Root-Level-Restriction_1" {
  name = "platform_root_level_restriction_policy_1"
  description = "platform IAM restriction policy"
  content = file("SCPDefinitions/SCPD0001-RootLevelRestriction/scp_1.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Root-Level-Restriction_2" {
  name = "platform_root_level_restriction_policy_2"
  description = "This policy contains restrictions applied at the root level."
  content = file("SCPDefinitions/SCPD0001-RootLevelRestriction/scp_2.json")
  type = "SERVICE_CONTROL_POLICY"
}
