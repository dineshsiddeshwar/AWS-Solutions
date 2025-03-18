# Private Link Service

> [!NOTE]
> Verify that the Subnet's enforce_private_link_service_network_policies attribute is set to true.

> [!NOTE]
> If no visibility_subscription_ids are specified then Azure allows every Subscription to see this Private Link Service.

Example of using the private link service module

```terraform
module "plink_svc" {
  plink_name = "test-service-plink"
  resource_group_name = "EYGDSSECbaseline-rg"
  auto_approval_subscription_ids              = [A list of Subscription UUID/GUID's]
  visibility_subscription_ids                 = [A list of Subscription UUID/GUID's]
  load_balancer_frontend_ip_configuration_ids = [A list of Frontend IP Configuration ID's from a Standard Load Balancer]
  enable_proxy_protocol                       = true

  nat_ip_config = [
    "nat-ip-config-name", 
    "10.0.1.17",
    "<Subnet_ID>"
    true
  ]

  tags = var.tags
}
```
