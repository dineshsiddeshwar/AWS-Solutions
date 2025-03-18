terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>2.52.0"
    }
  }

  # backend "azurerm" {
  #   resource_group_name  = "EYGDSSEC-rg"
  #   storage_account_name = "eygdssecterraformstate"
  #   container_name       = "terraform-state"
  #   key                  = "baseline/common_resources/terraform.tfstate"
  # }

  backend "remote" {
    hostname = "tfeserver.eastus.cloudapp.azure.com"
    organization = "ey-gds-india"

    workspaces {
      name = "Common_Resources"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }
}
