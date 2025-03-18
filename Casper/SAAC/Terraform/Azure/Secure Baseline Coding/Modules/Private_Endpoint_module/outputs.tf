output "private_link_endpoint_ip" {
  value = data.azurerm_private_endpoint_connection.pe_connection.private_service_connection.0.private_ip_address
}

output "fqdn" {
  value = azurerm_private_dns_a_record.a_record.fqdn
}

output "private_dns_zone_name" {
  value = try(azurerm_private_dns_zone.pdz[0].name, "")
}
