data "terraform_remote_state" "vpc" {
  backend = "azurerm"
  config = {
    resource_group_name  = "EYGDSSEC-rg"
    storage_account_name = "eygdssecterraformstate"
    container_name       = "terraform-state"
    key                  = "baseline/network/terraform.tfstate"
  }
}

data "azurerm_client_config" "current" {}

data "azurerm_resource_group" "rg" {
  name = "EYGDSSECbaseline-rg"
}

module "azdatabricks" {

  source                 = "../Modules/Azure_Databricks_module"
  settings_name          = var.settings_name
  global_settings_prefix = var.global_settings_prefix
  random_length          = var.random_length

  resource_group_name         = var.resource_group_name
  location                    = var.location
  sku                         = var.sku
  managed_resource_group_name = var.managed_resource_group_name != "" ? var.managed_resource_group_name : null
  tags                        = var.tags


  custom_parameters = [{

    no_public_ip        = false
    public_subnet_name  = element(data.terraform_remote_state.vpc.outputs.vnet_subnets, 0)
    private_subnet_name = element(data.terraform_remote_state.vpc.outputs.vnet_subnets, 1)
    virtual_network_id  = data.terraform_remote_state.vpc.outputs.vnet_id

  }]


}