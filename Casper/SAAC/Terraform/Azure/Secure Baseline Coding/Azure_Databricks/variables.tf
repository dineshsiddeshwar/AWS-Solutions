variable "settings_name" {
  description = "The basename of the resource to create, the basename will be sanitized as per supported characters set for each Azure resources"
  default     = "eytest-databricksws"

}

variable "global_settings_prefix" {
  description = "A list of prefix to append as the first characters of the generated name - prefixes will be separated by the separator character"
  default     = ["a", "b"]
}

variable "random_length" {
  description = "A default to 0 : Define the seed to be used for random generator. 0 will not be respected and will generate a seed based in the unix time of the generation."
  default     = 5

}

variable "clean_input" {
  description = "Defaults to true. remove any noncompliant character from the name, suffix or prefix."
  type    = bool
  default = true

}

variable "sku" {
  description = "The sku to use for the Databricks Workspace. Possible values are standard, premium, or trial. Changing this can force a new resource to be created in some circumstances."
  type    = string
  default = "standard"

}

variable "managed_resource_group_name" {
  description = "Azure requires that this Resource Group does not exist in this Subscription (and that the Azure API creates it) - otherwise the deployment will fail."
  type        = string
  default     = ""
}


variable "location" {
  description = "Specifies the supported Azure location where to create the resource. Changing this forces a new resource to be created."
  type        = string
  default     = "eastus"
}

variable "resource_group_name" {
  description = "The name of the resource group where to create the resource."
  type        = string
  default     = "EYGDSSECbaseline-rg"
}

variable "tags" {
  description = "Base tags for the resource to be inherited from the resource group."
  type        = map(any)
  default = {
    Department  = "EYGDSSEC"
    Environment = "Dev"
  }
}

variable "custom_parameters" {
  type = list(object({
    no_public_ip        = bool
    public_subnet_name  = string
    private_subnet_name = string
    virtual_network_id  = string
  }))
  default = []



}