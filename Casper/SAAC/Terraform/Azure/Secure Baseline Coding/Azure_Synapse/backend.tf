terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=2.54.0"
    }
  }


  backend "azurerm" {
    resource_group_name  = "EYGDSSEC-rg"
    storage_account_name = "eygdssecterraformstate"
    container_name       = "terraform-state"
    key                  = "baseline/azsynapse/terraform.tfstate"
  }
}



# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {}
} 