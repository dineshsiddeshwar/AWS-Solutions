resource "azurerm_resource_group" "demo" {
  name     = "${var.prefix}-rg"
  location = var.location
}

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

resource "azurerm_kubernetes_cluster" "demo" {
  name                = "${var.prefix}-aks"
  location            = azurerm_resource_group.demo.location
  resource_group_name = azurerm_resource_group.demo.name
  dns_prefix          = "${var.prefix}-aks"
  private_cluster_enabled = true
  api_server_authorized_ip_ranges = var.authorized_ip_range
  enable_host_encryption = true
  role_based_access_control = enabled

  default_node_pool {
    name                = "default"
    node_count          = var.nodes_count
    vm_size             = "Standard_D2_v2"
    type                = "VirtualMachineScaleSets"
    availability_zones  = ["1", "2"]
    enable_auto_scaling = true
    min_count           = var.vmss_min_count
    max_count           = var.vmss_max_count
	

    # Required for advanced networking
    vnet_subnet_id = azurerm_subnet.demo.id
  }

  # identity {
  #   type = "SystemAssigned"
  # }

  # role_based_access_control {
  #   azure_active_directory {
  #     client_app_id     = var.client_app_id
  #     server_app_id     = var.server_app_id
  #     server_app_secret = var.server_app_secret
  #     tenant_id         = var.tenant_id
  #   }
  #   enabled = true
  # }

  
#service_principal {
#    client_id     = var.app_id
#    client_secret = var.password
#  }

  role_based_access_control {
    enabled = true
  }

  network_profile {
    network_plugin    = "azure"
    load_balancer_sku = "standard"
    network_policy    = "calico"
  }

  tags = {
    Environment = var.environment
  }
}

resource "azurerm_advanced_threat_protection" "example" {
  target_resource_id = azurerm_kubernetes_cluster.demo.id
  enabled            = true
}