#========================Layer-1====================#

resource "aws_organizations_policy" "Exceptions-Tagging-Restriction" {
  name = "platform_nested_ou_exceptions_tagging_restriction"
  description = "This SCP is for restrictions on Tagging. "
  content = file("SCPDefinitions/SCPD0059-ExceptionsTaggingRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

resource "aws_organizations_policy" "Exceptions-Region-Restriction" {
  name = "platform_nested_ou_exceptions_region_restriction"
  description = "This SCP is for restrictions on Region. "
  content = file("SCPDefinitions/SCPD0060-ExceptionsRegionRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}

# resource "aws_organizations_policy" "Exceptions-IAM-Restriction" {
#   name = "platform_nested_ou_exceptions_iam_restriction"
#   description = "This SCP is for restrictions on IAM. "
#   content = file("SCPDefinitions/SCPD0061-ExceptionsIAMRestriction/scp.json")
#   type = "SERVICE_CONTROL_POLICY"
# }

resource "aws_organizations_policy" "Exceptions-Management-Restriction" {
  name = "platform_nested_ou_exceptions_management_restriction"
  description = "This SCP is for restrictions by Platform Management. "
  content = file("SCPDefinitions/SCPD0062-ExceptionsManagementRestriction/scp.json")
  type = "SERVICE_CONTROL_POLICY"
}
