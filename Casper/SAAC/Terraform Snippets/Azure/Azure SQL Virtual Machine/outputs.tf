output "sqlvm_id" {
  description = "ID of SQL Virtual Machine"
  value       = azurerm_mssql_virtual_machine.mssql_vm.id
}
