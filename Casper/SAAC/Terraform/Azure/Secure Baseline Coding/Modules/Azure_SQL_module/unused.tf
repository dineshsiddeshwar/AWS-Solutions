# #-----------------------------------------------------------------------------------------------
# # Create and initialize a Microsoft SQL Server database using sqlcmd utility - Default is "false"
# #-----------------------------------------------------------------------------------------------

# # resource "null_resource" "create_sql" {
# #   count = var.initialize_sql_script_execution ? 1 : 0
# #   provisioner "local-exec" {
# #   command = "sqlcmd -I -U ${azurerm_sql_server.primary.administrator_login} -P ${azurerm_sql_server.primary.administrator_login_password} -S ${azurerm_sql_server.primary.fully_qualified_domain_name} -d ${azurerm_sql_database.db.name} -i ${var.sqldb_init_script_file} -o ${format("%s.log", replace(var.sqldb_init_script_file, "/.sql/", ""))}"
# #   } 
# # }

# #-----------------------------------------------------------------------------------------------
# # Adding AD Admin to SQL Server - Secondary server depend on Failover Group - Default is "false"
# #-----------------------------------------------------------------------------------------------

# # data "azurerm_client_config" "current" {}

# # resource "azurerm_sql_active_directory_administrator" "aduser1" {
# #     count                   = var.enable_sql_ad_admin ? 1 : 0
# #     server_name             = azurerm_sql_server.primary.name
# #     resource_group_name     = local.resource_group_name
# #     login                   = var.ad_admin_login_name
# #     tenant_id               = data.azurerm_client_config.current.tenant_id
# #     object_id               = data.azurerm_client_config.current.object_id
# # }

# # resource "azurerm_sql_active_directory_administrator" "aduser2" {
# #     count                   = var.enable_failover_group && var.enable_sql_ad_admin ? 1 : 0
# #     server_name             = azurerm_sql_server.secondary.0.name
# #     resource_group_name     = local.resource_group_name
# #     login                   = var.ad_admin_login_name
# #     tenant_id               = data.azurerm_client_config.current.tenant_id
# #     object_id               = data.azurerm_client_config.current.object_id
# # }

# #---------------------------------------------------------
# # Private Link for SQL Server - Default is "false" 
# #---------------------------------------------------------

# data "azurerm_virtual_network" "vnet01" {
#     name                    = var.virtual_network_name
#     resource_group_name     = local.resource_group_name
# }

# resource "azurerm_subnet" "snet-ep" {
#     count                   = var.enable_private_endpoint ? 1 : 0
#     name                    = "snet-endpoint-shared-${local.location}"
#     resource_group_name     = local.resource_group_name
#     virtual_network_name    = var.virtual_network_name
#     address_prefix          = var.private_subnet_address_prefix
#     enforce_private_link_endpoint_network_policies = true
# }

# resource "azurerm_private_endpoint" "pep1" {
#     count                   = var.enable_private_endpoint ? 1 : 0
#     name                    = format("%s-primary", "sqldb-private-endpoint")
#     location                = local.location
#     resource_group_name     = local.resource_group_name
#     subnet_id               = azurerm_subnet.snet-ep.0.id
#     tags                    = var.tags

#     private_service_connection {
#         name                           = "sqldbprivatelink"
#         is_manual_connection           = false
#         private_connection_resource_id = azurerm_sql_server.primary.id
#         subresource_names              = ["sqlServer"]
#     }
# }

# resource "azurerm_private_endpoint" "pep2" {
#     count                   = var.enable_failover_group && var.enable_private_endpoint ? 1 : 0
#     name                    = format("%s-secondary", "sqldb-private-endpoint")
#     location                = local.location
#     resource_group_name     = local.resource_group_name
#     subnet_id               = azurerm_subnet.snet-ep.0.id
#     tags                    = var.tags

#     private_service_connection {
#         name                           = "sqldbprivatelink"
#         is_manual_connection           = false
#         private_connection_resource_id = azurerm_sql_server.secondary.0.id
#         subresource_names              = ["sqlServer"]
#     }
# }

# # #------------------------------------------------------------------
# # # DNS zone & records for SQL Private endpoints - Default is "false" 
# # #------------------------------------------------------------------

# data "azurerm_private_endpoint_connection" "private-ip1" {
#     count                   = var.enable_private_endpoint ? 1 : 0    
#     name                    = azurerm_private_endpoint.pep1.0.name
#     resource_group_name     = local.resource_group_name
#     depends_on              = [azurerm_sql_server.primary]
# }

# data "azurerm_private_endpoint_connection" "private-ip2" {
#     count                   = var.enable_failover_group && var.enable_private_endpoint ? 1 : 0
#     name                    = azurerm_private_endpoint.pep2.0.name
#     resource_group_name     = local.resource_group_name
#     depends_on              = [azurerm_sql_server.secondary]
# }

# resource "azurerm_private_dns_zone" "dnszone1" {
#     count                   = var.enable_private_endpoint ? 1 : 0
#     name                    = "privatelink.database.windows.net"
#     resource_group_name     = local.resource_group_name
#     tags                    = var.tags
# }

# resource "azurerm_private_dns_zone_virtual_network_link" "vent-link1" {
#     count                   = var.enable_private_endpoint ? 1 : 0
#     name                    = "vnet-private-zone-link"
#     resource_group_name     = local.resource_group_name
#     private_dns_zone_name   = azurerm_private_dns_zone.dnszone1.0.name
#     virtual_network_id      = data.azurerm_virtual_network.vnet01.id
#     tags                    = var.tags
# }

# resource "azurerm_private_dns_a_record" "arecord1" {
#     count                   = var.enable_private_endpoint ? 1 : 0
#     name                    = azurerm_sql_server.primary.name
#     zone_name               = azurerm_private_dns_zone.dnszone1.0.name
#     resource_group_name     = local.resource_group_name
#     ttl                     = 300
#     records                 = [data.azurerm_private_endpoint_connection.private-ip1.0.private_service_connection.0.private_ip_address]
# }

# resource "azurerm_private_dns_a_record" "arecord2" {
#     count                   = var.enable_failover_group && var.enable_private_endpoint ? 1 : 0
#     name                    = azurerm_sql_server.secondary.0.name
#     zone_name               = azurerm_private_dns_zone.dnszone1.0.name
#     resource_group_name     = local.resource_group_name
#     ttl                     = 300
#     records                 = [data.azurerm_private_endpoint_connection.private-ip2.0.private_service_connection.0.private_ip_address]

# }

# # # Configure the Microsoft Azure Provider
# # provider "azurerm" {
# #   features {}
# # }

# #  resource "azurerm_resource_group" "rgsqlserver" {

# # #   name     = "rg-for-azure-sqlserver"
# #   name = var.resource_group_name
# #   location = "East US"

# # } 

# resource "random_string" "random-name" {
#   length  = 5
#   upper   = false
#   lower   = true
#   number  = true
#   special = false
# }

#   module "diagnostic" {
#   source                     = "../Secure_Baseline_Coding/Modules/Diagnostic_module"
#   name                       = "eygdssec_common"
#   resource_id                = data.azurerm_sql_server.azuresqlserver.id
#   # log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
# }   


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