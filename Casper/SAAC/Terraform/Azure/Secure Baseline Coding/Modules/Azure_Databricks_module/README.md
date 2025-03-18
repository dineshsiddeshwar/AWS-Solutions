# Azure Databricks workspace
## Example on how to use this module.

> [!NOTE]
> This module is used to create the Azure Databricks workspace.


Reference the module to a specific version (recommended):

```terraform
module "azdatabricks" {

  source                 = "../Modules/Azure_Databricks_module"
  settings_name          = "eytest-databricksws"
  global_settings_prefix = ["a", "b"]
  random_length          = 5

  resource_group_name         = "EYGDSSECbaseline-rg"
  location                    = "eastus"
  sku                         = "standard"
  managed_resource_group_name = "managed_resource_group_name"
  tags                        =  {
    Department  = "EYGDSSEC"
    Environment = "Dev"
  }


  custom_parameters = [{

    no_public_ip        = false
    public_subnet_name  = "public_subnet_name"
    private_subnet_name = "private_subnet_name"
    virtual_network_id  = "virtual_network_id"

  }]


}
```



