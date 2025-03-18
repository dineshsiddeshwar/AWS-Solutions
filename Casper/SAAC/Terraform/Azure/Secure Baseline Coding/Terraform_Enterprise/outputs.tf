output "tfe_fqdn" {
  value = azurerm_public_ip.pip.fqdn
}

output "tfe_pip" {
  value = azurerm_public_ip.pip.ip_address
}

output "jump_server_fqdn" {
  value = azurerm_public_ip.jump_pip.fqdn
}

output "jump_server_pip" {
  value = azurerm_public_ip.jump_pip.ip_address
}

output "storage_container_id" {
  value = azurerm_storage_container.tfe.id
}

output "psql_id" {
  value = azurerm_postgresql_server.tfe.id
}

output "psql_fqdn" {
  value = azurerm_postgresql_server.tfe.fqdn
}
