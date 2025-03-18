output "id" {
  description = "The ID of the Databricks Workspace in the Azure management plane."
  value       = module.azdatabricks.id

}

output "managed_resource_group_id" {
  description = "The ID of the Managed Resource Group created by the Databricks Workspace."
  value       = module.azdatabricks.managed_resource_group_id

}

output "workspace_url" {
  description = "The workspace URL which is of the format 'adb-{workspaceId}.{random}.azuredatabricks.net'"
  value       = module.azdatabricks.workspace_url

}

output "workspace_id" {
  description = "The unique identifier of the databricks workspace in Databricks control plane."
  value       = module.azdatabricks.workspace_id

}