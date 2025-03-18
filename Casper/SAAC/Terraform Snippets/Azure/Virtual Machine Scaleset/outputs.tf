output "vmascaleset_id" {
  description = "ID of Virtual machine scale set"
  value       = azurerm_linux_virtual_machine_scale_set.vm_scale_set.id
}
