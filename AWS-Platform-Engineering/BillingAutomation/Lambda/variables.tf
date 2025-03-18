variable athena_database {
    type = string
    description = "Athena Database"
}

variable athena_table{
    type = string
    description = "athena_table"
}

variable s3_output_location{
    type = string
    description = "s3_output_location"
}

variable s3_bucket{
    type = string
    description = "s3_bucket"
}

variable account_id{
    type = string
    description = "account_id of payer account"
}

variable cost_tracker{
    type = string
    description = "cost_tracker file"
}

variable main_billing_file{
    type = string
    description = "main_billing_file"
}

variable from_email{
    type = string
    description = "sender email to send billign report"
}

variable to_email{
    type = string
    description = "receiver email to send billign report"
}
