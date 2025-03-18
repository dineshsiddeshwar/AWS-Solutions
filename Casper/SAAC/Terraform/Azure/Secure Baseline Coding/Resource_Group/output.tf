output "Resource-Group-id" {
  value = azurerm_resource_group.rg.id
}

output "storage_account_id" {
  value = azurerm_storage_account.sa.id
}

output "tfstate_container_id" {
  value = azurerm_storage_container.container.id
  sensitive = true
}
