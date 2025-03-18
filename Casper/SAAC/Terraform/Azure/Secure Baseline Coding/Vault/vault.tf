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

module "vault" {
  source              = "../Modules/Vault_module"
  vault_name          = var.vault_name
  resource_group_name = "EYGDSSECbaseline-rg"
  sku_name            = var.sku_name
  admin_objects_ids   = [data.azurerm_client_config.current.object_id]

  # network_acls = [
  #   {
  #     bypass                     = "AzureServices",
  #     default_action             = "Deny",
  #     ip_rules                   = [],
  #     virtual_network_subnet_ids = toset(data.terraform_remote_state.vpc.outputs.vnet_subnets)
  #   }
  # ]

  ### Unable to set contact due to permission issue.
  # contact = [
  #   {
  #     email = "Sai.Santosh.Pavan.Lanka@gds.ey.com"
  #     name  = "Santosh Lanka"
  #     phone = "1234567890"
  #   }
  # ]

  tags = var.tags
}

module "endpoint" {
  source                = "../Modules/Private_Endpoint_module"
  resource_group_name   = "EYGDSSECbaseline-rg"
  name                  = module.vault.key_vault_name
  resource_id           = module.vault.vault_id
  subresource_names     = ["vault"]
  private_dns_zone_name = "privatelink.vaultcore.azure.net"
  vnet_id               = data.terraform_remote_state.vpc.outputs.vnet_id
  tags                  = var.tags
}
