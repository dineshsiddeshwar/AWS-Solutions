variable "eh_map" {
  description = "(Optional) contains the SA and EH details for operations diagnostics."
  type = map(string)
  default     = {}
}

variable "log_analytics_workspace_id" {
  description = "(Optional) contains the log analytics workspace ID details for operations diagnostics."
  type = string
  default     = "/subscriptions/2deda99b-1d35-4ee1-a4ce-aa5a3875266a/resourceGroups/EYGDSSECbaseline-rg/providers/Microsoft.OperationalInsights/workspaces/acctest-01"
}

variable "storage_account_id" {
  description = "The storage account where the logs and mertics will be saved"
  type = string
  default     = "/subscriptions/2deda99b-1d35-4ee1-a4ce-aa5a3875266a/resourceGroups/EYGDSSECbaseline-rg/providers/Microsoft.Storage/storageAccounts/eygdsbaseline"
}

variable "name" {
  description = "(Required) Name of the diagnostics object."
  type = string
}

variable "resource_id" {
  description = "(Required) Fully qualified Azure resource identifier for which you enable diagnostics."
  type = string
}

variable "retention_days" {
  description = "(Optional) The number of days to retain the logs and metrics. Defaults to 7 days"
  default = 7
}
