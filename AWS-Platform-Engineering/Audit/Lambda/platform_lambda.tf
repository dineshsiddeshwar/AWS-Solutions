data "aws_iam_role" "platform_audit_admin_role"{
    name = "Platform_AuditAdmin"
}


data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/platform_sechub_findings_s3.py"
  output_path = "${path.module}/lambda_function_payload.zip"
}



resource "aws_lambda_function" "platform_sechub_findings_s3" {
  filename      = data.archive_file.lambda.output_path
  function_name = "platform_sechub_findings_s3"
  description = "Lambda function to collect Security Hub Findings as JSON Files and put it in the S3 Bucket of Logging Account."
  role          = data.aws_iam_role.platform_audit_admin_role.arn
  handler       = "platform_sechub_findings_s3.lambda_handler"
  memory_size = 256
  source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime = "python3.8"

  timeout = 900

  environment {
    variables = {
      setup_env = var.env_type
    }
  }

  tags = {
    "platform_donotdelete" = "yes"
  }
}


resource "aws_sqs_queue" "SecHubFindingstoS3Queue" {
  name                      = "platform-da2-securityhub-s3-${var.env_type}-queue"
  message_retention_seconds = 1209600
  visibility_timeout_seconds = 900

  tags = {
    platform_donotdelete = "yes"
  }
}

data "aws_iam_policy_document" "SecHubFindingstoS3Policy" {
  version = "2008-10-17"
  policy_id = "SecHubFindingstoS3QueuePolicy"
  statement {
    sid    = "SecHubFindingsS3EventRuletoSendEvents"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }

    actions   = ["sqs:SendMessage","sqs:AddPermission"]
    resources = [aws_sqs_queue.SecHubFindingstoS3Queue.arn]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_cloudwatch_event_rule.SecHubFindingsS3EventRule.arn]
    }
  }
}
resource "aws_sqs_queue_policy" "SecHubFindingstoS3Policy" {
  queue_url = aws_sqs_queue.SecHubFindingstoS3Queue.id
  policy    = data.aws_iam_policy_document.SecHubFindingstoS3Policy.json
}

resource "aws_cloudwatch_event_rule" "SecHubFindingsS3EventRule" {
  name        = "Platform-AuditAccount-SecHubFindingsS3EventRule-${var.rule_id[var.region]}"
  description = "CloudWatch Events rule for Security Hub Findings to trigger a SQS which inturn invoke a Lambda will collect it and put it as JSON files into S3 Bucket of Logging Account."

  event_pattern = jsonencode({
    source = ["aws.securityhub"]
  })
}

resource "aws_cloudwatch_event_target" "SecHubFindingsS3EventRule" {
  rule      = aws_cloudwatch_event_rule.SecHubFindingsS3EventRule.name
  target_id = "TargetFunction"
  arn       = aws_sqs_queue.SecHubFindingstoS3Queue.arn
}

resource "aws_lambda_event_source_mapping" "SecHubFindingsS3LambdaEventSourcing" {
  batch_size = 5
  event_source_arn = aws_sqs_queue.SecHubFindingstoS3Queue.arn
  function_name    = aws_lambda_function.platform_sechub_findings_s3.arn
}

# IAM.9 handling lambda

data "aws_iam_role" "SecHubIAM9HandlingLambdaRole"{
    name = "platform_SecHubIAM9HandlingLambdaRole"
}

data "archive_file" "sechubiamlambda" {
  type        = "zip"
  source_file = "${path.module}/platform_sechub_iam9_handling_lambda_function.py"
  output_path = "${path.module}/platform_sechubiam_lambda_function_payload.zip"
}

resource "aws_lambda_function" "SecHubIAM9HandlingLambdaFunction" {
  count = var.sechublambda
  filename      = data.archive_file.sechubiamlambda.output_path
  function_name = "platform_sechub_iam9_handling_lambda_function"
  description = "Lambda function to handle IAM.9 control in Security Hub"
  role          = data.aws_iam_role.SecHubIAM9HandlingLambdaRole.arn
  handler       = "platform_sechub_iam9_handling_lambda_function.lambda_handler"
  #memory_size = 256
  source_code_hash = data.archive_file.sechubiamlambda.output_base64sha256

  runtime = "python3.11"

  timeout = 300

}
