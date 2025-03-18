# locals {
#   module_tag = {
#     "module" = basename(abspath(path.module))
#   }
#   tags = merge(local.module_tag, try(var.settings.tags, null), var.base_tags)
# }

provider "azurerm" {
  features {}
}

terraform {
  required_providers {
    azurecaf = {
      source = "aztfmod/azurecaf"
    }
  }
}