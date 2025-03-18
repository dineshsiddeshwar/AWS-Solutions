# Azure Application Gateway

This module create an application gateway and a Public IP.

**An example of how to use this module.**


```terraform
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
      path                  = "/"
      port            = 80
      protocol        = "Http"
      request_timeout = 20
    },
    {
      name                  = "tfe-backend-https-settings"
      cookie_based_affinity = "Disabled"
      path                  = "/"
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
```

## Variable examples

**appgw_probes**
```terraform
appgw_probes = [
  {
    host                                      = <host_name>
    interval                                  = 20
    name                                      = <name for the proble>
    path                                      = "/login"
    protocol                                  = http
    timeout                                   = 30
    pick_host_name_from_backend_http_settings = false
    unhealthy_threshold                       = 4
    port                                      = 80
    minimum_servers                           = 1
    match_body                                = <match body as string value>
    match_status_code                         = ["200-299"]
  }
]
```

**appgw_url_path_map**
```terraform
appgw_url_path_map = [
  {
    name                                = <"path_map_name">
    default_backend_address_pool_name   = <"backend_address_pool_name">
    default_redirect_configuration_name = <"redirect_configuration_name>
    default_backend_http_settings_name  = <"backend_http_settings_name">
    default_rewrite_rule_set_name       = <"rewrite_rule_set_name">
    
    path_rule = [
      {
        path_rule_name              = <name>
        paths                       = "/"
        backend_address_pool_name   = <"backend_address_pool_name">
        backend_http_settings_name  = <"backend_http_settings_name">
        redirect_configuration_name = <"redirect_configuration_name>
        rewrite_rule_set_name       = <"rewrite_rule_set_name">
      }
    ]
  }
]
```

**appgw_redirect_configuration**
```terraform
appgw_redirect_configuration = [
  {
    name                 = <"redirect_config_name">
    redirect_type        = "Permanent"
    target_listener_name = <"tgt_listner_name">
    target_url           = <"tft_url">
    include_path         = false
    include_query_string = false
  }
]
```

**appgw_rewrite_rule_set**
```terraform
appgw_rewrite_rule_set = [
  {
    name
    rewrite_rule = [
      {
        name = 
        rule_sequence
      }
    ]
    condition = [
      {
        ignore_case = true
        negate      = true
        pattern     = <"pattern">
        variable    = <"variable">
      }
    ]
    request_header_configuration = [
      {
        name  = <"request_header_configuration_name">
        value = <"request_header_configuration_value">
      }
    ]
    response_header_configuration = [
      {
        name  = <"response_header_configuration_name">
        value = <"response_header_configuration_value">
      }
    ]
    url = [
      {
        path         = "/vidoes"
        query_string = <"query_string">
        reroute      = true
      }
    ]
  }
]
```

**ssl_certificates_configs**
```terraform
ssl_certificates_configs = [
  {
    name                = <"cert_name">
    data                = file(./cert.crt)
    password            = <"password">
  }
]
```

**custom_error_configuration**
```terraform
custom_error_configuration = [
  {
    custom_error_page_url =  <"custom error page url">
    status_code           =  <"status code">
  }
]
```

**autoscale_configuration**
```terraform
autoscale_configuration = {
  min_capacity = 1
  max_capacity = 10
}
```

**ssl_policy**
```terraform
ssl_policy = {
  disabled_protocols   = [a list of disabled protocol]
  policy_type          = <"policy type">
  policy_name          = <"Policy name">
  cipher_suites        = [a list of cipher suites]
  min_protocol_version = <"min protocol version">
}
```

