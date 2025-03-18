variable "vpc_id" {
  description = "VPC ID for the NLB"
  type        = string
}

variable "tags" {
  description = "Tags to apply to the Target Group"
  type        = map(string)
}