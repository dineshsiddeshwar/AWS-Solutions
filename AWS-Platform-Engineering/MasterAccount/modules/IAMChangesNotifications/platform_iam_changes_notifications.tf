# IAM Changes topic encryption key
resource "aws_kms_key" "iam_changes_topic_encryption_key" {
  description = "Key used to encrypt SNS IAM change topic"
  is_enabled = true
  enable_key_rotation = true
}

# IAM Changes topic encryption key policy
resource "aws_kms_key_policy" "iam_changes_topic_encryption_key_policy" {
  key_id = aws_kms_key.iam_changes_topic_encryption_key.id
  policy = data.aws_iam_policy_document.data_iam_changes_topic_encryption_key_policy.json
}

# IAM Changes topic encryption key alias
resource "aws_kms_alias" "iam_changes_topic_encryption_key_alias" {
  name          = "alias/IAMNotificationTopicEncryptionKey"
  target_key_id = aws_kms_key.iam_changes_topic_encryption_key.key_id
}

# IAM Changes sns topic
resource "aws_sns_topic" "iam_changes_sns_topic" {
  name = var.iam_change_sns_topic_name
  kms_master_key_id = "alias/IAMNotificationTopicEncryptionKey"
}

# IAM Changes sns topic subscription
resource "aws_sns_topic_subscription" "iam_changes_sns_topic_subscription" {
  topic_arn = aws_sns_topic.iam_changes_sns_topic.arn
  protocol  = "email"
  endpoint  = var.subscription_email
  count     = var.env_type == "prod" ? 0 : 0
}

# IAM Changes metric filter
resource "aws_cloudwatch_log_metric_filter" "iam_changes_metric_filter" {
  name           =  var.iam_changes_metric_filter_name
  pattern        = "{ ( ($.eventSource = \"iam.amazonaws.com\") && (($.eventName = \"AttachRolePolicy\") || ($.eventName = \"DetachRolePolicy\") || ($.eventName = \"CreateRole\") || ($.eventName = \"CreateServiceLinkedRole\") || ($.eventName = \"DeleteRole\") || ($.eventName = \"DeleteRolePermissionsBoundary\") || ($.eventName = \"DeleteRolePolicy\") || ($.eventName = \"DeleteServiceLinkedRole\") || ($.eventName = \"CreatePolicy\") || ($.eventName = \"CreatePolicyVersion\") || ($.eventName = \"DeleteGroupPolicy\") || ($.eventName = \"DeletePolicy\") || ($.eventName = \"DeletePolicyVersion\") || ($.eventName = \"DeleteRolePolicy\") || ($.eventName = \"DeleteUserPolicy\") || ($.eventName = \"DetachGroupPolicy\") || ($.eventName = \"DetachUserPolicy\") ) ) }"
  log_group_name = var.cloudtrail_log_group_name

  metric_transformation {
    name      = "IAMChanges"
    namespace = "LogMetrics"
    value     = "1"
  }
}

# IAM Changes metric alarm
resource "aws_cloudwatch_metric_alarm" "iam_changes_metric_alarm" {
  alarm_name                = "platform_IAM_Role_Policy_Change_Notification"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  metric_name               = "IAMChanges"
  namespace                 = "LogMetrics"
  period                    = 60
  statistic                 = "Sum"
  threshold                 = 1
  alarm_description         = "Alarm for IAM Roles and Policy changes"
  treat_missing_data        = "notBreaching"
  alarm_actions             = [aws_sns_topic.iam_changes_sns_topic.arn]
}