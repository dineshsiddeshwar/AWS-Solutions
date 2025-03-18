resource "aws_iam_policy" "policy_platform_audit_admin" {
  name        = "platform_audit_admin"
  path        = "/"
  description = "Policy for Lambda to perform actions in Audit Account"

  policy = file("${path.module}/Policies/IAMP0001-PlatformAuditAdminPolicy/policy.json")
}

resource "aws_iam_policy" "policy_platform_cloud_health_policy" {
  name        = "platform_cloud_health_policy"
  path        = "/"
  description = "Policy for creating a test database"

  policy = templatefile("${path.module}/Policies/IAMP0002-PlatformCloudHealthPolicy/policy.json",{ s3 = var.s3_bucket })
}

resource "aws_iam_policy" "policy_platform_ITOM_Discovery_Child_Policy" {
  name        = "ServiceNow_ITOM_Discovery_Child_Policy"
  path        = "/"

  policy = file("${path.module}/Policies/IAMP0003-PlatformSnowITOMDiscoveryChildPolicy/policy.json")
}




