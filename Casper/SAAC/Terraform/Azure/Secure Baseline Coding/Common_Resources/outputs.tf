output "Log_Analytics_Workspace_id" {
  value = azurerm_log_analytics_workspace.law.id
}

output "storage_account_id" {
  value = azurerm_storage_account.storage.id
}

output "diagnostic_setting_name" {
  value = module.diagnostic.name
}

output "diagnostic_setting_id" {
  value = module.diagnostic.id
}
