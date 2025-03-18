output "synapse_workspace_id" {
  description = "The ID of the Synapse Workspace in the Azure management plane."
  value = module.azsynapse.synapse_workspace_id
}

output "test_storage_account_id" {
  description = "The ID of the storage account"
  value       = module.azsynapse.test_storage_account_id
}

output "connect_storage_id" {
  description = "The ID of the target storage account"
  value       = module.azsynapse.*.connect_storage_id
}

output "storage_fs_id" {
  description = "The ID of the storage file system account"
  value       = module.azsynapse.storage_fs_id
}

output "azurerm_synapse_sql_pool" {
  description = "The ID of the synapse sql pool"
  value       = module.azsynapse.*.azurerm_synapse_sql_pool
}

output "azurerm_synapse_managed_private_endpoint" {
  description = "The ID of the synapse managed private endpoint"
  value       = module.azsynapse.azurerm_synapse_managed_private_endpoint
}
