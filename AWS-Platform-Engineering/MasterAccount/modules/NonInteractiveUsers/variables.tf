variable "api_stage" {
  type    = string
}

variable "NonInteractiveUser_Lambda_ApiAuth_permission_statement_id" {
  type    = string
}

variable "NonInteractiveUser_Lambda_Invoker_permission_statement_id" {
  type    = string
}

variable "NonInteractiveUser_Lambda_Receiver_permission_statement_id" {
  type    = string
}

variable "cloudwatch_event_target_id" {
 type    = string 
}

variable "master_admin_role_arn" {
  type    = string
  default = "platform admin role arn"
}