variable env_type {
    type = string
    description = "Environment type"
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
