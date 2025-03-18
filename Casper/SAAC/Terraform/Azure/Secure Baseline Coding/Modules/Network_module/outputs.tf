output "vnet_id" {
  description = "The id of the newly created vNet"
  value       = azurerm_virtual_network.vnet.id
}

output "vnet_name" {
  description = "The Name of the newly created vNet"
  value       = azurerm_virtual_network.vnet.name
}

output "vnet_location" {
  description = "The location of the newly created vNet"
  value       = azurerm_virtual_network.vnet.location
}

output "vnet_address_space" {
  description = "The address space of the newly created vNet"
  value       = azurerm_virtual_network.vnet.address_space
}

output "vnet_subnets" {
  description = "The ids of subnets created inside the newly created vNet"
  value       = azurerm_subnet.subnet.*.id
  # value = flatten(concat(azurerm_subnet.subnet.*.id, [var.gateway_subnet_address_prefix != null ? azurerm_subnet.gw_snet.0.id : null], [var.firewall_subnet_address_prefix != null ? azurerm_subnet.fw-snet.0.id : null]))
}

output "vnet_gw_subnet_id" {
  description = "The id of the gateway subnet"
  value = azurerm_subnet.gw_snet.*.id
}

