variable "SSMParameters" {
  type = map(string)
  description = "SSM Parameters dictionary"
}

variable "ProvisionedProduct" {
  type = map(string)
  description = "Provisioned Product"
}

variable "RequestEventData" {
  type = map(string)
  description = "Request Event Data"
}

variable "Connectivity" {
  type = string
  description = "Account connectivity"
}