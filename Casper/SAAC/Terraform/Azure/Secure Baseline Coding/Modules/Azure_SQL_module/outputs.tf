output "resource_group_name" {
  description = "The name of the resource group in which resources are created"
  value       = local.resource_group_name
}

output "resource_group_location" {
  description = "The location of the resource group in which resources are created"
  value       = local.location
}

output "storage_account_id" {
  description = "The ID of the storage account"
  value       = element(concat(azurerm_storage_account.storeacc.*.id, [""]), 0)
}

output "storage_account_name" {
  description = "The name of the storage account"
  value       = element(concat(azurerm_storage_account.storeacc.*.name, [""]), 0)
}

output "sec_storage_account_name" {
  description = "The name of the storage account"
  value       = element(concat(azurerm_storage_account.secondarystoreacc.*.name, [""]), 0)
}

output "primary_sql_server_id" {
  description = "The primary Microsoft SQL Server ID"
  value       = azurerm_sql_server.primary.id
}

output "primary_sql_server_fqdn" {
  description = "The fully qualified domain name of the primary Azure SQL Server"
  value       = azurerm_sql_server.primary.fully_qualified_domain_name
}

output "primarysql_server_name" {
  description = "The name of the storage account"
  value       = element(concat(azurerm_sql_server.primary.*.name, [""]), 0)
}

output "secondarysql_server_name" {
  description = "The name of the storage account"
  value       = element(concat(azurerm_sql_server.secondary.*.name, [""]), 0)
}

output "secondary_sql_server_id" {
  description = "The secondary Microsoft SQL Server ID"
  value       = element(concat(azurerm_sql_server.secondary.*.id, [""]), 0)
}

output "secondary_sql_server_fqdn" {
  description = "The fully qualified domain name of the secondary Azure SQL Server"
  value       = element(concat(azurerm_sql_server.secondary.*.fully_qualified_domain_name, [""]), 0)
}

output "sql_server_admin_user" {
  description = "SQL database administrator login id"
  value       = azurerm_sql_server.primary.administrator_login
  sensitive   = true
}

output "sql_server_admin_password" {
  description = "SQL database administrator login password"
  value       = azurerm_sql_server.primary.administrator_login_password
  sensitive   = true
}

output "sql_database_id" {
  description = "The SQL Database ID"
  value       = azurerm_sql_database.db["true"].id
}

output "sql_database_name" {
  description = "The SQL Database Name"
  value       = azurerm_sql_database.db["true"].name
}

output "sql_failover_group_id" {
  description = "A failover group of databases on a collection of Azure SQL servers."
  value       = element(concat(azurerm_sql_failover_group.fog.*.id, [""]), 0)
}
