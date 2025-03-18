######################################################################################################################################################################
############################################################       REQUIREMENTS SECTION        #######################################################################
######################################################################################################################################################################

#  Ensure All the Hub Virtual networks are peered with Virtual network gateway subnet to connect Azure ExpressRoute - INVALIDATED
#  Ensure no public IP's used within the Azure tenant - NOTE: Please choose one of the below configurations depenging on the scope where Policy will apply ! 
# Management Group Scope 
/* resource "azurerm_management_group_policy_assignment" "example" { 
 name = var.az_policy_name # Required argument 
 management_group_id = var.cust_scope # Required argument
 policy_definition_id = var.az_policy_id # Required argument
 description = var.az_policy_description # Optional argument
 display_name = var.az_policy_name # Optional argument
}

# Subscription Scope 
resource "azurerm_subscription_policy_assignment" "example" { 
 name = var.az_policy_name # Required argument 
 subscription_id = var.cust_scope # Required argument
 policy_definition_id = var.az_policy_id # Required argument
 description = var.az_policy_description # Optional argument
 display_name = var.az_policy_name # Optional argument
} */

# Resource Group Scope 
resource "azurerm_resource_group_policy_assignment" "example" { 
 name = var.az_policy_name # Required argument 
 resource_group_id = var.cust_scope # Required argument
 policy_definition_id = var.az_policy_id # Required argument
 description = var.az_policy_description # Optional argument
 display_name = var.az_policy_name # Optional argument
}
/*
# Individual Resource Scope 
resource "azurerm_resource_group_policy_assignment" "example" { 
 name = var.az_policy_name # Required argument 
 resource_id = var.cust_scope # Required argument
 policy_definition_id = var.az_policy_id # Required argument
 description = var.az_policy_description # Optional argument
 display_name = var.az_policy_name # Optional argument
} */

#  Ensure each applications is segmented with spoke Virtual network and spoke VNet connected to Hub network
resource "azurerm_virtual_network_peering" "example-2" {
  name                      = var.hubToSpoke_peering_name ############## (1/2) Peer hub vnet to spoke vnet !
  resource_group_name       = var.resource_group.name
  virtual_network_name      = var.vnet_name
  remote_virtual_network_id = var.spoke_vnet_id
  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
  allow_gateway_transit = true # or false
}

resource "azurerm_virtual_network_peering" "example-1" {
  name                      = var.spoketoHub_peering_name ############## (2/2) Peer spoke vnet to hub vnet !
  resource_group_name       = var.resource_group.name
  virtual_network_name      = var.spoke_vnet_name
  remote_virtual_network_id = var.hub_vnet_id
  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
  allow_gateway_transit = true # or false
}

#  Ensure each subnet has NSG attached to it
resource "azurerm_subnet_network_security_group_association" "example" {
  subnet_id                 = var.subnet_id
  network_security_group_id = var.nsg_id
}

#  Ensure only VNet peering is allowed for VNet to VNet connection (Removed - Redundant with another Requirement )

# Ensure VNet administrative tasks leverage Role Based Access Control
resource "azurerm_role_assignment" "example" {
  scope                = var.rbac_role_assignment_scope # Required argument (The scope at which the Role Assignment applies to)
  role_definition_name = var.rbac_role_name # Required argument (The name of a Built-in or Custom role)
  principal_id         = var.rbac_principal_id # Required argument (User, Group or Service Principal ID, AKA Object ID)
}

# Ensure VMProtectionAlerts is enabled for virtual network using Diagnostic logging
resource "azurerm_monitor_diagnostic_setting" "example" {
  name               = var.vnet-diagsetting_name # Required argument
  target_resource_id = var.vnet_diagtarget_id # Required argument (Source of log data)
  log_analytics_workspace_id = var.log_dump_resource_id # Optional argument (Destination for log data. It can be one of the follwing: storage_account_id, log_analytics_workspace_id, eventhub_name)

  log {
    category = var.vnet_log_category
     
     retention_policy {
      enabled = true
      days = var.log_retention_days  # Retention duration only applies if log destination is of a type storage_account_id
    }
  }
}

#  Ensure administrative tasks are performed only in admin-e workstations (Removed - Not applicable to this service)

# Ensure that virtual network uses standard organizational Resource tagging method
resource "azurerm_virtual_network" "vnet" {
 # provider = azurerm.othersubscription #<-------  Ensure that Dev/UAT/Prod Hub and spoke VNets are logically separated using azure subscription
  name = var.vnet_name
  address_space = var.address_space
  location = var.resource_group.location
  resource_group_name = var.resource_group.name
    subnet {
      address_prefix = var.subnet.iprange
      name = var.subnet.name
    } 
    tags = { #<-------  Ensure that virtual network uses standard organizational Resource tagging method
      cost_center = var.cost_center
      ppmc_id = var.ppmc_id
      toc = var.toc
      usage_id = var.usage_id
      env_type = var.env_type
      exp_date = var.exp_date
      endpoint = var.endpoint
      sd_period = var.sd_period
    }
} 