variable patching_template_version {
    type = string
    description = "example v1.0"
}

variable patching_report_sns_topic_name {
    type = string
    description = "patching report sns topic name"
}

variable platform_patch_report_monthly_event_rule_name {
    type = string
    description = "platform patch report monthly event rule name"
}

variable master_inventory_state_machine_event_rule_name {
    type = string
    description = "master inventory state machine event rule name"
}

variable account_details_event_rule_name {
    type = string
    description = "account details event rule name"
}

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

variable "role_arn" {
  type    = string
  default = "platform admin role arn"
}

variable master_account {
    type = string
    description = "master account"
}

variable org_id {
    type = string
    description = "organization id"
}

variable release_bucket_name {
    type = string
    description = "enter the release bucket name"
}

variable env_type {
    type = string
    description = "environment type dev/uat/prod"
}