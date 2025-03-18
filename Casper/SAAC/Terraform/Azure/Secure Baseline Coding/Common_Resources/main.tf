data "azurerm_resource_group" "rg" {
  name = "EYGDSSECbaseline-rg"
}

data "azurerm_client_config" "current" {}

resource "azurerm_storage_account" "storage" {
  name                      = "eygdsbaseline"
  resource_group_name       = data.azurerm_resource_group.rg.name
  location                  = data.azurerm_resource_group.rg.location
  account_tier              = "Standard"
  account_replication_type  = "LRS"
  enable_https_traffic_only = true
  allow_blob_public_access  = false

  blob_properties {
    delete_retention_policy {
      days = 7
    }
  }

  identity {
    type = "SystemAssigned"
  }

  tags = merge(var.tags, {"ms-resource-usage" = "azure-cloud-shell"})
}

resource "azurerm_storage_encryption_scope" "storage_encryption" {
  name               = "microsoftmanaged"
  storage_account_id = azurerm_storage_account.storage.id
  source             = "Microsoft.Storage"
}

resource "azurerm_log_analytics_workspace" "law" {
  name                = "acctest-01"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

data "azurerm_storage_account" "sa_data" {
  name                = "eygdssecterraformstate"
  resource_group_name = "EYGDSSEC-rg"
}

module "diagnostic" {
  source                     = "../Modules/Diagnostic_module"
  name                       = "eygdssec_common"
  resource_id                = data.azurerm_storage_account.sa_data.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
}

resource "azurerm_monitor_action_group" "ag" {
  name                = "BaselineActionGroup"
  resource_group_name = data.azurerm_resource_group.rg.name
  short_name          = "baselien_ag"

    email_receiver {
    name                    = "sec_baseline_team"
    email_address           = "vignesh.seethapathy@gds.ey.com"
    use_common_alert_schema = true
  }
}
