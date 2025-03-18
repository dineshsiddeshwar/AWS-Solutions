locals {
  resource_group_name = element(coalescelist(data.azurerm_resource_group.rgrp.*.name, azurerm_resource_group.rg.*.name, [""]), 0)
  location            = element(coalescelist(data.azurerm_resource_group.rgrp.*.location, azurerm_resource_group.rg.*.location, [""]), 0)
}

data "azurerm_resource_group" "rgrp" {
  count = var.create_resource_group == false ? 1 : 0
  name  = var.resource_group_name
}

resource "azurerm_resource_group" "rg" {
  count    = var.create_resource_group ? 1 : 0
  name     = var.resource_group_name
  location = var.location
  tags     = merge({ "Name" = format("%s", var.resource_group_name) }, var.tags, )
}

resource "azurerm_application_insights" "app_insights" {
  name                = var.app_insights_name
  location            = local.location
  resource_group_name = local.resource_group_name
  application_type    = var.application_type

  daily_data_cap_in_gb = var.daily_data_cap_in_gb
  retention_in_days    = var.retention_in_days
  sampling_percentage  = var.sampling_percentage
  disable_ip_masking   = var.disable_ip_masking
  tags                 = merge({ "Name" = format("%s", var.app_insights_name) }, var.tags, )

  daily_data_cap_notifications_disabled = var.daily_data_cap_notifications_disabled
}


resource "azurerm_application_insights_analytics_item" "analytics_items" {
  for_each                = var.analytics_items
  name                    = each.key
  application_insights_id = azurerm_application_insights.app_insights.id
  content                 = each.value.content
  type                    = each.value.type
  scope                   = each.value.scope
  function_alias          = lookup(each.value, "function_alias", null)
}

resource "azurerm_application_insights_api_key" "read_telemetry" {
  name                    = "tf-test-appinsights-read-telemetry-api-key"
  application_insights_id = azurerm_application_insights.app_insights.id
  read_permissions        = ["aggregate", "api", "draft", "extendqueries", "search"]
}

resource "azurerm_application_insights_api_key" "write_annotations" {
  name                    = "tf-test-appinsights-write-annotations-api-key"
  application_insights_id = azurerm_application_insights.app_insights.id
  write_permissions       = ["annotations"]
}

resource "azurerm_application_insights_api_key" "authenticate_sdk_control_channel" {
  name                    = "tf-test-appinsights-authenticate-sdk-control-channel-api-key"
  application_insights_id = azurerm_application_insights.app_insights.id
  read_permissions        = ["agentconfig"]
}

resource "azurerm_application_insights_api_key" "full_permissions" {
  name                    = "tf-test-appinsights-full-permissions-api-key"
  application_insights_id = azurerm_application_insights.app_insights.id
  read_permissions        = ["agentconfig", "aggregate", "api", "draft", "extendqueries", "search"]
  write_permissions       = ["annotations"]
}

resource "azurerm_application_insights_smart_detection_rule" "smart_detection_rules" {
  for_each                    = toset(var.smart_detection_rules)
  name                        = each.value
  application_insights_id     = azurerm_application_insights.app_insights.id
  additional_email_recipients = var.additional_email_recipients
}

resource "azurerm_application_insights_web_test" "web_tests" {
  for_each                = var.web_tests
  name                    = each.key
  location                = local.location
  resource_group_name     = local.resource_group_name
  application_insights_id = azurerm_application_insights.app_insights.id
  kind                    = each.value.kind
  geo_locations           = each.value.geo_locations
  configuration           = each.value.configuration
  frequency               = lookup(each.value, "frequency", 300)
  timeout                 = lookup(each.value, "timeout", 30)
  enabled                 = lookup(each.value, "enabled", true)
  retry_enabled           = lookup(each.value, "retry_enabled", true)
  description             = lookup(each.value, "description", null)
  tags                    = merge({ "Name" = format("%s", each.key) }, var.tags, )
}
