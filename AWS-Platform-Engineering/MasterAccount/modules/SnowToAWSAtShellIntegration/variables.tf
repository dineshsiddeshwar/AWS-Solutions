variable env_type {
    type = string
    description = "environment name"
}

variable "role_arn" {
  type    = string
  default = "platform admin role arn"
}

variable master_account {
    type = string
    description = "master account"
}

variable vpc_flow_bucket_env_type {
    type = string
    description = "dev, acceptance, prod"
}
