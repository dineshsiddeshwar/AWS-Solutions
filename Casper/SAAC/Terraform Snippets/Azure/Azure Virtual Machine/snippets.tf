######################################################################################################################################################################
############################################################       REQUIREMENTS SECTION        #######################################################################
######################################################################################################################################################################
# Ensure Azure Virtual machines are secured using virtual networks
resource "azurerm_network_interface_security_group_association" "example" {
  network_interface_id      = var.NIC_id
  network_security_group_id = var.NSG_id
}

# Ensure VMs are not associated with any public IP address
# terraform import azurerm_windows_virtual_machine.example /subscriptions/xxxxxx-xxxxxx-xxxxxx-xxxxxx-xxxxxx/resourceGroups/yourvaluehere/providers/Microsoft.Compute/virtualMachines/yourvaluehere
resource "azurerm_windows_virtual_machine" "example" {
  name                = var.VM_details.name
  resource_group_name = var.VM_details.resource_group_name
  location            = var.VM_details.location
  size                = var.VM_details.size
  admin_username      = var.VM_details.admin_username
  admin_password      = var.VM_details.admin_password
  license_type        = var.VM_details.license_type
  public_ip_address   = null 
  secure_boot_enabled = true #<------- Ensure Trusted Launch is enabled for Azure Virtual machine # WARNING: Best to be used at VM creation only ! ! !

  network_interface_ids = [
    var.network_interface_ids[0]
  ]

  os_disk {
    name = var.os_disk.name
    caching = var.os_disk.caching
    storage_account_type = var.os_disk.storage_account_type
  }

  source_image_reference { 
          offer     = var.source_image_reference.offer
          publisher = var.source_image_reference.publisher
          sku       = var.source_image_reference.sku  
          version   = var.source_image_reference.version  
  }

  identity { #<------- Ensure Azure secrets securely managed using Managed Identities
    type = var.identity.type
  }

  tags = { #<------- Ensure that virtual network uses standard organizational Resource tagging method
    cost_center = var.tags.cost_center
    ppmc_id     = var.tags.ppmc_id
    toc         = var.tags.toc
    usage_id    = var.tags.usage_id
    env_type    = var.tags.env_type
    exp_date    = var.tags.exp_date
    endpoint    = var.tags.endpoint
    sd_period   = var.tags.sd_period
  }

}

# terraform import azurerm_network_interface.example /subscriptions/xxxxxx-xxxxxx-xxxxxx-xxxxxx-xxxxxx/resourceGroups/yourvaluehere/providers/Microsoft.Network/networkInterfaces/yourvaluehere
resource "azurerm_network_interface" "example" {
  name                = var.nic.name
  location            = var.VM_details.location
  resource_group_name = var.VM_details.resource_group_name

  ip_configuration {
    name                          = var.nic.ip_config_name
    subnet_id                     = var.nic.subnet_id
    private_ip_address_allocation = var.nic.private_ip_address_allocation
    public_ip_address_id = null
  }
}


# INVALIDATED - Ensure Activity logging is enabled for virtual machines (moved to Subscription security baseline section)

# INVALIDATED - Ensure that 'OS and Data' disks are encrypted with Organization Managed Key (CMK) (moved to Disk Storage security baseline section)

# IVALIDATED - Ensure all the sensitive information is encrypted during transit (might needed to be moved to Web App section)


# Ensure all the web applications deployed on VM Should not be exposed to Internet
# terraform import azurerm_network_security_rule.example /subscriptions/xxxxxx-xxxxxx-xxxxxx-xxxxxx-xxxxxx/resourceGroups/yourvaluehere/providers/Microsoft.Network/networkInterfaces/yourvaluehere
resource "azurerm_network_security_rule" "example" {
    name = "Internet"
    priority  = 100
    direction = "Outbound" 
    access = "Deny" 
    protocol = "Tcp" 
    source_port_range  = "*"
    destination_port_range  = "*" 
    source_address_prefix = "*" 
    destination_address_prefix= "Internet" 
    resource_group_name         = var.VM_details.resource_group_name
    network_security_group_name = var.NSG_name
}

resource "azurerm_network_security_rule" "example2" {
    name = "Internet"
    priority  = 100
    direction = "Inbound" 
    access = "Deny" 
    protocol = "Tcp" 
    source_port_range  = "*"
    destination_port_range  = "*" 
    source_address_prefix = "*" 
    destination_address_prefix= "Internet" 
    resource_group_name         = var.VM_details.resource_group_name
    network_security_group_name = var.NSG_name
}

# Ensure that least privilege access method is implemented using Role-based access control (RBAC)
resource "azurerm_role_assignment" "example" {
  scope              = var.VM_details.id # VM's Id
  role_definition_name = var.role_name
  principal_id       = azurerm_windows_virtual_machine.example.identity[0].principal_id # Object ID of the security principal to who should assume the role - This should be Object ID of the newly recreated VM if Trusted Launch subsequently set to 'True' through Terraform
  depends_on = [
    azurerm_windows_virtual_machine.example
  ]
}

#  Ensure users do not have permission to remove any already installed security software (cannot be done through Terraform)

#  Ensure only organization approved VM images are used for deployment (This is a policy assignment) NOTE: It is assumed that Azure Policy has already been created with the array of approved images whether custom or third-party ! 
/*

ATTENTION: Choose ONE of the below code blocks, depending on the desired scope where policy should apply !
I
resource "azurerm_management_group_policy_assignment" "example" {
  name                 = var.policy.name
  policy_definition_id = var.policy.policy_definition_id 
  management_group_id  = var.policy.management_group_id
}

II
resource "azurerm_subscription_policy_assignment" "example" {
  name                 = var.policy.name
  policy_definition_id = var.policy.policy_definition_id
  subscription_id      = var.policy.subscription_id
}

III
resource "azurerm_resource_group_policy_assignment" "example" {
  name                 = var.policy.name
  resource_group_id    = var.policy.resource_group_id
  policy_definition_id = var.policy.policy_definition_id
}

IV
resource "azurerm_resource_policy_assignment" "example" {
  name                 = var.policy.name
  resource_id          = var.policy.resource_id
  policy_definition_id = var.policy.policy_definition_id
}
*/


# INVALIDATED - Ensure strict Inbound access control is enforced (cannot be done through Terraform)

# INVALIDATED - Ensure Azure VM adheres to organization patch and vulnerability management standards (MS Defender for Cloud security requirements)

# INVALIDATED - Ensure idle Azure VM instances are identified and stopped or terminated (out of scope - cannot be done through Terraform)

