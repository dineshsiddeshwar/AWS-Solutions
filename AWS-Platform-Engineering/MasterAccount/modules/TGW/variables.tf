variable "env_type" {
  type = string
  description = "Enter environment type"
}

variable "tgw_vpc_cidr" {
  type = string
  description = "Enter tgw vpc cidr range"
}

variable "tgw_id" {
  type = string
  description = "Enter tgw id"
}

variable "tgw_pvt_sub_cidr_1" {
  type = string
  description = "Enter tgw pvt subnet cidr range"
}

variable "tgw_pvt_sub_cidr_2" {
  type = string
  description = "Enter tgw pvt subnet cidr range"
}

variable "tgw_pub_sub_cidr_1" {
  type = string
  description = "Enter tgw pub subnet cidr range"
}

variable "tgw_pub_sub_cidr_2" {
  type = string
  description = "Enter tgw pub subnet cidr range"
}

variable "tgw_table" {
  type = string
  description = "tgw table name"
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