# README for Traffic Manager
## Example on how to use this module.

> [!NOTE]
> This module is to create the Azure Traffic Manager profile and endpoint along with the diagnostic settings enabled on the Traffic manager profile.

Reference the module to a specific version (recommended):

```terraform
module "traffic_mgr" {
source              = "../Modules/traffic_mgr"
resource_group_name   = "EYGDSSECbaseline-rg"
tags = {
    Department  = "EYGDSSEC"
    Environment = "Dev"
  }
location = "useast"
profilename = "test-tmprofile"
traffic_routing = "Performance"

protocol = "HTTPS"
port = 443
path = "/"
interval = 30
timeout = 10
failures = 3

endpointname = "test-endpoint"
targeturl = var.targeturl
target_resource_id  = "/subscriptions/2deda99b-1d35-4ee1-a4ce-aa5a3875266a/resourcegroups/EYGDSSECbaseline-rg/providers/Microsoft.Web/sites/test-webapp2604"
endpointtype = "azureEndpoints"

}
```

###Example variable
**Monitor configuration**
```terraform
monitor_config = [{
    protocol                     = "HTTPS"
    port                         = 443
    path                         = "/"
    interval_in_seconds          = 30
    timeout_in_seconds           = 10
    tolerated_number_of_failures = 3
  }]


```
