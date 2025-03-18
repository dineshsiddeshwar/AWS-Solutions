locals {
  logs = data.azurerm_monitor_diagnostic_categories.amdc.logs
  metrics = data.azurerm_monitor_diagnostic_categories.amdc.metrics
}

data "azurerm_monitor_diagnostic_categories" "amdc" {
  resource_id = var.resource_id
}

resource "azurerm_monitor_diagnostic_setting" "diagnostics" {
  name               = "${var.name}-diag"
  target_resource_id = var.resource_id

  eventhub_name                  = lookup(var.eh_map, "eh_name", null)
  eventhub_authorization_rule_id = lookup(var.eh_map, "eh_id", null) != null ? "${var.eh_map.eh_id}/authorizationrules/RootManageSharedAccessKey" : null

  log_analytics_workspace_id     = var.log_analytics_workspace_id
  # log_analytics_destination_type = var.log_analytics_workspace_id != "" ? "Dedicated" : null
  # commenting log_analytics_destination_type as it seems to be re-applying the parameter on every terraform plan/ apply runs.

  storage_account_id = var.storage_account_id

  dynamic "log" {
    for_each = local.logs
    content {
      category = log.value

      retention_policy {
        enabled = false
        days = var.retention_days
      }
    }
  }

  dynamic "metric" {
    for_each = local.metrics
    content {
      category = metric.value

      retention_policy {
        enabled = false
        days = var.retention_days
      }
    }
  }
}
