resource "aws_iam_policy" "policy_platform_log_admin" {
  name        = "platform_log_admin"
  path        = "/"
  description = "Policy for Lambda to perform actions in Logging Account"

  policy = file("${path.module}/Policies/IAMP0001-PlatformLogAdmin/policy.json")
}

resource "aws_iam_policy" "policy_platform_splunk" {
  name        = "platform_splunk"
  path        = "/"
  description = "Policy for Splunk to perform actions in Logging Account"

  policy = file("${path.module}/Policies/IAMP0002-PlatformSplunk/policy.json")
}

resource "aws_iam_policy" "policy_platform_cloud_health_policy" {
  name        = "platform_cloud_health_policy"
  path        = "/"
  description = "Policy for creating a test database"

  policy = templatefile("${path.module}/Policies/IAMP0003-PlatformCloudHealthPolicy/policy.json",{ s3 = var.s3_bucket })
}


resource "aws_iam_policy" "policy_platform_ITOM_Discovery_Child_Policy" {
  name        = "ServiceNow_ITOM_Discovery_Child_Policy"
  path        = "/"
  #description = "ServiceNow ITOM Discovery Child_Policy"

  policy = file("${path.module}/Policies/IAMP0004-PlatformSnowITOMDiscoveryChildPolicy/policy.json")
}