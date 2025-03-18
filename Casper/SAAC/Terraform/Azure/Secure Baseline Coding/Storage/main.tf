resource "azurerm_resource_group" "demo" {
  name     = "${var.prefix}-rg"
  location = var.location
}

resource "random_string" "unique" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_storage_account" "this" {
  name                      = substr(format("sta%s%s", lower(replace(var.storage_account_name, "/[[:^alnum:]]/", "")), random_string.unique.result), 0, 24)
  resource_group_name       = azurerm_resource_group.demo.name
  location                  = var.location
  account_kind              = var.account_kind
  account_tier              = var.account_tier
  account_replication_type  = var.account_replication_type
  access_tier               = var.access_tier
  enable_https_traffic_only = var.https_traffic
  min_tls_version           = var.min_tls_version
  infrastructure_encryption_enabled  = var.infrastructure_encryption
  allow_nested_items_to_be_public = var.nested_items

  tags = var.tags

  blob_properties {
    delete_retention_policy {
      days = var.blob_soft_delete_retention_days
    }
    container_delete_retention_policy {
      days = var.container_soft_delete_retention_days
    }
    versioning_enabled       = var.enable_versioning
    last_access_time_enabled = var.last_access_time_enabled
    change_feed_enabled      = var.change_feed_enabled
  }

  dynamic network_rules {
    for_each = var.network_rules
    content {
      default_action           = network_rules.value.default_action
      bypass                   = network_rules.value.bypass
      ip_rules                 = network_rules.value.ip_rules
      virtual_network_subnet_ids = network_rules.value.virtual_network_subnet_ids
    }
  }
}

#--------------------------------------
# Storage Advanced Threat Protection
#--------------------------------------
resource "azurerm_advanced_threat_protection" "atp" {
  target_resource_id = azurerm_storage_account.this.id
  enabled            = var.enable_advanced_threat_protection
}


# Storage Diragnostic setting
# If you want to enable the diagnostic on blob and other services then specifiaclly need to define the blob in Like :- target_resource_id = "${data.azurerm_storage_account.example.id}/blobServices/default"

resource "azurerm_monitor_diagnostic_setting" "base" {
  name               = var.diagnostic_name
  target_resource_id = azurerm_storage_account.this.id
  storage_account_id = var.sa_account_id
  #eventhub_authorization_rule_id = 
  #log_analytics_workspace_id = 


  metric {
    category = "Transaction"

    retention_policy {
      enabled = false
    }
  }
}
   
