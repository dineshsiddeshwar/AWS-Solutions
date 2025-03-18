######################################################################################################################################################################
############################################################       Requirements section   #######################################################################
######################################################################################################################################################################

# Ensure private endpoint is integrated with private dns zone

resource "azurerm_private_dns_zone" "pe_private_dns_zone" {
  name                = var.pe_private_dns_zone_name
  resource_group_name = var.resource_group.name
}

resource "azurerm_private_endpoint" "private_endpoint" {
  name                = var.private_endpoint_name
  location            = var.resource_group.location
  resource_group_name = var.resource_group.name
  subnet_id           = var.subnet_id

  private_service_connection {
    name                           = var.private_service_connection_name
    private_connection_resource_id = var.resource_id # resource to which you want to assign the private endpoint.
    is_manual_connection           = false
    subresource_names              = var.subresource_names 
      
  }
  private_dns_zone_group {
    name = var.private_dns_zone_group_name
    private_dns_zone_ids = [
      azurerm_private_dns_zone.pe_private_dns_zone.id,
    ]
  }
  tags = var.sa_tags # Ensure that private endpoint uses standard organizational resource tagging method
}

# Ensure least privilege access method for Private Endpoint is implemented using Role-based access control (RBAC)

resource "azurerm_role_assignment" "pe_role_assignment" {
  scope                = azurerm_private_endpoint.private_endpoint.id
  role_definition_name = var.role_definition_name
  principal_id         = var.principal_id # Object ID of the security principal to who should assume the role - This should be Object ID of the newly recreated VM if Trusted Launch subsequently set to 'True' through Terraform
}

# Ensure Secondary accounts are used for administrative tasks and any suspicious activity are alerted - could not find relvant code for this control


resource "azurerm_monitor_action_group" "pe_monitor_action_group" {
  name                = var.pe_monitor_action_group_name
  resource_group_name = var.resource_group.name
  short_name          = var.pe_monitor_action_group_short_name
}

  resource "azurerm_monitor_activity_log_alert" "pe_monitor_activity_log_alert" {
  name                = "example-activitylogalert"
  resource_group_name = var.resource_group.name
  scopes              = [azurerm_private_endpoint.private_endpoint.id]
  description         = "This alert will monitor a specific private endpoint updates."

  criteria {    
    operation_name = "Microsoft.Insights/AlertRules/Write"
    target_resource_type ="microsoft.network/privateendpoints"
    category       = "Administrative"
  }
  action {
    action_group_id = azurerm_monitor_action_group.pe_monitor_action_group.id
  }
}

# Ensure Activity logging is enabled for Azure Private Endpoint - needs to invalidated as it needs to be moved to subscription baseline requirement section.
