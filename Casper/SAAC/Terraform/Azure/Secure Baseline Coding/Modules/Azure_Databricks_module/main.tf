
resource "azurecaf_name" "wp" {
  name          = var.settings_name
  resource_type = "azurerm_databricks_workspace"
  prefixes      = var.global_settings_prefix
  random_length = var.random_length
  clean_input   = true

}

# Databricks workspace
resource "azurerm_databricks_workspace" "ws" {
  name                        = azurecaf_name.wp.result
  resource_group_name         = var.resource_group_name
  location                    = var.location
  sku                         = var.sku
  managed_resource_group_name = var.managed_resource_group_name
  tags                        = var.tags

  dynamic "custom_parameters" {
    for_each = var.custom_parameters

    content {
      no_public_ip        = lookup(custom_parameters.value, "no_public_ip", false)
      public_subnet_name  = lookup(custom_parameters.value, "public_subnet_name", "")
      private_subnet_name = lookup(custom_parameters.value, "private_subnet_name", "")
      virtual_network_id  = lookup(custom_parameters.value, "virtual_network_id", "")
    }
  }
}



# no_public_ip        = false
# public_subnet_name  = element(data.terraform_remote_state.vpc.outputs.vnet_subnets,0)
# private_subnet_name = element(data.terraform_remote_state.vpc.outputs.vnet_subnets,1)
# virtual_network_id  = data.terraform_remote_state.vpc.outputs.vnet_id