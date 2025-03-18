resource "azurerm_resource_group" "demo" {
  name     = "${var.prefix}-rg"
  location = var.location
}

module "vnet" {
  # source = "git::https://HitenderSaxena0816@dev.azure.com/HitenderSaxena0816/Secure%20Baseline%20Coding/_git/azure_network"
  source = "../Modules/Network_module"
  # create_resource_group = true
  resource_group_name = azurerm_resource_group.demo.name
  location            = azurerm_resource_group.demo.location
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

  depends_on = [azurerm_resource_group.demo]
}

resource "azurerm_network_security_group" "ssh" {
  name                = "ssh"
  resource_group_name = azurerm_resource_group.demo.name
  location            = azurerm_resource_group.demo.location

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

resource "azurerm_network_interface" "main" {
  name                = "${var.prefix}-nic"
  location            = azurerm_resource_group.demo.location
  resource_group_name = azurerm_resource_group.demo.name

  ip_configuration {
    name                          = "testconfiguration1"
    subnet_id                     = azurerm_subnet.demo.id
    private_ip_address_allocation = "Dynamic"
  }
}
resource "azurerm_virtual_machine" "main" {
  name                  = "${var.prefix}-vm"
  location              = azurerm_resource_group.demo.location
  resource_group_name   = azurerm_resource_group.demo.name
  network_interface_ids = [azurerm_network_interface.main.id]
  vm_size               = "Standard_DS1_v2"

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "16.04-LTS"
    version   = "latest"
  }
  storage_os_disk {
    name              = "myosdisk1"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Standard_LRS"
  }
  os_profile {
    computer_name  = "hostname"
    admin_username = "testadmin"
    admin_password = "Password1234!"
  }
  os_profile_linux_config {
    disable_password_authentication = false
  }
  tags = {
    environment = var.environment
  }
}

# Azure SQl server

module "sqlserver" {

  source              = "../Modules/Azure_SQL_module"
  resource_group_name = azurerm_resource_group.demo.name
  tags                = var.tags

  primary_sqlserver_name = "baseline-azuresql"
  admin_login    = "admin_login"
  admin_password = "admin_password"
  enable_failover_group = true
  secondary_sql_server_location = "westus"

  database_name = "eygdssec-sqldb-test"
  enable_firewall_rules        = true
  firewall_rules               = [{
    name             = "Allow access to Azure services"
    start_ip_address = "0.0.0.0"
    end_ip_address   = "0.0.0.0"
  }]
  enable_auditing_policy = true

  storage_account_name     = "dbstoragetest1"
}

