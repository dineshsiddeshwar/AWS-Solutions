#Virtual Machine Scaleset requirement
# Enable autoscale will monitor abnormal scaling of VMS

# terraform import azurerm_linux_virtual_machine_scale_set.example /subscriptions/xxxxxx-xxxxxx-xxxxxx-xxxxxx-xxxxxx/resourceGroups/yourvaluehere/providers/Microsoft.Compute/virtualMachinesscaleset/yourvaluehere
# The azurerm_virtual_machine_scale_set resource has been deprecated in favour of the azurerm_linux_virtual_machine_scale_set and azurerm_windows_virtual_machine_scale_set resources. 
# Here for reference, choosing linux virtual machine scale set for control requirement. You can use windows VM scale set as well based on the requirement.

resource "azurerm_linux_virtual_machine_scale_set" "vm_scale_set" {
  name                            = var.vm_scale_set.linux_vm_name
  resource_group_name             = var.resource_group.name
  location                        = var.resource_group.location
  sku                             = var.vm_scale_set.sku
  instances                       = var.vm_scale_set.instances
  disable_password_authentication = false
  admin_username                  = data.azurerm_key_vault_secret.user.value
  admin_password                  = data.azurerm_key_vault_secret.password.value
  tags                            = var.vss_tags 

  source_image_reference {
    publisher = var.source_image_referenc_details.publisher
    offer     = var.source_image_referenc_details.offer
    sku       = var.source_image_referenc_details.sku
    version   = var.source_image_referenc_details.version
  }

  os_disk {
    storage_account_type = var.os_disk_details.storage_account_type
    caching              = var.os_disk_details.caching
  }

  network_interface {
    name    = var.network_interface_name
    primary = true

    ip_configuration {
      name      = var.ip_configuration_name
      primary   = true
      subnet_id = var.subnet_id
    }
  }
}

resource "azurerm_monitor_autoscale_setting" "monitor_autoscale_setting" {
  name                = var.monitor_autoscale_setting_name
  resource_group_name = var.resource_group.name
  location            = var.resource_group.location
  target_resource_id  = azurerm_linux_virtual_machine_scale_set.vm_scale_set.id

  profile {
    name = var.profile_name

    capacity {
      default = var.capacity.default
      minimum = var.capacity.minimum
      maximum = var.capacity.maximum
    }

    rule {
      metric_trigger {
        metric_name        = var.metric_trigger.metric_name
        metric_resource_id = azurerm_linux_virtual_machine_scale_set.vm_scale_set.id
        time_grain         = var.metric_trigger.time_grain
        statistic          = var.metric_trigger.statistic
        time_window        = var.metric_trigger.time_window
        time_aggregation   = var.metric_trigger.time_aggregation
        operator           = var.metric_trigger.operator
        threshold          = var.metric_trigger.threshold
      }

      scale_action {
        direction = var.scale_action.direction
        type      = var.scale_action.type
        value     = var.scale_action.value
        cooldown  = var.scale_action.cooldown
      }
    }
  }
}
