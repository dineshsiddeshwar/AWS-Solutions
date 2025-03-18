# AWS Provider variable

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

variable "aws_region" {
  description = "Aws region where resource needs to be deployed | Example: \"us-west-2\""
  type        = string
}

# Tags used for common resource
variable "ses_common_tags" {
  type        = map(string)
  description = "Default tags attached to all resources | Example: { Name = \"ses_system_1\", ... }"
}

variable "ses_prefix" {
  type        = string
  description = "A prefix for all the resource | Example: \"test-lb\""
}

# VPC Input Variables

data "aws_vpc" "ses_vpc_id" {
  id = var.ses_vpc_id
}

data "aws_vpc_endpoint" "ses_vpc_endpoint_id" {
  vpc_id       = data.aws_vpc.ses_vpc_id.id
  service_name = var.ses_service_name
}

variable "ses_vpc_id" {
  type        = string
  description = "VPC Id of the deployed VPC, can be found on Confluence page AWS VPC CIDR Deployed (Auto updated) | Example: \"vpc-0bbc736e\""
}

variable "ses_vpc_sg" {
  type        = set(string)
  description = "AWS Security group ID created for the VPC ID, Refer confluence page AWS Standard Security Group Baseline | Example: \"sg-051c238028a9a1e42\""
}

variable "ses_sns_topic_arn" {
  type        = string
  description = "Enter the sns topic arn | Example: \"arn:aws:sns:us-east-1:1234567890123456:mytopic\""
}

variable "ses_service_name" {
  type        = string
  description = "Enter service name for VPC endpoint | Example: \"com.amazonaws.us-west-2.ses\""
}

variable "ses_vpc_endpoint_type" {
  type        = string
  description = "Enter type of VPC endpoint like Interface , Gateway etc.., | Example: \"Gateway\""
}

variable "ses_vpc_endpoint" {
  type        = string
  description = "Enter the name for ses vpc endpoint | Example: \"vpce-0123example\""
}

# kms key & alias

data "aws_kms_key" "ses_cmk_key" {
  key_id = var.ses_key_arn
}

data "aws_kms_alias" "ses_cmk_key_alias" {
  name = "alias/${var.ses_alias_name}"
}

variable "ses_key_arn" {
  description = "The name of the key arn | Example: \"arn:aws:kms:us-west-2:111122223333:key/0987dcba-09fe-87dc-65ba-ab0987654321\""
  type        = string
  sensitive   = true
}

variable "ses_alias_name" {
  description = "The name of the key alias | Example: \"alias/key_1\""
  type        = string
}

# IAM User
variable "ses_user_name" {
  type        = string
  description = "Enter the name of user to have least privledge to access SES service | Example: \"ses_account_name\""
}

variable "ses_user_policy" {
  type        = string
  description = "Enter the name of policy to have least privledge to access SES service | Example: \"ExampleAuthorizationPolicy\""
}

# Policy : SES resource policies enforce least privilege 
data "template_file" "ses_least_privilege_access" {
  template = file("policies/SESLeastPrivilegeAccessPolicy.json")
  vars = {
    ses_Recipients      = var.ses_recipients      # Example : *@aws.capgroup.com
    ses_fromAddress     = var.ses_fromaddress     # Example : operations@aws.capgroup.com
    ses_FromDisplayName = var.ses_fromdisplayname # Example : Operations
  }
}

variable "ses_recipients" {
  type        = string
  description = "Enter the Recipient Addresses to restrict user to call the SES email-sending APIs, but only to recipient addresses in domain example.com | Example: \"karen@example.com\""
  sensitive   = true
}

variable "ses_fromaddress" {
  type        = string
  description = "Enter the From Address to restrict a user to call the SES email-sending APIs, but only if the From address | Example: \"operationskaren@example.com\""
  sensitive   = true
}

variable "ses_fromdisplayname" {
  type        = string
  description = "Enter the Display name of a user to call the SES email-sending APIs, but only if the display name of the From address includes like Operations- | Example: \"Operations\""
  sensitive   = true
}

# Policy : SES resource policies for approved list of Recipients Domains only 
data "template_file" "ses_approved_listof_domain_policy" {
  template = file("policies/SESApprovedListOfDomainPolicy.json")
  vars = {
    ses_resource_arn       = var.ses_resource_arn       # Example : arn:aws:ses:us-east-1:848721808435:identity/capgroup.com
    ses_principal_org_id   = var.ses_principal_org_id   # Example : o-1eax4cor3c
    ses_list_of_recipients = var.ses_list_of_recipients # Example : "*@capgroup.com", "*@thecapitalgroup.com", etc
  }
}

variable "ses_resource_arn" {
  type        = string
  description = " Enter the SES resource ARN | Example: \"arn:aws:ses:us-west-2:111122223333:identity/awesome@example.com\""
}

variable "ses_principal_org_id" {
  type        = string
  description = " Enter the Principal Organization ID | Example: \"o-1eax4cor3c\""
}

variable "ses_list_of_recipients" {
  type        = string
  description = "Enter the approved list of recipents domains | Example: \"awesome@example.com\""
}

# SES verified identity is created using CG owned domain
variable "ses_domain_name" {
  type        = string
  description = "Enter the domain name to assign to SES | Example: \"example.com\""
}

# Policy : SES resource policies for role based access 
data "template_file" "ses_resource_based_iam_role_policy" {
  template = file("policies/SESResourceBasedIAMRolePolicy.json")
  vars = {
    ses_iam_role_arn  = var.ses_iam_role_arn
    source_ip_address = var.source_ip_address
  }
}

variable "ses_iam_role_arn" {
  type        = string
  description = "Enter the iam role arn for ses resource | Example: \"arn:aws:iam::111122223333:root\""
}

variable "source_ip_address" {
  type        = string
  description = "Enter the list of IP address | Example: \"203.0.113.0/24\""
}

# Domain & DKIM Identity

variable "ses_configuration_set" {
  type        = string
  description = "Enter the configuration set name for tls policy name | Example: \"event_destination_sns\""
}

variable "ses_role_name" {
  type        = string
  description = "Enter the iam role name for ses resource | Example: \"instance_role\""
}

variable "ses_iam_policy_name" {
  type        = string
  description = "Enter the iam role policy name for ses resource | Example: \"ses_basicexecution_role\""
}

# Policy : SES Assume role polyc for IAM Role
data "template_file" "ses_assumerole_policy" {
  template = file("policies/SESAssumeRolePolicy.json")
}
