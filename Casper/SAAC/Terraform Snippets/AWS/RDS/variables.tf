variable "db_deployment_region" {
    type = string
    default = "us-west-1"
}

variable "db_name" {
    type = string
    default = null
}

variable "db_username" {
    type = string
    default = "terraform_username"
}

variable "db_password" {
    type = string
    default = "terraform_password"
    sensitive = true
}

variable "db_allocated_storage" {
    type = number
    default = 20
}

variable "db_storage_type" {
    type = string
    default = "gp2"
}

variable "db_engine" {
    type = string
    default = "mysql"
}

variable "db_engine_version" {
    type = string
    default = "5.7"
}

variable "db_instance_class" {
    type = string
    default = "db.t2.micro"
}

variable "db_backup_retention_period" {
    type = number
    default = 10
}

variable "db_deletion_protection" {
    type = bool
    default = false
}

variable "db_parameter_group_name" {
    type = string
    default = "default.mysql5.7"
}

variable "db_skip_final_snapshot" {
    type = bool
    default = true
}

variable "db_instance_ingress_access" {
    type = map
    default = {
        from_port = ["3306"]
        to_port = ["3306"]
        protocol = ["tcp"]
    }
}

variable "db_subnet_region" {
    type = list(string)
    default = ["us-west-1b","us-west-1c"]
}