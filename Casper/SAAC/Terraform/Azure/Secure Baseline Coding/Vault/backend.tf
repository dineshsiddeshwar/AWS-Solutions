terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>2.66.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "EYGDSSEC-rg"
    storage_account_name = "eygdssecterraformstate"
    container_name       = "terraform-state"
    key                  = "baseline/vault/terraform.tfstate"
  }
}

provider "azurerm" {
  features {
    # key_vault {
    #   purge_soft_delete_on_destroy = true
    # }
  }
}

