variable env_type {
    type = string
    description = "environment name"
}

variable vpc_flow_bucket_env_type {
    type = string
    description = "dev, acceptance, prod"
}

variable cis_pro_tools {
    type = string
    description = "cis pro tools"
}

variable cis_ami_reports {
    type = string
    description = "cis ami reports"
}

variable "role_arn" {
  type    = string
  default = "platform admin role arn"
}

variable master_account {
    type = string
    description = "master account"
}