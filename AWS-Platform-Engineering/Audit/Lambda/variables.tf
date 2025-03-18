variable env_type {
    type = string
    description = "Environment type"
}

variable event_rule_name{
    type = string
    description = "event rule name"
}

variable rule_id{
    type = map(string)
    description = "rule unique identifier"
}

variable region{
    type = string
}

variable sechublambda{
    type = number
}