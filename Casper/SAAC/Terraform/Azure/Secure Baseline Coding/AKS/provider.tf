terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=2.78.0"
    }
  }
  backend "azurerm" {
    resource_group_name  = "EYGDSSEC-rgs"
    storage_account_name = "eygdssecterraformstate"
    container_name       = "terraform-state"
    key                  = "baseline/network/terraform.tfstate"
  }
}

provider "azurerm" { 
  features {} 
}