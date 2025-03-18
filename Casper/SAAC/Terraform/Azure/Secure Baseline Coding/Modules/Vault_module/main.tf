locals {
  tenant_id = coalesce(
    var.tenant_id,
    data.azurerm_client_config.current.tenant_id,
  )
  reader_objects = var.enable_rbac_authorization ? [] : toset(var.reader_objects_ids)
  admin_objects = var.enable_rbac_authorization ? [] : toset(var.admin_objects_ids)
}

resource "random_string" "random-name" {
  length  = 5
  upper   = false
  lower   = true
  number  = true
  special = false
}

data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "vault" {
  name                        = lower("${var.vault_name}-${random_string.random-name.result}")
  location                    = data.azurerm_resource_group.rg.location
  resource_group_name         = data.azurerm_resource_group.rg.name
  enabled_for_disk_encryption = var.enabled_for_disk_encryption
  tenant_id                   = local.tenant_id
  soft_delete_retention_days  = var.soft_delete_retention_days
  purge_protection_enabled    = var.purge_protection_enabled

  sku_name                        = var.sku_name
  enabled_for_deployment          = var.enabled_for_deployment
  enabled_for_template_deployment = var.enabled_for_template_deployment
  enable_rbac_authorization       = var.enable_rbac_authorization

  dynamic network_acls {
    for_each = var.network_acls == null ? [] : var.network_acls
    iterator = acl
    content {
      bypass = lookup(acl.value, "bypass", "AzureServices")
      default_action = lookup(acl.value, "default_action", "Deny")
      ip_rules = lookup(acl.value, "ip_rules", [])
      virtual_network_subnet_ids = lookup(acl.value, "virtual_network_subnet_ids", [])
    }
  }

   dynamic contact {
    for_each = var.contact
    content {
      email = lookup(contact.value, "email", "")
      name  = lookup(contact.value, "name", "")
      phone = lookup(contact.value, "phone", "")
    }
  }

  tags = var.tags
}

# resource "azurerm_advanced_threat_protection" "vault" {
#   target_resource_id = azurerm_key_vault.vault.id
#   enabled            = true
# }

module "monitoring" {
  source = "../Diagnostic_module"
  name = azurerm_key_vault.vault.name
  resource_id = azurerm_key_vault.vault.id
}


resource "azurerm_key_vault_access_policy" "readers_policy" {
  for_each = local.reader_objects

  object_id    = each.value
  tenant_id    = local.tenant_id
  key_vault_id = azurerm_key_vault.vault.id

  key_permissions = [
    "Get",
    "List",
  ]

  secret_permissions = [
    "Get",
    "List",
  ]

  certificate_permissions = [
    "Get",
    "List",
  ]

  storage_permissions = [ 
    "Get", 
    "List",
  ]
}

resource "azurerm_key_vault_access_policy" "admin_policy" {
  for_each = local.admin_objects

  object_id    = each.value
  tenant_id    = local.tenant_id
  key_vault_id = azurerm_key_vault.vault.id

  key_permissions = [
    "Backup",
    "Create",
    "Decrypt",
    "Delete",
    "Encrypt",
    "Get",
    "Import",
    "List",
    "Purge",
    "Recover",
    "Restore",
    "Sign",
    "UnwrapKey",
    "Update",
    "Verify",
    "WrapKey",
  ]

  secret_permissions = [
    "Backup",
    "Delete",
    "Get",
    "List",
    "Purge",
    "Recover",
    "Restore",
    "Set",
  ]

  certificate_permissions = [
    "Backup",
    "Create",
    "Delete",
    "DeleteIssuers",
    "Get",
    "GetIssuers",
    "Import",
    "List",
    "ListIssuers",
    "ManageContacts",
    "ManageIssuers",
    "Purge",
    "Recover",
    "Restore",
    "SetIssuers",
    "Update",
  ]

  storage_permissions = [ 
    "Backup",
    "Delete",
    "DeleteSAS",
    "Get",
    "GetSAS",
    "List",
    "ListSAS",
    "Purge",
    "Recover",
    "RegenerateKey",
    "Restore",
    "Set",
    "SetSAS",
    "Update",
 ]
}
