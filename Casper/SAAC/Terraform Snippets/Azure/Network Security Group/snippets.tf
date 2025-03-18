######################################################################################################################################################################
############################################################       REQUIREMENTS SECTION        #######################################################################
######################################################################################################################################################################

# Run the following in terminal: terraform import azurerm_network_security_group.main /subscriptions/xxxx-xxxxx-xxxxxxx/resourceGroups/example-rg/providers/Microsoft.Compute/disks/examplenetworksecuritygroup (to import already existing NSG resource to Terraform state file, in order for Terraform to be able to modify it) !

resource "azurerm_network_security_group" "example" {
  name                = var.network_security_group_name1
  location            = var.resource_group_location
  resource_group_name = var.resource_group_name
                                                                   #  Ensure Service tags are enabled for the network security group
  dynamic "security_rule" {                                        #  Ensure Explicit Deny rules are defined with higher priority value in NSG to override the allow rules
    for_each = var.nsg_rules
    content {
      name                       = security_rule.value["name"]
      priority                   = security_rule.value["priority"]
      direction                  = security_rule.value["direction"]
      access                     = security_rule.value["access"]
      protocol                   = security_rule.value["protocol"]
      source_port_range          = security_rule.value["source_port_range"]
      destination_port_range     = security_rule.value["destination_port_range"]
      source_address_prefix      = security_rule.value["source_address_prefix"]
      destination_address_prefix = security_rule.value["destination_address_prefix"]
    }
  }
  tags = { #<------ # Ensure that virtual network uses standard organizational Resource tagging method
    cost_center = var.cost_center
    ppmc_id     = var.ppmc_id
    toc         = var.toc
    usage_id    = var.usage_id
    env_type    = var.env_type
    exp_date    = var.exp_date
    endpoint    = var.endpoint
    sd_period   = var.sd_period
  }
}

#  Ensure each Subnet and Network interface should be associated with Network Security Group

resource "azurerm_network_interface_security_group_association" "example" { # Enables NIC with network security group association.
  network_interface_id      = var.network_interface_id
  network_security_group_id = azurerm_network_security_group.example.id
}

resource "azurerm_subnet_network_security_group_association" "example" { # Enables subnet with network security group association.
  subnet_id                 = var.subnet_id
  network_security_group_id = azurerm_network_security_group.example.id
}

#  Ensure Application security group(ASG) is combined with NSG to filter network traffic for a fleet of VMs

resource "azurerm_application_security_group" "example" { # If ASG is not already created, please use this code for creation
  name                = var.application_security_group_name
  location            = var.resource_group_location
  resource_group_name = var.resource_group_name
}

resource "azurerm_network_security_rule" "example" {
  name                   = var.name_asg
  priority               = var.priority_asg
  direction              = var.direction_asg
  access                 = var.access_asg
  protocol               = var.protocol_asg
  source_port_range      = var.source_port_range_asg
  destination_port_range = var.destination_port_range_asg
  source_address_prefix  = var.source_address_prefix_asg
  resource_group_name                        = var.resource_group_name
  network_security_group_name                = var.network_security_group_name1
  destination_application_security_group_ids = [azurerm_application_security_group.example.id] # id of the destination ASG 
}

#  Ensure NSG implements Role Based Access Control

resource "azurerm_role_assignment" "example" {
  scope              = azurerm_network_security_group.example.id # Required argument (The scope at which the Role Assignment applies to)
  principal_id       = var.rbac_principal_id                     # Required argument (User, Group or Service Principal ID, AKA Object ID)
  role_definition_id = var.role_definition_id
}

# Ensure Diagnostic logs are enabled for Azure NSG

resource "azurerm_eventhub_namespace" "example" {   #Assuming that eventhub namespace is not currently present
  name                = var.eventhub_namespace_name # Your value
  location            = var.resource_group_location
  resource_group_name = var.resource_group_name
  sku                 = var.sku
  capacity            = var.capacity

}

resource "azurerm_eventhub_namespace_authorization_rule" "example" { # Setting authorizational rule
  name                = var.eventhub_namespace_authorization_rule_name
  namespace_name      = azurerm_eventhub_namespace.example.name
  resource_group_name = var.resource_group_name
  listen = var.listen
  send   = var.send
  manage = var.manage
}


resource "azurerm_monitor_diagnostic_setting" "example" {
  name                           = var.vnet-diagsetting_name                 # Required argument
  target_resource_id             = azurerm_network_security_group.example.id # Required argument (Source of log data)
  eventhub_authorization_rule_id = azurerm_eventhub_namespace_authorization_rule.example.id
  log {
    category = var.vnet_log_category

    retention_policy {
      enabled = true
      days    = var.log_retention_days # Retention duration only applies if log destination is of a type storage_account_id
    }
  }
  log {
    category = var.vnet_log_category1

    retention_policy {
      enabled = true
      days    = var.log_retention_days # Retention duration only applies if log destination is of a type storage_account_id
    }
  }
}


#  Ensure all the NSG has NSG flow log data enabled using Network Watcher

resource "azurerm_network_watcher" "test" {
  name                = var.network_watcher_name 
  location            = var.resource_group_location
  resource_group_name = var.resource_group_name
}

resource "azurerm_network_watcher_flow_log" "test" {
  network_watcher_name      = azurerm_network_watcher.test.name
  resource_group_name       = var.resource_group_name
  name                      = var.network_watcher_flow_log_name
  network_security_group_id = azurerm_network_security_group.example.id
  storage_account_id        = var.storage_account_id
  enabled                   = true

  retention_policy {
    enabled = true
    days    = var.log_retention_days
  }

  traffic_analytics {
    enabled               = true
    workspace_id          = var.workspace_id
    workspace_region      = var.workspace_region
    workspace_resource_id = var.workspace_resource_id
    interval_in_minutes   = var.interval_in_minutes
  }
}



