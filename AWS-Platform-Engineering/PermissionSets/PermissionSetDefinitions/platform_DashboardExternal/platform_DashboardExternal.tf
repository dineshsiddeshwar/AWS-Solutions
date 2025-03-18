data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "platform_DashboardExternal" {
  name             = "platform_DashboardExternal"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  description      = "Permission set for dashboard read-only access in Public"
  session_duration = "PT1H"
}

resource "aws_ssoadmin_managed_policy_attachment" "platform_DashboardExternal" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_DashboardExternal.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "platform_DashboardExternal1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSecurityHubReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.platform_DashboardExternal.arn
}

data "aws_iam_policy_document" "platform_DashboardExternal" {
  statement {
    sid    = "VisualEditor0"
    effect = "Deny"
    actions = [
      "ce:DescribeCostCategoryDefinition",
      "ce:GetRightsizingRecommendation",
      "ce:GetCostAndUsage",
      "ce:GetSavingsPlansUtilization",
      "ce:GetReservationPurchaseRecommendation",
      "ce:ListCostCategoryDefinitions",
      "ce:GetCostForecast",
      "ce:GetReservationUtilization",
      "ce:GetSavingsPlansPurchaseRecommendation",
      "ce:GetDimensionValues",
      "ce:GetSavingsPlansUtilizationDetails",
      "ce:GetCostAndUsageWithResources",
      "ce:GetReservationCoverage",
      "ce:GetSavingsPlansCoverage",
      "ce:GetTags",
      "ce:GetUsageForecast",
      "cur:DescribeReportDefinitions",
      "aws-portal:ViewPaymentMethods",
      "aws-portal:ViewAccount",
      "account:GetAlternateContact",
      "account:GetChallengeQuestions",
      "account:GetContactInformation",
      "payments:ListPaymentPreferences",
      "aws-portal:ViewBilling",
      "account:GetAccountInformation",
      "billing:Get*",
      "billing:List*",
      "ce:Describe*",
      "ce:Get*",
      "consolidatedbilling:GetAccountBillingRole",
      "consolidatedbilling:ListLinkedAccounts",
      "cur:Get*",
      "cur:ValidateReportDestination",
      "freetier:Get*",
      "invoicing:Get*",
      "invoicing:ListInvoiceSummaries",
      "payments:Get*",
      "payments:ListPaymentPreferences",
      "tax:GetTaxInheritance",
      "tax:GetTaxRegistrationDocument",
      "tax:ListTaxRegistrations",
      "aws-portal:ViewUsage",
      "cur:GetUsageReport"
    ]
    resources = ["*"]

  }
}

resource "aws_ssoadmin_permission_set_inline_policy" "platform_DashboardExternal" {
  inline_policy      = file("${path.module}/policy.json")
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.platform_DashboardExternal.arn
}