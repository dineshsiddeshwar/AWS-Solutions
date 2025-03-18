variable "managed_policy_arns" {
  description = "Existing Managed Policy Arns attached with the role"
  type        = list(string)
}

variable "tags" {
  description = "Tags to apply to the IAM role"
  type        = map(string)
}
