resource "azurerm_public_ip" "jump_pip" {
  name                = "tfe-jump-pip"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location
  allocation_method   = "Static"
  idle_timeout_in_minutes = 4
  domain_name_label = "tfe-jump-server"

  tags = var.tags
}

resource "azurerm_network_interface" "jump_nic" {
  name                = "jump-nic"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "jump-server-ip"
    subnet_id                     = element(data.terraform_remote_state.vpc.outputs.vnet_subnets, 0)
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id = azurerm_public_ip.jump_pip.id
  }

  tags = var.tags
}

data "azurerm_key_vault_secret" "jump_admin" {
  name         = "tfe-jump-admin"
  key_vault_id = data.azurerm_key_vault.kv.id
}

data "azurerm_key_vault_secret" "jump_admin_pwd" {
  name         = "tfe-jump-adm-pwd"
  key_vault_id = data.azurerm_key_vault.kv.id
}

resource "azurerm_windows_virtual_machine" "jump" {
  name                = "tfe-jump-vm"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location
  size                = "Standard_B2ms"
  admin_username      = data.azurerm_key_vault_secret.jump_admin.value
  admin_password      = data.azurerm_key_vault_secret.jump_admin_pwd.value
  network_interface_ids = [
    azurerm_network_interface.jump_nic.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  identity {
    type = "SystemAssigned"
  }

  source_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2019-Datacenter"
    version   = "latest"
  }

  tags = var.tags
}
