variable "subscription_email" {
  type    = string
  default = "GXSOMWIPROCLOUDAWSDA2-Operations@shell.com"
}

variable "cloudtrail_log_group_name" {
  type    = string
  default = "enter cloudtrail log group name"
}

variable "iam_change_sns_topic_name" {
  type    = string
  default = "iam change sns topic name"
}

variable "iam_changes_metric_filter_name" {
  type    = string
  description = "iam change metric filter name"
}

variable master_account {
    type = string
    description = "master account"
}

variable org_id {
    type = string
    description = "organization id"
}

variable env_type {
    type = string
    description = "environment type dev/uat/prod"
}
