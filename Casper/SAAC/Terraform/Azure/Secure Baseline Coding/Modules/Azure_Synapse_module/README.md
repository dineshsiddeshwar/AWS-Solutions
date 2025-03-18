# Azure Synapse Analytics
## Example on how to use this module.

> [!NOTE]
> This module is to create the Azure Synapse workspace along with a SQL pool with the diagnostic settings enabled.

Reference the module to a specific version (recommended):


```terraform
module "azsynapse" {

  source        = "../Modules/Azure_Synapse_module"
  resource_group_name = "GDSSECbaseline-rg"
  datalake_name = "storage-datalake"
  synapse_name  = "baseline-synapse"

  adminlogin    = "admin_login"
  adminpassword = "admin_password"
  tags          = {
    Department  = "EYGDSSEC"
    Environment = "Dev"
  }

  synapse_sql_pool = "synapsesqlpool"
  #   sql pool

  firewallrule     = "AllowAzureServices"
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"

  # storage_acc_id     = "storage_acc_id"
  storage_account_name= "gdsbaselinedatalake"
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "BlobStorage"

  endpoint_name    = "test-endpoint"
  subresource_name = "blob"

  synapse_role = "Sql Admin"
  
  synapse_spark_pool = {
    sql_pool_1 = {}
  }
}
```

#### Example variable definition.

**Synapse spark pools**
```terraform 
synapse_spark_pool = {
      spark_pool_name = "testpool"
      node_size_family = "MemoryOptimized"
      node_size = "Small"
      node_count = 3
      
      auto_scale = [{
        max_node_count = 5
        min_node_count = 3
      }]

      auto_pause = [{
        delay_in_minutes = 5
      }]
    }
```

**Autoscale Configuration**
```terraform 
auto_scale = {
      max_node_count = 5
      min_node_count = 1
    }
```