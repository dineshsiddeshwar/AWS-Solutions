variable "ipaws_vpc_cidr" {
  type = string
  description = "IPAWS VPC cidr range"
}

variable "ipaws_pvt_subnet_cidr_1" {
  type = string
  description = "IPAWS Private subnet 1 CIDR range"
}

variable "ipaws_pvt_subnet_cidr_2" {
  type = string
  description = "IPAWS Private subnet 2 CIDR range"
}

variable "ipaws_pub_subnet_cidr_1" {
  type = string
  description = "IPAWS Public subnet 1 CIDR range"
}

variable "ipaws_pub_subnet_cidr_2" {
  type = string
  description = "IPAWS Public subnet 2 CIDR range"
}

variable "env_type" {
  type = string
  description = "Enter environment type"
}

variable "role_arn" {
  type    = string
  default = "platform admin role arn"
}

variable "requests_layer" {
  type    = string
  default = "requests layer"
}

variable "cryptography_layer" {
  type    = string
  default = "cryptography layer"
}

variable "msal_layer" {
  type    = string
  default = "msal layer"
}

variable "pyjwt_layer" {
  type    = string
  default = "pyjwt layer"
}

variable "cffi_layer" {
  type    = string
  default = "cffi layer"
}

