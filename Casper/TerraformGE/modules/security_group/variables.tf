variable "vpc_id" {
  description = "VPC ID for the Security Group"
  type        = string
}

variable "tags" {
  description = "Tags to apply to all the Security Group"
  type        = map(string)
}
