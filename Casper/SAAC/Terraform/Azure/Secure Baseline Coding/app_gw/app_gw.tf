data "terraform_remote_state" "vpc" {
  backend = "azurerm"
  config = {
    resource_group_name  = "EYGDSSEC-rg"
    storage_account_name = "eygdssecterraformstate"
    container_name       = "terraform-state"
    key                  = "baseline/network/terraform.tfstate"
  }
}

data "azurerm_resource_group" "rg" {
  name = "EYGDSSECbaseline-rg"
}

data "azurerm_client_config" "current" {}

module "app_gw" {
  source                              = "../Modules/App_Gateway_module"
  location                            = data.azurerm_resource_group.rg.location
  stack                               = "baseline"
  environment                         = "dev"
  location_short                      = "us"
  resource_group_name                 = data.azurerm_resource_group.rg.name
  appgw_name                          = "eygds-baseline-app-gateway"
  appgw_private                       = true
  appgw_private_ip                    = "172.19.6.9"
  frontend_ip_configuration_name      = "baseline-us-dev-frontipconfig"
  frontend_priv_ip_configuration_name = "baseline-us-dev-private-frontipconfig"

  subnet_id = element(data.terraform_remote_state.vpc.outputs.vnet_subnets, 3)

  frontend_port_settings = [
    {
      name = "frontend-http-port"
      port = 80
    },
    {
      name = "frontend-https-port"
      port = 443
    }
  ]

  appgw_backend_pools = [{
    name = "tfe-backendpool"
    # fqdns = ["example.com"] 172.19.1.4
    ip_addresses = ["172.19.1.4"]
  }]

  appgw_routings = [{
    name                       = "tfe-routing-http"
    rule_type                  = "Basic"
    http_listener_name         = "tfe-listener-http"
    backend_address_pool_name  = "tfe-backendpool"
    backend_http_settings_name = "tfe-backend-https-settings"
  }]

  appgw_http_listeners = [{
    frontend_ip_configuration_name = "baseline-us-dev-frontipconfig"
    name                           = "tfe-listener-http"
    frontend_port_name             = "frontend-http-port"
    protocol                       = "Http"
    # ssl_certificate_name           = "baseline-tfe-example-com-sslcert"
    # host_name                      = "tfeserver.eastus.cloudapp.azure.com"
    # require_sni                    = true
  }]

  appgw_backend_http_settings = [
    {
      name                  = "tfe-backhttpsettings"
      cookie_based_affinity = "Disabled"
      # path                  = "/"
      port            = 80
      protocol        = "Http"
      request_timeout = 20
    },
    {
      name                  = "tfe-backend-https-settings"
      cookie_based_affinity = "Disabled"
      # path                  = "/"
      port                           = 443
      host_name                      = "tfeserver.eastus.cloudapp.azure.com"
      trusted_root_certificate_names = ["tfe-rootca"]
      protocol                       = "Https"
      request_timeout                = 20
    }
  ]

  trusted_root_certificate_configs = [{
    name = "tfe-rootca"
    data = "./ca.cer"
  }]
}
