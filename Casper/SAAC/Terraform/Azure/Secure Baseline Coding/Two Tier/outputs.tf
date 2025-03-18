output "vnet_id" {
  description = "The id of the newly created vNet"
  value       = module.vnet.vnet_id
}

output "vnet_name" {
  description = "The Name of the newly created vNet"
  value       = module.vnet.vnet_name
}

output "vnet_location" {
  description = "The location of the newly created vNet"
  value       = module.vnet.vnet_location
}

output "vnet_address_space" {
  description = "The address space of the newly created vNet"
  value       = module.vnet.vnet_address_space
}

output "vnet_subnets" {
  description = "The ids of subnets created inside the newl vNet"
  value       = module.vnet.vnet_subnets
}


output "vnet_gw_subnet_id" {
  description = "The ids of subnets created inside the newl vNet"
  value       = element(module.vnet.vnet_gw_subnet_id, 0)
}