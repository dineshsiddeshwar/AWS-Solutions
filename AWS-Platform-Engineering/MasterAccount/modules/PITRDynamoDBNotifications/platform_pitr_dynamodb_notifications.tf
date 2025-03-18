# PITR Change topic encryption key
resource "aws_kms_key" "pitr_change_topic_encryption_key" {
  description = "Key used to encrypt SNS PITR topic"
  is_enabled = true
  enable_key_rotation = true
}

# PITR Change topic encryption key policy
resource "aws_kms_key_policy" "pitr_change_topic_encryption_key_policy" {
  key_id = aws_kms_key.pitr_change_topic_encryption_key.id
  policy = data.aws_iam_policy_document.data_pitr_change_topic_encryption_key_policy.json
}

# PITR Change topic encryption key alias
resource "aws_kms_alias" "pitr_change_topic_encryption_key_alias" {
  name          = "alias/PITRChangeTopicEncryptionKey"
  target_key_id = aws_kms_key.pitr_change_topic_encryption_key.key_id
}

# PITR Change sns topic
resource "aws_sns_topic" "pitr_change_sns_topic" {
  kms_master_key_id = "alias/PITRChangeTopicEncryptionKey"
  name = var.pitr_change_sns_topic_name
}

# PITR Change sns topic subscription
resource "aws_sns_topic_subscription" "pitr_change_sns_topic_subscription_1" {
  topic_arn = aws_sns_topic.pitr_change_sns_topic.arn
  protocol  = "email"
  endpoint  = var.subscription_email_1
}

# # PITR Change sns topic subscription
# resource "aws_sns_topic_subscription" "pitr_change_sns_topic_subscription_2" {
#   topic_arn = aws_sns_topic.pitr_change_sns_topic.arn
#   protocol  = "email"
#   endpoint  = var.subscription_email_2
# }

# PITR Change sns topic subscription
resource "aws_sns_topic_subscription" "pitr_change_sns_topic_subscription_3" {
  topic_arn = aws_sns_topic.pitr_change_sns_topic.arn
  protocol  = "email"
  endpoint  = var.subscription_email_3
  count     = var.env_type == "prod" ? 1 : 0
}

# PITR Event rule
resource "aws_cloudwatch_event_rule" "dynamodb_pitr_event_rule" {
  name = var.dynamodb_pitr_event_rule_name
  description = "Event Rule to trigger for PITR change "
  is_enabled = true

  event_pattern = jsonencode({
    "source": ["aws.dynamodb"],
    detail-type = [
      "AWS API Call via CloudTrail"
    ],
    "detail": {
      "eventSource": ["dynamodb.amazonaws.com"],
      "eventName": ["UpdateContinuousBackups"],
      "requestParameters": {
        "tableName": ["Account_Details","CIS-Score-Report","DL_Details","github-tf-state-lock","Instance_PatchCompliance","	IPMGMTTable","	Network_Details_Table","Platform-MasterAccount-PimStack-*","platform_exception_ami_accounts"],
        "pointInTimeRecoverySpecification": {
          "pointInTimeRecoveryEnabled": [false]
        }
      }
    }
  })
}

# PITR Event rule target
resource "aws_cloudwatch_event_target" "dynamodb_pitr_event_target" {
  rule      = aws_cloudwatch_event_rule.dynamodb_pitr_event_rule.name
  target_id = "TargetTopicV1"
  arn       = aws_sns_topic.pitr_change_sns_topic.arn
  input_transformer {
    input_paths = {
      principal = "$.detail.userIdentity.principalId",
      role   = "$.detail.userIdentity.sessionContext.sessionIssuer.userName",
      table_name = "$.detail.requestParameters.tableName"
    }
    input_template = "\"Principal \u003cprincipal\u003e used role \u003crole\u003e to change DynamoDB table \u003ctable_name\u003e PITR status to False\"    \n"
  }
}

