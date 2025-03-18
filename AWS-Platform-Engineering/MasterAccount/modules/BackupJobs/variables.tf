variable "backup_jobs_report_event_rule_name" {
  type    = string
  default = "backup jobs report event rule name"
}

variable "failed_backup_jobs_report_event_rule_name" {
  type    = string
  default = "failed backup jobs report event rule name"
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


