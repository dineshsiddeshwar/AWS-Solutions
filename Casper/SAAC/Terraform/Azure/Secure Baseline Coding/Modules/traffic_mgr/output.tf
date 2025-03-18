output "traffic_mgr_endpoint_id" {
  value = azurerm_traffic_manager_endpoint.endpoint.id
}

output "traffic_mgr_profile_id" {
  value = azurerm_traffic_manager_profile.profile.id
}

output "traffic_mgr_profile_fqdn" {
  value = azurerm_traffic_manager_profile.profile.fqdn
}
