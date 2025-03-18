variable platform_cloudhealth_account {
    type = string
    description = "platform cloudhealth account"
}

variable platform_cloudhealth_external_id {
    type = string
    description = "platform cloudhealth external id"
}

variable s3_bucket {
    type = string
    description = "s3 bucket for cloudhealth"
}

variable env_type {
    type = string
    description = "Environment type"
}
#variable audit_account{
#    type = number
#    description = "audit account number"
#}

variable ou_id{
    type = string
    description = "Organization id"
}

variable instance_profile_name{
    type = string
    description = "instance profile name"
}

variable "account_id" {
    type = string
    description = "account id of log archieve account"
  
}

variable "cloudtrail_bucket_rule_id" {
    type = string
    description = "Rule id of lifecycle rules for cloudtrail bucket"
}

variable "config_bucket_rule_id"{
    type = string
    description = "Rule id of lifecycle rules for config bucket"
}

variable "s3accesslogs_bucket_rule_id"{
    type = string
    description = "Rule id of lifecycle rules for s3accesslogs bucket"
}

variable "vpcflowlogs_bucket_rule_id"{
    type = string
    description = "Rule id of lifecycle rules for vpcflowlogs bucket"
}