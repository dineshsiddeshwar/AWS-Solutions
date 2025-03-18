resource "azurerm_resource_group" "rg" {
  name     = "${var.prefix}baseline-Demo"
  location = var.location
}
#Testing Commit after changes in TFE1
module "vnet" {
  # source = "git::https://HitenderSaxena0816@dev.azure.com/HitenderSaxena0816/Secure%20Baseline%20Coding/_git/azure_network"
  source = "../Modules/Network_module"
  # create_resource_group = true
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  vnet_name           = "baseline-vnet"
  address_space       = ["172.19.0.0/16"]
  create_ddos_plan    = true
  storage_account_name = "eygdsnetworkstorage"

  firewall_subnet_address_prefix = var.firewall_subnet_address_prefix
  gateway_subnet_address_prefix  = var.gateway_subnet_address_prefix
  subnet_prefixes                = var.subnet_prefixes
  subnet_names                   = var.subnet_names

  subnet_service_endpoints = {
    subnet1 = ["Microsoft.KeyVault", "Microsoft.Storage", "Microsoft.Sql"],
    subnet2 = ["Microsoft.KeyVault", "Microsoft.Storage", "Microsoft.Sql"],
    subnet3 = ["Microsoft.KeyVault", "Microsoft.Storage", "Microsoft.Sql", "Microsoft.AzureActiveDirectory"],
    app_gateway = ["Microsoft.KeyVault", "Microsoft.Storage", "Microsoft.Sql"],
  }

  subnet_enforce_private_link_endpoint_network_policies = {
    subnet3 = "true"
  }

  subnet_enforce_private_link_service_network_policies = {
    subnet1 = "true"
    subnet2 = "true"
  }

  # delegation = {
  #   subnet1 = {
  #         name = "testdelegation"
  #         service_delegation = {
  #           name    = "Microsoft.ContainerInstance/containerGroups"
  #           actions = "Microsoft.Network/virtualNetworks/subnets/join/action,Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action"
  #       }
  #     }
  # }

  nsg_ids = {
    # subnet1 = azurerm_network_security_group.ssh.id
    subnet2 = azurerm_network_security_group.ssh.id
    subnet3 = azurerm_network_security_group.ssh.id
  }

  route_tables_ids = {
    subnet1 = azurerm_route_table.rtable.id
    subnet2 = azurerm_route_table.rtable.id
    subnet3 = azurerm_route_table.rtable.id
    app_gateway = azurerm_route_table.rtable.id
  }

  tags = {
    environment = "dev"
    Department  = "EYDGS"
  }

  depends_on = [azurerm_resource_group.rg]
}

resource "azurerm_network_security_group" "ssh" {
  name                = "ssh"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  security_rule {
    name                       = "deny_ssh"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_route_table" "rtable" {
  name                = "baseline-vnet-internal-route"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  lifecycle {
    create_before_destroy = true
  }
}

resource "azurerm_route" "route" {
  count = length(var.subnet_names)
  name                = "Route-To-${var.subnet_names[count.index]}"
  resource_group_name = azurerm_resource_group.rg.name
  route_table_name    = azurerm_route_table.rtable.name
  address_prefix      = var.subnet_prefixes[count.index]
  next_hop_type       = "vnetlocal"
}
