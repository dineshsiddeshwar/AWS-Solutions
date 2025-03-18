variable "cis_securityhub_controls" {
  type        = list(string)
  description = "Cis Aws SecurityHub Controls"
}

variable "aws_securityhub_controls" {
  type        = list(string)
  description = "Aws SecurityHub Controls"
}

variable aws_region {
    type = string
    description = "aws region"
}

variable current_account_number {
    type = string
    description = "child account number"
}
