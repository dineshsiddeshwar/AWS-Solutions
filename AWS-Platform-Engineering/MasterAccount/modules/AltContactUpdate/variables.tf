variable master_account {
    type = string
    description = "master account"
}

variable SecurityContactEmail {
    type = string
    description = "Security Contact Email"
}

variable SecurityContactName {
    type = string
    description = "Security Contact Name"
}

variable SecurityContactTitle {
    type = string
    description = "Security Contact Title"
}

variable SecurityContactPhone {
    type = string
    description = "Security Contact Phone"
}

variable OperationsContactEmail {
    type = string
    description = "Operations Contact Email"
}

variable OperationsContactName {
    type = string
    description = "Operations Contact Name"
}

variable OperationsContactTitle {
    type = string
    description = "Operations Contact Title"
}

variable OperationsContactPhone {
    type = string
    description = "Operations Contact Phone"
}

variable "role_arn" {
  type    = string
  default = "platform admin role arn"
}

variable "requests_layer" {
  type    = string
  default = "requests layer"
}