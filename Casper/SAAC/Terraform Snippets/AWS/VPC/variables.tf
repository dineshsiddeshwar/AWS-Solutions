variable "aws_region" {
  type=string
  description = "value"
}
variable "vpc_cidr_block" {
  type=string
  description = "value"
}
# variable "primary_vpc_sg_id" {
#   type=string
#   description = "value"
# }
variable "private_subnet1_az1_cidr" {
  type=string
  description = "value"
}
variable "private_subnet2_az1_cidr" {
  type=string
  description = "value"
}
# variable "availability_zones" {
#   type=set(string)
#   description = "value"
# }
variable "vpc_availability_zone_1" {
  type=string
  description = "value"
}
variable "iam_vpc_user" {
  type=string
  description = "value"
}
variable "vpc_flow_logs_cloudwatch" {
  type=string
  description = "value"
}
variable "retention_in_days" {
  type=number
  description = "value"
}
variable "kms_key_id" {
  type=string
  description = "value"
}
# variable "peer_vpc_id" {
#   type=string
#   description = "value"
# }
# variable "peer_vpc_region" {
#   type=string
#   description = "value"
# }
# variable "peer_vpc_timeout_create" {
#   type=string
#   description = "value"
# }
# variable "peer_vpc_timeout_delete" {
#   type=string
#   description = "value"
# }
# variable "peer_provider" {
#   type=string
#   description = "value"
# }
# variable "auto_accept_peering" {
#   type=string
#   description = "value"
# }
# variable "peer_cidr_block" {
#   type=string
#   description = "value"
# }
variable "vpc_endpoint_lb_arns" {
  type=set(string)
  description = "value"
}
variable "aws_vpc_endpoint_to_service_name" {
  type=string
  description = "value"
}
variable "vpc_endpoint_allowed_principals" {
  type=set(string)
  description = "value"
}
variable "aws_vpc_endpoint_sg_ids" {
  type=set(string)
  description = "value"
}
# variable "vpc_endpoint_svc_network_load_balancer_arns" {
#   type=set(string)
#   description = "value"
# }

data "template_file" "VpcUserPolicy" {
  template = file("policies/VpcUserPolicy.json")
}

data "template_file" "VpcFlowLogsCloudwatchRole" {
  template = file("policies/VpcFlowLogsCloudwatchRole.json")
}

data "template_file" "VpcFlowLogsCloudWatchPolicy" {
  template = file("policies/VpcFlowLogsCloudwatchPolicy.json")
}

variable "common_tags" {
  type        = map(string)
  description = "Default tags attached to all resources. | Example: { Name = \"vpc_endpoint\", ... }"
}
