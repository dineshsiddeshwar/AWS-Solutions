output "private_link_service_alias" {
  description = "A globally unique DNS Name for your Private Link Service. You can use this alias to request a connection to your Private Link Service."
  value       = azurerm_private_link_service.plink.alias
}

# output "network_interfaces" {
#   description = "A list of network interface resource ids that are being used by the service."
#   value       = azurerm_private_link_service.plink.network_interfaces
# }
