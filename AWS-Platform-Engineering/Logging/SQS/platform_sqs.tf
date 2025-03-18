resource "aws_sqs_queue" "ConfigCloudtrailQueue" {
  name                      = "platform-da2-central-config-cloudtrail-${var.env_type}-queue"
  message_retention_seconds = 1209600
  visibility_timeout_seconds = 900

  tags = {
    platform_donotdelete = "yes"
  }
}

data "aws_iam_policy_document" "ConfigCloudtrailPolicy" {
  version = "2008-10-17"
  policy_id = "ConfigCloudtrailQueuePolicy"
  statement {
    sid    = "ConfigCloudtrailBucketToSendEvents"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }

    actions   = ["sqs:SendMessage","sqs:AddPermission"]
    resources = [aws_sqs_queue.ConfigCloudtrailQueue.arn]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values = ["arn:aws:s3:::aws-controltower-logs-${var.account_id}-us-east-1"]
    }
  }
}
resource "aws_sqs_queue_policy" "ConfigCloudtrailQueuePolicy" {
  queue_url = aws_sqs_queue.ConfigCloudtrailQueue.id
  policy    = data.aws_iam_policy_document.ConfigCloudtrailPolicy.json
}

resource "aws_sqs_queue" "CloudtrailQueue" {
  name                      = "platform-da2-central-cloudtrail-${var.env_type}-queue"
  message_retention_seconds = 1209600
  visibility_timeout_seconds = 120

  tags = {
    platform_donotdelete = "yes"
  }
}

data "aws_iam_policy_document" "CloudtrailPolicy" {
  version = "2008-10-17"
  policy_id = "CloudtrailQueuePolicy"
  statement {
    sid    = "CloudtrailBucketToSendEvents"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }

    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.CloudtrailQueue.arn]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values = ["arn:aws:s3:::platform-da2-central-cloudtrail-${var.env_type}"]
    }
  }
}
resource "aws_sqs_queue_policy" "CloudtrailQueuePolicy" {
  queue_url  = aws_sqs_queue.CloudtrailQueue.id
  policy    = data.aws_iam_policy_document.CloudtrailPolicy.json
}


resource "aws_sqs_queue" "ConfigQueue" {
  name                      = "platform-da2-central-config-${var.env_type}-queue"
  message_retention_seconds = 1209600
  visibility_timeout_seconds = 900

  tags = {
    platform_donotdelete = "yes"
  }
}

data "aws_iam_policy_document" "ConfigPolicy" {
  version = "2008-10-17"
  policy_id = "ConfigQueuePolicy"
  statement {
    sid    = "ConfigBucketToSendEvents"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }

    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.ConfigQueue.arn]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values = ["arn:aws:s3:::platform-da2-central-config-${var.env_type}"]
    }
  }
}
resource "aws_sqs_queue_policy" "ConfigQueuePolicy" {
  queue_url  = aws_sqs_queue.ConfigQueue.id
  policy    = data.aws_iam_policy_document.ConfigPolicy.json
}

resource "aws_sqs_queue" "SecurityHubQueue" {
  name                      = "platform-da2-central-securityhub-${var.env_type}-queue"
  message_retention_seconds = 1209600
  visibility_timeout_seconds = 900

  tags = {
    platform_donotdelete = "yes"
  }
}

data "aws_iam_policy_document" "SecurityHubPolicy" {
  version = "2008-10-17"
  policy_id = "SecurityHubQueuePolicy"
  statement {
    sid    = "SecurityHubBucketToSendEvents"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }

    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.SecurityHubQueue.arn]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values = ["arn:aws:s3:::platform-da2-central-securityhub-${var.env_type}"]
    }
  }
}
resource "aws_sqs_queue_policy" "SecurityHubQueuePolicy" {
  queue_url  = aws_sqs_queue.SecurityHubQueue.id
  policy    = data.aws_iam_policy_document.SecurityHubPolicy.json
}

resource "aws_sqs_queue" "VPCFlowLogsQueue" {
  name                      = "platform-da2-central-vpcflowlogs-${var.env_type}-queue"
  message_retention_seconds = 1209600
  visibility_timeout_seconds = 900

  tags = {
    platform_donotdelete = "yes"
  }
}

data "aws_iam_policy_document" "VPCFlowLogsPolicy" {
  version = "2008-10-17"
  policy_id = "VPCFlowLogsQueuePolicy"
  statement {
    sid    = "VPCFlowlogsBucketToSendEvents"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }

    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.VPCFlowLogsQueue.arn]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values = ["arn:aws:s3:::platform-da2-central-vpcflowlogs-${var.env_type}"]
    }
  }
}
resource "aws_sqs_queue_policy" "VPCFlowLogsQueuePolicy" {
  queue_url  = aws_sqs_queue.VPCFlowLogsQueue.id
  policy    = data.aws_iam_policy_document.VPCFlowLogsPolicy.json
}