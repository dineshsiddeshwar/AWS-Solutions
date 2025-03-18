variable "subscription_email_1" {
  type    = string
  description  = "subscription email"
}

variable "subscription_email_2" {
  type    = string
  description  = "subscription email"
}

variable "subscription_email_3" {
  type    = string
  description  = "subscription email"
}

variable "dynamodb_pitr_event_rule_name" {
  type    = string
  description  = "enter rule name"
}

variable "pitr_change_sns_topic_name" {
  type    = string
  description  = "sns topic name"
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