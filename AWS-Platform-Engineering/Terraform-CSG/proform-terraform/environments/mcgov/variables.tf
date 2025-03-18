variable "tags" {
  default = {
    Org         = "CSG",
    Business    = "ProductsAndSolutions",
    Portfolio   = "ProForm-Internal",
    Domain      = "Talent Acquisition",
    Environment = "mcqa",
    CostCenter  = "TBD",
    Terraform   = "true"
  }
}

variable "env" {
  type        = string
  description = "Short code for enviornment (dev, stg, prod); will be set by the GitHub Workflow"
  default     = "mcqa"
}

variable "region" {
  type        = string
  description = "Short code for enviornment (dev, stg, prod); will be set by the GitHub Workflow"
  default     = "us-east-1"
}

variable "cidr_block" {
  type        = string
  description = "CIDR of the Vpc"
  default     = "172.17.0.0/16"
}
variable "public_subnet_cidr_block" {
  description = "list of public subnet cidr blocks"
  type        = list(any)
  default     = ["172.17.1.0/24", "172.17.2.0/24"]
}
variable "avaialabity_zones" {
  description = "list of avaialabity_zones "
  type        = list(any)
  default     = ["us-east-1a", "us-east-1b"]
}
variable "private_subnet_cidr_block" {
  description = "list of private subnet cidr blocks"
  type        = list(any)
  default     = ["172.17.3.0/24", "172.17.4.0/24"]
}