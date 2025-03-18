data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

resource "azurerm_private_endpoint" "pe" {
  name                = "${var.name}_pe"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  subnet_id           = var.subnet_id

  private_service_connection {
    name                           = "${var.name}_psc"
    private_connection_resource_id = var.resource_id
    is_manual_connection           = var.is_manual_connection
    subresource_names = var.subresource_names
  }
}

data "azurerm_private_endpoint_connection" "pe_connection" {
  name                = azurerm_private_endpoint.pe.name
  resource_group_name = azurerm_private_endpoint.pe.resource_group_name
}

resource "azurerm_private_dns_zone" "pdz" {
  count = var.create_private_dns_zone ? 1 : 0
  name                = var.private_dns_zone_name
  resource_group_name = data.azurerm_resource_group.rg.name
  dynamic "soa_record" {
    for_each = var.soa_record == null ? [] : list(var.soa_record)
    iterator = soa
    content {
      email        = lookup(soa.value, "email", "")
      expire_time  = lookup(soa.value, "expire_time", 2419200)
      minimum_ttl  = lookup(soa.value, "minimum_ttl", 10)
      refresh_time = lookup(soa.value, "refresh_time", 3600)
      retry_time   = lookup(soa.value, "retry_time", 300)
      ttl          = lookup(soa.value, "ttl", 3600)
    }
  }
  tags = var.tags
}

resource "azurerm_private_dns_a_record" "a_record" {
  name                = var.name
  zone_name           = var.private_dns_zone_name
  resource_group_name = data.azurerm_resource_group.rg.name
  ttl                 = var.ttl
  records             = [data.azurerm_private_endpoint_connection.pe_connection.private_service_connection.0.private_ip_address]
}

resource "azurerm_private_dns_zone_virtual_network_link" "vnet_link" {
  count = var.vnet_id != null ? 1 : 0
  name                  = "${var.name}_lnk"
  resource_group_name   = data.azurerm_resource_group.rg.name
  private_dns_zone_name = var.private_dns_zone_name
  virtual_network_id    = var.vnet_id
}
