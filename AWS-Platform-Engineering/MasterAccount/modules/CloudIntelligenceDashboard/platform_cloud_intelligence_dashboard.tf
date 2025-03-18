# Cloud Intelligence Dashboard Stack
resource "aws_cloudformation_stack" "cloud_intelligence_dashboard_stack" {
  name = var.cid_stack_name
  capabilities = [
    "CAPABILITY_IAM",
    "CAPABILITY_NAMED_IAM"
  ]
  iam_role_arn = var.master_admin_role_arn
  parameters = {
    QuickSightUser = var.CIDashboardQuickSightUserName
    DeployTAODashboard = "yes"
    PrerequisitesQuickSight = "yes"
    PrerequisitesQuickSightPermissions = "yes"
    OptimizationDataCollectionBucket = "trusted-advisor-org-reports-${var.master_account}"
    OptimizationDataCollectionBucketPath = "s3://trusted-advisor-org-reports-${var.master_account}"
  }

  template_url = "https://s3.amazonaws.com/${var.release_bucket_name}/TFC-Master/10/CloudFormationTemplates/CloudIntelligenceDashboards.yaml"
}