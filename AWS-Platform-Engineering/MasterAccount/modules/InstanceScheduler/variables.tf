variable instancescheduler_template_version {
    type = string
    description = "example v1.0"
}

variable "role_arn" {
  type    = string
  default = "platform admin role arn"
}

variable "requests_layer" {
  type    = string
  default = "requests layer"
}