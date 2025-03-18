variable master_account {
    type = string
    description = "master account"
}

variable role_arn {
    type = string
    description = "platform admin role arn"
}

variable SnowNerworkVPCIntegrationLogBucket {
    type = string
    description = "Snow Nerwork VPC Integration Log Bucket"
}

variable vpc_flow_bucket_env_type {
    type = string
    description = "dev, acceptance, prod"
}