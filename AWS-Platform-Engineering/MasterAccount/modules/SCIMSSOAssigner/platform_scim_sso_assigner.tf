# SCIM SSO Assigner lambda
resource "aws_lambda_function" "scim_sso_assigner_lambda" {
  filename      = "${path.module}/PythonFunctionZippedFiles/platform_SCIM_SSO_assigner.zip"
  function_name = "platform_SCIM_SSO_assigner"
  role          = var.role_arn
  handler       = "platform_SCIM_SSO_assigner.lambda_handler"
  source_code_hash = data.archive_file.scim_sso_assigner_lambda_zip.output_base64sha256

  runtime = "python3.8"
  memory_size = 10240
  timeout = 900
  layers = [var.requests_layer]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

# SCIM SSO Assigner lambda schedule
resource "aws_cloudwatch_event_rule" "scim_sso_assigner_schedule" {
  name        = "SCIMSSOEventSchedule"
  description = "Scheduled Rule for every 2nd hour"
  schedule_expression = "rate(30 minutes)"
  is_enabled = true
}

resource "aws_cloudwatch_event_target" "scim_sso_assigner_target" {
  rule      = aws_cloudwatch_event_rule.scim_sso_assigner_schedule.name
  target_id = "SCIMintegration"
  arn       = aws_lambda_function.scim_sso_assigner_lambda.arn
}

resource "aws_lambda_permission" "scim_sso_assigner_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scim_sso_assigner_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scim_sso_assigner_schedule.arn
}