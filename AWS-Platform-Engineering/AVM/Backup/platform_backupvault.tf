data "aws_region" "current" {}

locals {
    snstopicarn = "arn:aws:sns:${data.aws_region.current.name}:${var.child_accountnumber}:platform_back_up_topic"
}

resource "aws_backup_vault" "create_backupvault_in_child_account" {
  count               = length(var.SSMParameters) == 0 ? 0 : 1

  name       = "platform_backupvault"
  tags = {
    platform_donotdelete = "yes"
  }
}

resource "aws_sns_topic" "create_back_up_topic" {
  count               = length(var.SSMParameters) == 0 ? 0 : 1

  name = "platform_back_up_topic"
  kms_master_key_id = "alias/aws/sns"
  policy = <<EOF
    {
      "Version": "2008-10-17",
      "Id": "__default_policy_ID",
      "Statement": [
        {
          "Sid": "__default_statement_ID",
          "Effect": "Allow",
          "Principal": {
            "AWS": "*"
          },
          "Action": [
            "SNS:GetTopicAttributes",
            "SNS:SetTopicAttributes",
            "SNS:AddPermission",
            "SNS:RemovePermission",
            "SNS:DeleteTopic",
            "SNS:Subscribe",
            "SNS:ListSubscriptionsByTopic",
            "SNS:Publish",
            "SNS:Receive"
          ],
          "Resource": "${local.snstopicarn}",
          "Condition": {
            "StringEquals": {
              "AWS:SourceOwner": "${var.child_accountnumber}"
            }
          }
        },
        {
          "Sid": "__console_pub_0",
          "Effect": "Allow",
          "Principal": {
            "Service": "backup.amazonaws.com"
          },
          "Action": "SNS:Publish",
          "Resource": "${local.snstopicarn}"
        }
      ]
    }
  EOF   
}

resource "aws_sns_topic_subscription" "create_back_up_topic_subscription" {
  count               = length(var.SSMParameters) == 0 ? 0 : 1

  topic_arn = aws_sns_topic.create_back_up_topic[0].arn
  protocol  = "email"
  endpoint  = var.dloftheAccount
}

resource "aws_backup_vault_notifications" "Create_backup_vault_notifications" {
  count               = length(var.SSMParameters) == 0 ? 0 : 1
  
  backup_vault_name   = "platform_backupvault"
  sns_topic_arn       = aws_sns_topic.create_back_up_topic[0].arn
  backup_vault_events = ["BACKUP_JOB_FAILED"]
}