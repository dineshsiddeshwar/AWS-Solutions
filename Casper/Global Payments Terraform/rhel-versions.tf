#rhel version
variable "rhel_8_sku" {
  type        = string
  description = "SKU for RHEL 8"
  default     = "rhel-cloud/rhel-8"
}

variable "linux_instance_type" {
  type        = string
  description = "VM instance type for Linux Server"
  default     = "f1-micro"
}