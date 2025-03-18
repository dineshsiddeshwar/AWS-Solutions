# Azure SQL Server
## Example on how to use this module.


This module is used to create the Azure SQL server with features like failover groups and private endpoints.

Reference the module to a specific version (recommended):


```terraform
module "sqlserver" {

  source              = "../Modules/Azure_SQL_module"
  resource_group_name = "EYGDSSECbaseline-rg"
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
```

**Example for implementing private endpoint for primary SQL server**

```terraform
module "primaryendpoint" {
  source                = "../Modules/Private_Endpoint_module"
  resource_group_name   = "EYGDSSECbaseline-rg"
  name                  = "primaryendpoint"
  resource_id           = "endpointresourceid"
  subresource_names     = ["sqlserver"]
  private_dns_zone_name = "privatelink.sqlcore.azure.net"
  vnet_id               = "vnetwork_id"
  tags                  = { 
    Department  = "EYGDSSEC"
    Environment = "Dev" 
  }
}
```
**Example for implementing second private endpoint for  SQL server**

```terraform
module "secondendpoint" {
  source                = "../Modules/Private_Endpoint_module"
  resource_group_name   = "EYGDSSECbaseline-rg"
  name                  = "secondary_endpoint"
  resource_id           = <"endpointresourceid">
  subresource_names     = ["sqlserver"]
  private_dns_zone_name = "privatelink.sqlcore.azure.net"
  create_private_dns_zone = false
  tags                  = { 
    Department  = "EYGDSSEC"
    Environment = "Dev" 
  }
}
```

**Example variable definition.**

```terraform
 firewall_rules = {
    name             = "firewall_rule_inbound"
    start_ip_address = "0.0.0.0"
    end_ip_address   = "0.0.0.0"
  }

```




