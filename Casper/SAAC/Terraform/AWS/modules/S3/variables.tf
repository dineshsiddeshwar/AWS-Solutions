variable "s3_bucket_name" {
  type = string
  description = "value"
}
variable "s3_bucket_object_lock_config_retention_mode" {
  type = string
  description = "value"
}
variable "s3_bucket_object_lock_config_retention_period" {
  type = number
  description = "value"
}
variable "s3_vpc_id" {
  type = string
  description = "value"
}
variable "s3_vpc_endpoint_type" {
  type = string
  description = "value"
}
variable "s3_vpc_sgs" {
  type = set(string)
  description = "value"
}

variable "s3_sse_key" {
  type = string
  description = "value"
}

variable "s3_region" {
  type = string
  description = "value"
}