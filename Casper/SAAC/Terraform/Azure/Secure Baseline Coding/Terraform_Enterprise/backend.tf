terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>2.52.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "EYGDSSEC-rg"
    storage_account_name = "eygdssecterraformstate"
    container_name       = "terraform-state"
    key                  = "baseline/tfe/terraform.tfstate"
  }
}

provider "azurerm" {
  features {
  }
}
