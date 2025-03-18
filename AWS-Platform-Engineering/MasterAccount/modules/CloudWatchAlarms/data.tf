data "archive_file" "send_notification_lambda_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/PythonFunctionFiles/platform_send_alarm_notification.py"
  output_path = "${path.module}/PythonFunctionZippedFiles/platform_send_alarm_notification.zip"
}
