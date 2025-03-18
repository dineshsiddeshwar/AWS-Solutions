variable RequestEventData { }

variable ProvisionedProduct { }

variable SSMParameters { }

variable cis_aws_securityhub_controls { }

variable "Env_type" {
  type = string
  description = "VPC env type"
}

variable "VPC_cidr_extend_number_US" {
  type = string
  description = "VPC extension track US"
}

variable "VPC_cidr_extend_number_EU" {
  type = string
  description = "VPC extension track EU"
}

variable "VPC_cidr_extend_number_SG" {
  type = string
  description = "VPC extension track SG"
}

variable RegionIpDictionary_US { }

variable RegionIpDictionary_EU { }

variable RegionIpDictionary_SG { }

variable "Non_routable_requested_US" {
  type = string
  description = "Non routable requested for US region VPC"
}

variable "Non_routable_requested_EU" {
  type = string
  description = "Non routable requested for SG region VPC"
}

variable "Non_routable_requested_SG" {
  type = string
  description = "Non routable requested for SG region VPC"
}
