output "key_vault_id" {
  value = module.vault.vault_id
}

output "key_vault_name" {
  value = module.vault.key_vault_name
}

output "private_ips" {
  value = module.endpoint.private_link_endpoint_ip
}

output "fqdn" {
  value = module.endpoint.fqdn
}
