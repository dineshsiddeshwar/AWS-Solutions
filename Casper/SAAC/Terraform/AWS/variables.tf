variable "aws_region" {
  type        = string
  description = "Region running from"
}

variable "common_tags" {
  type        = map(string)
  description = "Default tags attached to all resources | Example: { Name = \"ses_system_1\", ... }"
}

variable "kms_deletion_window_in_days" {
  type = number
  description = "how long until key deleted"
}
