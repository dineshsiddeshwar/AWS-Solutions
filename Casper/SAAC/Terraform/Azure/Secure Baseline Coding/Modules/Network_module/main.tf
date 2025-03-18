#Azure Generic vNet Module

locals {
  resource_group_name = element(coalescelist(data.azurerm_resource_group.rgrp.*.name, azurerm_resource_group.rg.*.name, [""]), 0)
  location            = element(coalescelist(data.azurerm_resource_group.rgrp.*.location, azurerm_resource_group.rg.*.location, [""]), 0)
  if_ddos_enabled     = var.create_ddos_plan ? [{}] : []
}

data azurerm_resource_group "rgrp" {
  count = var.create_resource_group == false ? 1 : 0
  name = var.resource_group_name
}

resource "azurerm_resource_group" "rg" {
  count    = var.create_resource_group ? 1 : 0
  name     = var.resource_group_name
  location = var.location
  tags     = merge({ "Name" = format("%s", var.resource_group_name) }, var.tags, )
}


resource azurerm_virtual_network "vnet" {
  name                = var.vnet_name
  resource_group_name = local.resource_group_name
  location            = local.location
  address_space       = var.address_space
  dns_servers         = var.dns_servers
  tags                = merge({ "Name" = format("%s", var.vnet_name) }, var.tags, )

  dynamic "ddos_protection_plan" {
    for_each = local.if_ddos_enabled

    content {
      id     = azurerm_network_ddos_protection_plan.ddos[0].id
      enable = true
    }
  }

}

resource "azurerm_network_ddos_protection_plan" "ddos" {
  count               = var.create_ddos_plan ? 1 : 0
  name                = var.ddos_plan_name
  resource_group_name = local.resource_group_name
  location            = local.location
  tags                = merge({ "Name" = format("%s", var.ddos_plan_name) }, var.tags, )
}

resource "azurerm_subnet" "fw-snet" {
  count                = var.firewall_subnet_address_prefix != null ? 1 : 0
  name                 = "AzureFirewallSubnet"
  resource_group_name  = local.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = var.firewall_subnet_address_prefix #[cidrsubnet(element(var.vnet_address_space, 0), 10, 0)]
  service_endpoints    = var.firewall_service_endpoints
}

resource "azurerm_public_ip" "firewall_pip" {
  count               = var.firewall_subnet_address_prefix != null ? 1 : 0
  name                = "${var.vnet_name}-firewall-pip"
  location            = local.location
  resource_group_name = local.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = var.tags
}

resource "azurerm_firewall" "firewall" {
  count               = var.firewall_subnet_address_prefix != null ? 1 : 0
  name                = "${var.vnet_name}-firewall"
  location            = local.location
  resource_group_name = local.resource_group_name
  sku_name = var.firewall_sku_name
  sku_tier = var.firewall_sku_tier
  firewall_policy_id = var.firewall_policy_id
  dns_servers = var.firewall_dns_servers
  threat_intel_mode = var.threat_intel_mode

  ip_configuration {
    name                 = "firewall-ip-config"
    subnet_id            = azurerm_subnet.fw-snet[0].id
    public_ip_address_id = azurerm_public_ip.firewall_pip[0].id
  }

  tags = var.tags
}



resource "azurerm_subnet" "gw_snet" {
  count                = var.gateway_subnet_address_prefix != null ? 1 : 0
  name                 = "GatewaySubnet"
  resource_group_name  = local.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = var.gateway_subnet_address_prefix #[cidrsubnet(element(var.vnet_address_space, 0), 8, 1)]
  service_endpoints    = ["Microsoft.Storage"]
}

resource "azurerm_subnet" "subnet" {
  count                                          = length(var.subnet_names)
  name                                           = var.subnet_names[count.index]
  resource_group_name                            = local.resource_group_name
  virtual_network_name                           = azurerm_virtual_network.vnet.name
  address_prefixes                               = [var.subnet_prefixes[count.index]]
  service_endpoints                              = lookup(var.subnet_service_endpoints, var.subnet_names[count.index], null)
  enforce_private_link_endpoint_network_policies = lookup(var.subnet_enforce_private_link_endpoint_network_policies, var.subnet_names[count.index], false)
  enforce_private_link_service_network_policies  = lookup(var.subnet_enforce_private_link_service_network_policies, var.subnet_names[count.index], false)

}

locals {
  azurerm_subnets = {
    for index, subnet in azurerm_subnet.subnet :
    subnet.name => subnet.id
  }
}

resource "azurerm_subnet_network_security_group_association" "vnet" {
  for_each                  = var.nsg_ids
  subnet_id                 = local.azurerm_subnets[each.key]
  network_security_group_id = each.value
}

resource "azurerm_subnet_route_table_association" "vnet" {
  for_each       = var.route_tables_ids
  route_table_id = each.value
  subnet_id      = local.azurerm_subnets[each.key]
}

#---------------------------
# Storage Account, Log Analytics and monitoring diagnostics
#-------------------------------

resource "azurerm_storage_account" "sta" {
  name                     = var.storage_account_name
  resource_group_name      = local.resource_group_name
  location                 = local.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  tags = merge({ "Name" = "NetowrkLogWorkspace" }, var.tags, )
}

resource "azurerm_log_analytics_workspace" "law" {
  name                = "eygdsntwrklogworkspace"
  location            = local.location
  resource_group_name = local.resource_group_name
  sku                 = "PerGB2018"

  tags = merge({ "Name" = "NetworkLogWorkspace" }, var.tags, )
}

module "firewall_monitoring" {
  source = "../Diagnostic_module"
  name = "${var.vnet_name}-firewall-monitoring"
  resource_id = azurerm_firewall.firewall[0].id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
  storage_account_id = azurerm_storage_account.sta.id
}

resource "azurerm_monitor_diagnostic_setting" "example" {
  name               = "eygdsntwrkdiagnostic"
  target_resource_id = azurerm_virtual_network.vnet.id
  storage_account_id = azurerm_storage_account.sta.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id

  log {
    category = "VMProtectionAlerts"
    enabled  = false

    retention_policy {
      enabled = false
      days = 0
    }
  }

  metric {
    category = "AllMetrics"

    retention_policy {
      enabled = false
      days = 0
    }
  }
}

#-------------------------------------
# Network Watcher - Default is "true"
#-------------------------------------

# resource "azurerm_network_watcher" "nwatcher" { 
#   count               = var.create_network_watcher != false ? 1 : 0
#   name                = "NetworkWatcher_${local.location}"
#   location            = local.location
#   resource_group_name = local.resource_group_name
#   tags                = merge({ "Name" = format("%s", "NetworkWatcher_${local.location}") }, var.tags, )
# }

resource "azurerm_network_watcher_flow_log" "nwatcher" {
  network_watcher_name = "NetworkWatcher_eastus"
  resource_group_name  = "NetworkWatcherRG"

  network_security_group_id = lookup(var.nsg_ids, var.subnet_names[1], null)
  storage_account_id        = azurerm_storage_account.sta.id
  enabled                   = true

  retention_policy {
    enabled = true
    days    = 7
  }

  traffic_analytics {
    enabled               = true
    workspace_id          = azurerm_log_analytics_workspace.law.workspace_id
    workspace_region      = azurerm_log_analytics_workspace.law.location
    workspace_resource_id = azurerm_log_analytics_workspace.law.id
    interval_in_minutes   = 10
  }
}
