

locals {
  resource_group_name                 = element(coalescelist(data.azurerm_resource_group.rgrp.*.name, azurerm_resource_group.rg.*.name, [""]), 0)
  location                            = element(coalescelist(data.azurerm_resource_group.rgrp.*.location, azurerm_resource_group.rg.*.location, [""]), 0)
 }

 provider "azurerm" {
  features {
  }
}


data "azurerm_resource_group" "rgrp" {
  count = var.create_resource_group ? 0 : 1
  name  = var.resource_group_name
}

resource "azurerm_resource_group" "rg" {
  count    = var.create_resource_group ? 1 : 0
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}


data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

resource "azurerm_traffic_manager_profile" "profile" {
  name                = var.profilename
  resource_group_name = local.resource_group_name
  traffic_routing_method = var.traffic_routing
  profile_status = "Enabled"

  dns_config {
    relative_name = var.dnsrelativename
    ttl           = 100
  }


 monitor_config {
    protocol                     = var.protocol
    port                         = var.port
    path                         = var.path
    interval_in_seconds          = var.interval
    timeout_in_seconds           = var.timeout
    tolerated_number_of_failures = var.failures
  }
}

resource "random_id" "numberid" {
  keepers = {
    azi_id = 1
  }

  byte_length = 8
}

resource "azurerm_traffic_manager_endpoint" "endpoint" {
  name                = var.endpointname
  resource_group_name = local.resource_group_name
  profile_name        = azurerm_traffic_manager_profile.profile.name
  # target              = var.targeturl
  type                = var.endpointtype
  target_resource_id  = var.target_resource_id 
  weight              = 100
}

module "monitoring" {
  source = "../Diagnostic_module"
  name = azurerm_traffic_manager_profile.profile.name
  resource_id = azurerm_traffic_manager_profile.profile.id
}

data "azurerm_monitor_action_group" "ag" {
  name = "BaselineActionGroup"
  resource_group_name = local.resource_group_name
}




































# resource "azurerm_monitor_activity_log_alert" "main" {
#   name                = "example-activitylogalert"
#   resource_group_name = local.resource_group_name
#   scopes              = [azurerm_traffic_manager_profile.profile.id]
#   description         = "This alert will monitor a specific storage account updates."

#   criteria {
#     resource_id    = azurerm_traffic_manager_profile.profile.id
#     operation_name = "Microsoft.Network/trafficManagerProfiles"
#     # Supported operation names include Microsoft.Network/register/action, Microsoft.Network/unregister/action, Microsoft.Network/bgpServiceCommunities/read, Microsoft.Network/locations/virtualNetworkAvailableEndpointServices/read, Microsoft.Network/locations/availableDelegations/read, Microsoft.Network/locations/serviceTags/read, Microsoft.Network/locations/availablePrivateEndpointTypes/read, Microsoft.Network/locations/availableServiceAliases/read, Microsoft.Network/locations/supportedVirtualMachineSizes/read, Microsoft.Network/locations/checkAcceleratedNetworkingSupport/action, Microsoft.Network/locations/autoApprovedPrivateLinkServices/read, 
#     # Microsoft.Network/locations/batchValidatePrivateEndpointsForResourceMove/action, Microsoft.Network/locations/batchNotifyPrivateEndpointsForResourceMove/action, Microsoft.Network/locations/checkPrivateLinkServiceVisibility/action, Microsoft.Network/privateEndpoints/pushPropertiesToResource/action, Microsoft.Network/locations/validateResourceOwnership/action, Microsoft.Network/locations/setResourceOwnership/action, Microsoft.Network/locations/effectiveResourceOwnership/action, Microsoft.Network/locations/setAzureNetworkManagerConfiguration/action, Microsoft.Network/locations/getAzureNetworkManagerConfiguration/action"
#     category       = "Recommendation"
#   }

#   action {
#     action_group_id = data.azurerm_monitor_action_group.ag.id

#     webhook_properties = {
#       from = "terraform"
#     }
#   }
# }