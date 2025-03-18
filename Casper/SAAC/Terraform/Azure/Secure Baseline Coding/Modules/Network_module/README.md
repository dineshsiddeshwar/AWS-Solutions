# Azure Network Module

> [!NOTE]
> This module does not create NSG, Route table and routes, but you can create them and pass the NSG/ Route table ids to be associatged with the subnets created by the module.

> [!NOTE]
> It is expected that the nsg resources are created before calling this module. Use `terraform apply -target=resource` to explicitly create the nsg resources first.

## Example on how to use this module.

```terraform
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

  depends_on = [azurerm_resource_group.rg, azurerm_route_table.rtable, azurerm_network_security_group.ssh]
}
```
