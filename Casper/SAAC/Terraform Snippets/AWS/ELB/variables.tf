data "aws_caller_identity" "current_caller_identity" {}

locals {
  account_id = data.aws_caller_identity.current_caller_identity.account_id
}

variable "aws_region" {
  description = "Aws region where resource needs to be deployed | Example : \"us-west-2\""
  type        = string

}

# KMS keys
data "aws_kms_alias" "cg_cmk_key_alias" {
  name = var.alb_cg_cmk_key_alias
}

variable "alb_cg_cmk_key_alias" {
  description = "Alias for CG key used for alb Server Side Encryption | Example : \"alias/test-key\""
  type = string
}

variable "alb_sg_tags" {
  description = "Tags Specific to ALB Secuity Groups | Example : { Name  = \"foobar-terraform-elb\" }"
  type = map(string)
}

#ELB permissions for accesslogs bucket policy
data "template_file" "elb_accesslogs_bucketpolicy" {
  template = file("policies/ELBAccessLogsBucketPolicy.json")
  vars = {
    account_id = local.account_id
    s3_arn = data.aws_s3_bucket.alb_accesslogs_bucket.arn
  }
}

data "aws_s3_bucket" "alb_accesslogs_bucket" {
  bucket = var.alb_accesslogs_bucket_name
}

variable "alb_accesslogs_bucket_name" {
  description = "Name of bucket used for storing ALB access logs. | Example : \"foobar-bucket\""
  type = string 
}

variable "alb_sg_prefix" {
  type        = string
  description = "A prefix for all Security Group resources | Example : \"test-lb\""
}

#ALB
variable "alb_ingress_port" {
  description = "The port the ALB will listen to | Example: 200 "
  type        = number
}

variable "alb_name" {
  description = "Name of the ALB | Example: \"test-lb-tf\""
  type        = string
}

variable "alb_ip_address_type" {
  description = "The type of IP addresses used by the subnets for your load balancer. The possible values are ipv4 and dualstack | Example: \"IPV4\""
  type        = string
}

variable "alb_enable_deletion_protection" {
  type        = bool
  description = "If true, deletion of the load balancer will be disabled via the AWS API. This will prevent Terraform from deleting the load balancer | Example : true"
}

variable "alb_subnet_id" {
  description = "List of subnets the ALB will be created in | Example: [\"subnet-9d4a7b6c\", ...]"
  type        = list(string)
}

variable "alb_enable_http_to_https_redirect" {
  description = "enter to enable  http to https redirect functonality | Example : true"
  type        = bool

}

variable "alb_target_group" {
  description = "Target group all requests to the ALB will be forwarded to | Example : \"arn:aws:elasticloadbalancing:us-west-2:187416307283:targetgroup/app-front-end/20cfe21448b66314\""
  type        = string

}
variable "alb_ssl_policy" {
  description = "Target group all requests to the ALB will be forwarded to | Example : \"ELBSecurityPolicy-2016-08\""
  type        = string

}
variable "alb_certificate_arn" {
  description = "Target group all requests to the ALB will be forwarded to | Example: \"arn:aws:iam::187416307283:server-certificate/test_cert_rab3wuqwgja25ct3n4jdj2tzu4\""
  type        = string

}

variable "alb_aws_vpc_id" {
  description = "VPC the ALB and the security group will be created in | Example: \"vpc-0d01658f31297e081\""
  type        = string
}

variable "alb_cidr_blocks_redirect" {
  description = "enter cidr block of http to https request | Example : [\"10.0.3.0/24\", ...]"
  type        = list(string)

}

variable "alb_bucket" {
  type        = string
  description = "The name of the bucket. If omitted, Terraform will assign a random, unique name | Example : \"my-tf-test-bucket\""
}


# IAM
variable "alb_policy_arn" {
  description = "A list of full arn of iam policies to attach this role | Example : \"arn:aws:iam::123456789012:policy/UsersManageOwnCredentials\""
  type        = string
}

variable "alb_session_duration" {
  description = "A value for maximum time of session duration in seconds (default 1h). This setting can have a value from 1 hour to 12 hours | Example : \"3600\""
  type        = string
}

# description

data "template_file" "elb_rbac_role_trust" {
  template = "policies/ElbRbacRoleTrust.json"
}

variable "alb_role_name" {
  description = "The logical name of role | Example : \"instance_role\""
  type        = string
}

variable "alb_common_tags" {
  description = "Various common tags to be declared | Example: { Name  = \"foobar-terraform-elb\" }"
  type        = map(string)
}
