provider "azurerm" {
  features {}
}

locals {
  resource_group_name = element(coalescelist(data.azurerm_resource_group.rgrp.*.name, azurerm_resource_group.rg.*.name, [""]), 0)
  location            = element(coalescelist(data.azurerm_resource_group.rgrp.*.location, azurerm_resource_group.rg.*.location, [""]), 0)
}

data "azurerm_resource_group" "rgrp" {
  count = var.create_resource_group == false ? 1 : 0
  name  = var.resource_group_name
}

resource "azurerm_resource_group" "rg" {
  count    = var.create_resource_group ? 1 : 0
  name     = var.resource_group_name
  location = var.location
  tags     = merge({ "Name" = format("%s", var.resource_group_name) }, var.tags, )
}

resource "azurerm_private_link_service" "plink" {
  name                = var.plink_name
  resource_group_name = local.resource_group_name
  location            = local.location

  auto_approval_subscription_ids              = var.auto_approval_subscription_ids
  visibility_subscription_ids                 = var.visibility_subscription_ids
  load_balancer_frontend_ip_configuration_ids = var.load_balancer_frontend_ip_configuration_ids
  enable_proxy_protocol                       = var.enable_proxy_protocol

  dynamic "nat_ip_configuration" {
    for_each = var.nat_ip_config
    iterator = itr
    content {
      name                       = itr.value[0]
      private_ip_address         = itr.value[1]
      private_ip_address_version = "IPv4" # Only IPv4 is supported as of now.
      subnet_id                  = itr.value[2]
      primary                    = itr.value[3]
    }
  }

  tags = merge({ "Name" = format("%s", var.plink_name) }, var.tags)
}

