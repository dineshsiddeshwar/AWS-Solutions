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

variable event_rule_name {
    type = string
    description = "event rule name"
}

variable service_now_itom_discovery_child_instance_profile{
    type = string
    description = "audit account service now itom discovery child instance profile"
}


variable rule_id{
    type = map(string)
    description = "rule unique identifier"
}


variable account_id{
    type = string
    description = "Account id for audit account "
}

variable payer_account_id {
    type = string
    description = "Account id for payer account "
}

variable notifyRole_id{
    type = string
    description = "Role id of notify role"
}

variable customactionrole_id{
    type = string
    description = "Role id of customaction role"
}

variable orchestratorrole_id{
    type = string
    description = "Role id of orchestrator role"
}

variable remediatewithsharreventsrule_id{
    type = string
    description = "Role id of remediatewithsharreventsrule role"
}

variable cis41eventsrulerole_id{
    type = string
    description = "Role id of cis41eventsrule role"
}

variable CIS41AutoEventRule_statement_id {
    type = string
    description = "Statement id for CIS41AutoEventRule"
}

variable CIS42AutoEventRule_statement_id {
    type = string
    description = "Statement id for CIS41AutoEventRule"
}

variable SCEC213AutoEventRule_statement_id{
    type = string
    description = "Statement id for SCEC213AutoEventRule"
}

variable SCEC214AutoEventRule_statement_id{
    type = string
    description = "Statement id for SCEC214AutoEventRule"
}

variable ScoreCardBucketName{
    type = string
    description = "Name of the scorecard bucket"
}