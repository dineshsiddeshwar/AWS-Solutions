variable "NIC_id" {
  type = string
}

variable "NSG_id" {
  type = string
}

variable "VM_details" {
  type = map
}

variable "os_disk" {
  type = map
}

variable "source_image_reference" {
  type = map
}

variable "public_ip_address" {
    type = string
}

variable "network_interface_ids" {
    type = list
}

variable "nic" {
  type = map
}

variable "NSG_name" {
    type = string
}

variable "role_name" {
  type = string
}

variable "identity" {
  type = map
}

variable "policy" {
  type = map
}

variable "tags" {
  type = map
}



