# Azure Key Vault Module

> [!NOTE]
> This module has rbac_authorization enabled by default, which is the advised approach. If you disable rbac_authorization, then the module will create a reader and admin vault access policy, if you pass in the list of reader and admin object ids as inputs.


**Below is an example of how to use this module.**


```terraform
module "vault" {
  source              = "../Modules/Vault_module"
  vault_name          = <vault-name>
  resource_group_name = "EYGDSSECbaseline-rg"
  sku_name            = "premium"
  reader_objects_ids  = [list of object ids]
  admin_objects_ids   = [list of object ids]
  enable_rbac_authorization    = false
  enabled_for_deployment = true
  

  network_acls = [
    {
      bypass                     = "AzureServices",
      default_action             = "Deny",
      ip_rules                   = [],
      virtual_network_subnet_ids = toset(<list of subnets>)
    }
  ]

  contact = [
    {
      email = "vignesh.seethapathy@gds.ey.com"
      name  = "Vignesh Seethapathy"
      phone = "1234567890"
    }
  ]

  tags = var.tags
}
```

