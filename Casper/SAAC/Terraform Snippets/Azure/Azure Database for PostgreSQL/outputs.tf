output "adpostgresql_id" {
  description = "ID of postgre sql database"
  value       = azurerm_postgresql_database.postgresql_database.id
}
