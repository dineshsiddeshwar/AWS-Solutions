data "terraform_remote_state" "vpc" {
  backend = "azurerm"
  config = {
    resource_group_name  = "EYGDSSEC-rg"
    storage_account_name = "eygdssecterraformstate"
    container_name       = "terraform-state"
    key                  = "baseline/network/terraform.tfstate"
  }
}

data "azurerm_resource_group" "rg" {
  name = "EYGDSSECbaseline-rg"
}

data "azurerm_client_config" "current" {}

resource "azurerm_public_ip" "pip" {
  name                = "tfe-public-ip"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location
  allocation_method   = "Static"
  idle_timeout_in_minutes = 4
  domain_name_label = "tfeserver"

  tags = var.tags
}

resource "azurerm_linux_virtual_machine" "tfe" {
  name                = "terraform-Enterprise"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location
  size                = "Standard_D8s_v3"
  admin_username      = "tfadmin"
  network_interface_ids = [
    azurerm_network_interface.tfe.id,
  ]
  computer_name = "terraform-Enterprise"
  # encryption_at_host_enabled = true   # 'Microsoft.Compute/EncryptionAtHost' feature is not enabled for this subscription.

  identity {
    identity_ids = [ azurerm_user_assigned_identity.tfe.id ]
    type = "UserAssigned"
  }

  admin_ssh_key {
    username   = "tfadmin"
    public_key = file("id_rsa.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
    disk_size_gb = 70
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  tags = var.tags
}

resource "azurerm_network_interface" "tfe" {
  name                = "tfe-nic"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = element(data.terraform_remote_state.vpc.outputs.vnet_subnets, 0)
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id = azurerm_public_ip.pip.id
  }

  tags = var.tags

}

resource "azurerm_user_assigned_identity" "tfe" {
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location

  name = "tfe-server"

  tags = var.tags
}
