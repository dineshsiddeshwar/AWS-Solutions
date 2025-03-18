data "aws_region" "current" {}

locals {
    region = data.aws_region.current.name
}

# Compliance Logging Config Event Rule
resource "aws_cloudwatch_event_rule" "compliance_logging_config_schedule" {
  name        = "platform_compliance_logging_config_events"
  description = "Event rule to send Config Events to IRM IP Account Event Bus"
  event_pattern = jsonencode({
    "source": ["aws.config"],
  })
  is_enabled = true
}

# Compliance Logging Config Event target
resource "aws_cloudwatch_event_target" "compliance_logging_config_target" {
  rule      = aws_cloudwatch_event_rule.compliance_logging_config_schedule.name
  target_id = "IRMEventBus"
  arn       = "arn:aws:events:${local.region}:${var.irm_account_id}:event-bus/${var.irm_environment}"
  role_arn = "arn:aws:iam::${var.master_account}:role/platform_compliance_logging_role"
}

# Compliance Logging CloudTrail Event Rule
resource "aws_cloudwatch_event_rule" "compliance_logging_cloudtrail_schedule" {
  name        = "platform_compliance_logging_cloudtrail_events"
  description = "Event rule to send CloudTrail Events to IRM IP Account Event Bus"
  event_pattern = jsonencode({
    "source": [
      {
        "anything-but": [
          "aws.config", 
          "aws.securityhub"
        ]
      }
    ],
  })
  is_enabled = true
}

# Compliance Logging CloudTrail Event target
resource "aws_cloudwatch_event_target" "compliance_logging_cloudtrail_target" {
  rule      = aws_cloudwatch_event_rule.compliance_logging_cloudtrail_schedule.name
  target_id = "IRMEventBus"
  arn       = "arn:aws:events:${local.region}:${var.irm_account_id}:event-bus/${var.irm_environment}"
  role_arn = "arn:aws:iam::${var.master_account}:role/platform_compliance_logging_role"
}