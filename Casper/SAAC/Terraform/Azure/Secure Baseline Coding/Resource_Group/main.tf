resource "azurerm_resource_group" "rg" {
  name     = "${var.prefix}-rg"
  location = var.location
  tags = merge({"Name" = format("%s-resource-group", var.prefix)},var.standard_tags)
}

resource "azurerm_storage_account" "sa" {
  name                     = "eygdssecterraformstate"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS" # available types - LRS, GRS, RAGRS, ZRS, GZRS and RAGZRS
  min_tls_version = "TLS1_2"
  allow_blob_public_access = true

  tags = merge({"Name" = "EYGDSSEC-terraform-state"},var.standard_tags)
}

resource "azurerm_storage_container" "container" {
  name                  = "terraform-state"
  storage_account_name  = azurerm_storage_account.sa.name
  container_access_type = "blob" # Available values - lob, container or private
}
