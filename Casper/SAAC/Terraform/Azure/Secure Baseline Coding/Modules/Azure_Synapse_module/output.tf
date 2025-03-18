output "synapse_workspace_id" {
  value = azurerm_synapse_workspace.azsynapse.id
}

output "test_storage_account_id" {
  description = "The ID of the storage account"
  value       = local.storage_account_id
}

output "connect_storage_id" {
  description = "The ID of the target storage account"
  value       = azurerm_storage_account.storage_connect.*.id
}

output "storage_fs_id" {
  description = "The ID of the storage file system account"
  value       = azurerm_storage_data_lake_gen2_filesystem.storagefs.id
}

output "azurerm_synapse_sql_pool" {
  description = "The ID of the synapse sql pool"
  value       = azurerm_synapse_workspace.azsynapse.*.id
}

output "azurerm_synapse_managed_private_endpoint" {
  description = "The ID of the synapse managed private endpoint"
  value       = azurerm_synapse_managed_private_endpoint.pvt_endoint.id
}
