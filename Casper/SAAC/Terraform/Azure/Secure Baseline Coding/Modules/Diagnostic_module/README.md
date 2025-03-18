***Deploys diagnostics settings for an Azure resource***

Deploys the diagnostics settings for an already existing Azure resource

Reference the module to a specific version (recommended):

```terraform
module "diagnostics" {
    source  = "xxx/yyy/Diagnostic_module"
    version = "0.x.y"

    name                              = var.name
    resource_id                       = var.resource_id
    eh_map                            = var.eh_map                -> Optional
    log_analytics_workspace_id        = var.laworkspaceid         -> Optional, if a value is not provided, default value will be used.
    storage_account_id                = var.storage_account_id    -> Optinoal, if a value is not provided, default value will be used.
}
```

**Parameters**

**name**

(Required) name of the diagnostics object (will be appended with -diag)

```terraform
variable "name" {
  description = "(Required) Name of the diagnostics object."
  type = string
}
```

Example

`name = "vnet"`

**resource_id**

(Required) (Required) fully qualified Azure resource identifier for which you enable diagnostics.

```terraform
variable "resource_id" {
  description = "(Required) Fully qualified Azure resource identifier for which you enable diagnostics."
  type = string
}
```

Example

```terraform
resource_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/uqvh-hub-operations/providers/Microsoft.              RecoveryServices/vaults/asr-edo"
```

**log_analytics_workspace_id**

(Optional) contains the log analytics workspace details for operations diagnostics."

```terraform
variable "log_analytics_workspace_id" {
  description = "(Optional) contains the log analytics workspace details for operations diagnostics"
  type = string
}
```
    

Example

```terraform
  log_analytics_workspace_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/operations-rg/providers/microsoft.operationalinsights/workspaces/lalogs"
```

**eh_map**

(Required) Map with the diagnostics repository information"

```terraform
variable "eh_map" {
  description = "(Optional) Map with the diagnostics repository information"
  type = map(string)
}
```

**Example**

```terraform
eh_map = {
      #Event Hub is optional 
      eh_id         = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/arnaud-hub-operations/providers/Microsoft.EventHub/namespaces/opslogskumowxv"
      eh_name       = "opslogskumowxv"
  }
```

**Outputs**

|Name  |Type  |Description  |
|---------|---------|---------|
|object   | object  | Returns the created diagnostics object        |
|name     | string  | Returns the name created diagnostics object   |
|id       | string  | Returns the ID the created diagnostics object |
		

