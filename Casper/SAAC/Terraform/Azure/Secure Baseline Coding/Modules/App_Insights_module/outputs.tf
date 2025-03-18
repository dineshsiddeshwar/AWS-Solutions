output "app_insights_id" {
  value = azurerm_application_insights.app_insights.app_id
}

output "app_id" {
  value = azurerm_application_insights.app_insights.app_id
}

output "instrumentation_key" {
  value = azurerm_application_insights.app_insights.instrumentation_key
}

output "connection_string" {
  value = azurerm_application_insights.app_insights.connection_string
}

output "analytics_item_ids" {
  value = [
    for key in var.analytics_items:
      azurerm_application_insights_analytics_item.analytics_items[key].id
  ]
}

output "read_telemetry_api_key" {
  value = azurerm_application_insights_api_key.read_telemetry.api_key
}

output "write_annotations_api_key" {
  value = azurerm_application_insights_api_key.write_annotations.api_key
}

output "authenticate_sdk_control_channel" {
  value = azurerm_application_insights_api_key.authenticate_sdk_control_channel.api_key
}

output "full_permissions_api_key" {
  value = azurerm_application_insights_api_key.full_permissions.api_key
}

output "smart_detection_rule_ids" {
  value = [
    for key in var.smart_detection_rules:
      azurerm_application_insights_smart_detection_rule.smart_detection_rules[key].id
  ]
}

output "webtest_ids" {
  value = [
    for key in var.web_tests:
      azurerm_application_insights_web_test.web_tests[key].id
  ]
}

output "webtests_synthetic_ids" {
  value = [
    for key in var.web_tests:
      azurerm_application_insights_web_test.web_tests[key].synthetic_monitor_id
  ]
}
