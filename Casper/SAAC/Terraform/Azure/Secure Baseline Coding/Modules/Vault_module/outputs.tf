output "vault_id" {
  value = azurerm_key_vault.vault.id
}

output "vault_uri" {
  value = azurerm_key_vault.vault.vault_uri
}

output "key_vault_name" {
  value = azurerm_key_vault.vault.name
}
