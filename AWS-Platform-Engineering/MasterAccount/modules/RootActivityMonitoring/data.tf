data "aws_iam_policy_document" "hub_root_activity_event_bus_policy" {
  statement {
    sid    = "OrganizationAccess"
    actions = [
      "events:PutEvents",
    ]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    resources = ["arn:aws:events:us-east-1:${var.master_account}:event-bus/platform-hub-root-activity"]
  }
}

data "archive_file" "root_activity_notification_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_root_activity_monitor.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_root_activity_monitor.zip"
}
