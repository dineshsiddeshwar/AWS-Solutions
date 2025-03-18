variable "RegionIpDictionary" {}

variable "env_type" {
  type = string
  description = "VPC env type"
}

variable "Connectivity" {
  type = string
  description = "VPC Connectivity type"
}


variable "extension_index" {
  type = string
  description = "VPC extension_index"
}

variable "IsNonRoutable" {
  type = string
  description = "Is Non Routable Requested"
}

variable "SSMParameters" {
  type = map(string)
  description = "SSM Parameters dictionary"
}