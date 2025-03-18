######################################################################################################################################################################
############################################################       Define required variables   #######################################################################
######################################################################################################################################################################
variable "resource_group" {
  type = map 
  }

variable "vnet_name" {
  type = string 
 }

variable "address_space" {
  type = list(string)
  }

variable "hub_vnet_id" {
  type = string
  }

variable "subnet" {
  type = map
}

variable "cust_scope" {
  type = string
  }

variable "az_policy_name" {
  type = string
 }

variable "az_policy_id" {
  type = string
  }

variable "az_policy_description" {
  type = string
}

variable "subnet_id" {
  type = string
  }

variable "nsg_id" {
  type = string
  }

variable "rbac_role_assignment_scope" {
  type = string
  }

variable "rbac_role_name" {
  type = string
}

variable "rbac_principal_id" {
  type = string
}

variable "vnet-diagsetting_name" {
  type = string
}

variable "vnet_diagtarget_id" {
  type = string
 }

variable "log_dump_resource_id" {
  type = string
  }

variable "vnet_log_category" {
  type = string
}

variable "log_retention_days" {
  type = number
 }

variable "cost_center" {
}
variable "ppmc_id" {
}
variable "toc" {
 }
variable "usage_id" {
}
variable "env_type" {
}
variable "exp_date" {
 }
variable "endpoint" {
}
variable "sd_period" {
}
variable "spoke_vnet_name" {
  type = string
}
variable "spoke_vnet_id" {
  type = string
}
variable "hubToSpoke_peering_name" {
  type = string
}

variable "spoketoHub_peering_name" {
  type = string
}

