variable "location" {
  type = string
  default = "eastus"
}

variable "prefix" {
  type = string
  default = "EYGDSSEC"
}

variable "standard_tags" {
  description = "Standard tags that sould be associated to every resource"
  type = map(string)
  default = {
    Application = "Baseline"
    BusinessUnit = "EYGDS-SEC"
  }
}
