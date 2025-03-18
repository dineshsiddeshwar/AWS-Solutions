variable master_account {
    type = string
    description = "master account"
}

variable role_arn {
    type = string
    description = "platform admin role arn"
}

variable private_production_ou {
    type = string
    description = "private production ou id"
}

variable private_exception_ou {
    type = string
    description = "private exception ou id"
}

variable public_production_ou {
    type = string
    description = "public production ou id"
}

variable hybrid_account_ou {
    type = string
    description = "hybrid account ou id"
}

variable public_exception_ou {
    type = string
    description = "public exception ou id"
}

variable main_policy_id_private {
    type = string
    description = "main policy id private"
}

variable main_policy_id_public {
    type = string
    description = "main policy id public"
}

variable main_policy_id_hybrid {
    type = string
    description = "main policy id hybrid"
}

variable titan_team_dl {
    type = string
    description = "titan team dl"
}

variable scp_env_type {
    type = string
    description = "Dev, acceptance, prod"
}