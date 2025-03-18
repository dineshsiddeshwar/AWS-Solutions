variable trb_env_type {
    type = string
    description = "environment type dev/acceptance/prod"
} 


variable "role_arn" {
  type    = string
  default = "platform admin role arn"
}

variable master_account {
    type = string
    description = "master account"
}