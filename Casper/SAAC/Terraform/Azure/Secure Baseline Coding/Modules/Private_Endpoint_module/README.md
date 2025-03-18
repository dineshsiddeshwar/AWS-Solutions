# Priavate Endpoint Module

This module creates the following resources.
- private_endpoint
- private_dns_zone
- private_dns_zone_virtual_network_link
- private_dns_a_record

**Example of using this module to create Private endpoint, dns zone, vnet link and a record.**

```terraform
module "firstendpoint" {
  source                = "../Modules/Private_Endpoint_module"
  resource_group_name   = "EYGDSSECbaseline-rg"
  name                  = <private endpoint name>
  resource_id           = <resource id>
  subresource_names     = ["sqlserver"]
  private_dns_zone_name = "privatelink.sqlcore.azure.net"
  vnet_id               = data.terraform_remote_state.vpc.outputs.vnet_id
  tags                  = var.tags
}
``` 

**Example of using this module to create Private endpoint, 'A record' and use existing dns zone.**

```terraform
module "secondendpoint" {
  source                = "../Modules/Private_Endpoint_module"
  resource_group_name   = "EYGDSSECbaseline-rg"
  name                  = <private endpoint name>
  resource_id           = <resource id>
  subresource_names     = ["sqlserver"]
  private_dns_zone_name = "privatelink.sqlcore.azure.net"
  create_private_dns_zone = false
  tags                  = var.tags
}
```
