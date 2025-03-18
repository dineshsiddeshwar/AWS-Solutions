data "azurerm_storage_account" "sa" {
  name                = "eygdsbaseline"
  resource_group_name = data.azurerm_resource_group.rg.name
}

resource "azurerm_storage_container" "tfe" {
  name                  = "terraform-enterprise"
  storage_account_name  = data.azurerm_storage_account.sa.name
  container_access_type = "private"
}
