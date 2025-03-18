variable env_type {
    type = string
    description = "environment type dev/uat/prod"
}

variable "role_arn" {
  type    = string
  default = "platform admin role arn"
}

variable "requests_layer" {
  type    = string
  default = "requests layer"
}

variable master_account {
    type = string
    description = "master account"
}

variable vpc_flow_bucket_env_type {
    type = string
    description = "dev, acceptance, prod"
}
variable master_admin_role_arn {
    type = string
    description = "master admin role arn"
}
