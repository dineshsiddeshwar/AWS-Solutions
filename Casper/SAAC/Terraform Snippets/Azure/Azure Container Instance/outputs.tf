output "contianerinstance_id" {
  description = "ID of Container Instance"
  value       = azurerm_container_group.container_group.id
}
