
output "storage_account_id" {
  description = "The ID of the storage account"
  value       = module.sqlserver.storage_account_id
}

output "storage_account_name" {
  description = "The name of the storage account"
  value       = module.sqlserver.storage_account_name
}

output "sec_storage_account_name" {
  description = "The name of the storage account"
  value       = module.sqlserver.sec_storage_account_name

}
output "primary_sql_server_id" {
  description = "The primary Microsoft SQL Server ID"
  value       = module.sqlserver.primary_sql_server_id
}

output "primary_sql_server_fqdn" {
  description = "The fully qualified domain name of the primary Azure SQL Server"
  value       = module.sqlserver.primary_sql_server_fqdn
}

output "primarysql_server_name_" {
  description = "The name of the primary SQL server"
  value       = module.sqlserver.primarysql_server_name
}

output "secondarysql_server_name" {
  description = "The name of the secondary SQL server"
  value       = module.sqlserver.secondarysql_server_name
}

output "secondary_sql_server_id" {
  description = "The secondary Microsoft SQL Server ID"
  value       = module.sqlserver.secondary_sql_server_id
}

output "secondary_sql_server_fqdn" {
  description = "The fully qualified domain name of the secondary Azure SQL Server"
  value       = module.sqlserver.secondary_sql_server_fqdn
}

output "sql_server_admin_user" {
  description = "SQL database administrator login id"
  value       = module.sqlserver.sql_server_admin_user
  sensitive   = true
}

output "sql_database_id" {
  description = "The SQL Database ID"
  value       = module.sqlserver.sql_database_id
}

output "sql_database_name" {
  description = "The SQL Database Name"
  value       = module.sqlserver.sql_database_name
}

output "sql_failover_group_id" {
  description = "A failover group of databases on a collection of Azure SQL servers."
  value       = module.sqlserver.sql_failover_group_id
}

output "first_private_link_endpoint_ip" {
  value = module.firstendpoint.private_link_endpoint_ip
}

output "primary_plink_pe_fqdn" {
  value = module.firstendpoint.fqdn
}

