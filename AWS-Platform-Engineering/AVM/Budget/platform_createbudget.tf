locals {
  time_start = "${formatdate("YYYY-MM-DD_hh:mm", timestamp())}"
}
resource "aws_budgets_budget" "Monthly_Budget_Limit" {
  name              = "Monthly Budget Limit"
  budget_type       = "COST"
  limit_amount      = var.budget_value
  limit_unit        = "USD"
  time_period_end   = "2040-01-01_00:00"
  time_period_start = local.time_start
  time_unit         = "MONTHLY"

  cost_types {
    include_credit             = true
    include_discount           = false
    include_other_subscription = true
    include_recurring          = true
    include_refund             = true
    include_subscription       = true
    include_support            = true
    include_tax                = true
    include_upfront            = true
    use_blended                = true
    use_amortized              = false

  }
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 70
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.dlForNewAccount]
  }     
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 70
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.dlForNewAccount]
  }     
}