variable "df_name" {
  description = "The name for the data factory"
  type        = string
}

variable "resource_group_name" {
  description = "The resource group in which data factory needs to be created"
  type        = string
  default = "EYGDSSECbaseline-rg"
}

variable "tags" {
  description = "The tags that should be associated the data factory resource"
  # type        = map(string)
  # default     = {}
   default = {
    Department  = "EYGDSSEC"
    Environment = "Dev"
  }
}

variable "github_configuration" {
  description = "The git hub configuration block"
  type = list(object({
    account_name    = string
    branch_name     = string
    git_url         = string
    repository_name = string
    root_folder     = string
  }))
  default = []
}

variable "vsts_configuration" {
  description = "The vsts configuration block"
  type = list(object({
    account_name    = string
    branch_name     = string
    project_name    = string
    repository_name = string
    root_folder     = string
    tenant_id       = string
  }))
  default = []
}

variable "public_network_enabled" {
  description = "Is the Data Factory visible to the public network?"
  type        = bool
  default     = true
}

variable "dataset_azure_blob" {
  description = "For each azure_blob dataset and data factory linked service create an object"
  default     = {}
  /* ### Example
     ## dataset_name and one of `connection_string,sas_uri,service_endpoint` must be specified.
  dataset_azure_blob = {
    blob_data_set_1 = {
      dataset_name = string
      path = string
      filename = string
      folder = string

      schema_column = {
        name = string
        type = string
        description = string
      }

      description = string
      annotations = list(string)
      parameter = map
      additional_properties = map

      integration_runtime_name = string
      connection_string = string
      sas_uri = string
      service_endpoint = string
      use_managed_identity = bool
      service_principal_id = string
      service_principal_key = string
      tenant_id = string
    }
  }
  */
}


variable "dataset_cosmosdb_sqlapi" {
  description = "For each cosmosdb_sqlapi dataset and data factory linked service create an object"
  default     = {}
}

variable "dataset_delimited_text" {
  description = "For each delimited_text dataset and data factory linked service create an object"
  default     = {}
}

variable "dataset_http" {
  description = "For each http dataset and data factory linked service create an object"
  default     = {}
}

variable "dataset_json" {
  description = "For each http dataset and data factory linked service create an object"
  default     = {}
}

variable "dataset_mysql" {
  description = "For each mysql dataset and data factory linked service create an object"
  default     = {}
}

variable "dataset_parquet" {
  description = "For each parquet dataset and data factory linked service create an object"
  default     = {}
}

variable "dataset_postgresql" {
  description = "For each postgresql dataset and data factory linked service create an object"
  default     = {}
}

variable "dataset_sql_server_table" {
  description = "For each sql_server_table dataset and data factory linked service create an object"
  default     = {}
}

variable "azure_runtime" {
  description = "For each azure_runtime create an object"
  default     = {}
}

variable "azure_ssis_runtime" {
  description = "For each azure_ssis_runtime create an object"
  default     = {}
}

variable "azure_file_storage_lnk_svc" {
  description = "For each azure_file_storage_lnk_svc create an object"
  default     = {}
}

variable "azure_function_lnk_svc" {
  description = "For each azure_function_lnk_svc create an object"
  default     = {}
}

variable "azure_sql_database_lnk_svc" {
  description = "For each azure_sql_database_lnk_svc create an object"
  default     = {}
}

variable "azure_table_storage_lnk_svc" {
  description = "For each azure_table_storage_lnk_svc create an object"
  default     = {}
}

variable "data_lake_storage_gen2_lnk_svc" {
  description = "For each data_lake_storage_gen2_lnk_svc create an object"
  default     = {}
}

variable "sftp_lnk_svc" {
  description = "For each sftp_lnk_svc create an object"
  default     = {}
}

variable "snowflake_lnk_svc" {
  description = "For each snowflake_lnk_svc and key_vault_lnk_svc create an object"
  default     = {}
}

variable "synapse_lnk_svc" {
  description = "For each synapse_lnk_svc and key_vault_lnk_svc create an object"
  default     = {}
}

variable "df_pipeline" {
  description = "For each data factory pipeline and trigger create an object"
  default     = {}
}


