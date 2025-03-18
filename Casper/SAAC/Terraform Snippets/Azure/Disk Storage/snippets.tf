######################################################################################################################################################################
############################################################       REQUIREMENTS SECTION        #######################################################################
######################################################################################################################################################################

# Ensure that Managed disks can be accessed only through Private link for disk export -- NOTE: It is assumed Private Endpoint and Disk Access resources DO NOT exist in the environment
resource "azurerm_disk_access" "example" {
  name                = var.disk_access_resource
  resource_group_name = var.resource_group.name
  location            = var.resource_group.location
}

resource "azurerm_private_endpoint" "example" {
  name                = var.private_endpoint_name
  location            = var.resource_group.location
  resource_group_name = var.resource_group.name
  subnet_id           = data.azurerm_subnet.example.id

  private_service_connection {
    name                           = var.private_connection
    private_connection_resource_id = azurerm_disk_access.example.id
    subresource_names = [ "disks" ]
    is_manual_connection           = false
  }

  depends_on = [
    azurerm_disk_access.example
  ]
}

#run the following in terminal: terraform import azurerm_managed_disk.example /subscriptions/xxxx-xxxxx-xxxxxxx/resourceGroups/example-rg/providers/Microsoft.Compute/disks/exampledisk (to import already existing disk resource to Terraform state file, in order for Terraform to be able to modify it) !
resource "azurerm_managed_disk" "example" {
    create_option        = data.azurerm_managed_disk.sample.create_option
    disk_iops_read_write = data.azurerm_managed_disk.sample.disk_iops_read_write
    disk_mbps_read_write = data.azurerm_managed_disk.sample.disk_mbps_read_write
    disk_size_gb         = data.azurerm_managed_disk.sample.disk_size_gb
    name                 = data.azurerm_managed_disk.sample.name
    resource_group_name  = var.resource_group.name
    storage_account_type = data.azurerm_managed_disk.sample.storage_account_type
    location             = var.resource_group.location
    disk_encryption_set_id = azurerm_disk_encryption_set.example.id  #<------  Ensure managed disk is Encrypted with Customer Managed Keys (please see below) !
  # disk_encryption_set_id = var.disk_encryption_set_id #<------  Ensure managed disk is Encrypted with Customer Managed Keys (if Disc Encryption Set already exists in the environment and is NOT needed to be created through Terraform, use this line and comment the one above) !
    
    tags = {     #<------ Ensure that Managed disk uses standard organizational Resource tagging method
        cost_center = var.cost_center
        ppmc_id = var.ppmc_id
        toc = var.toc
        usage_id = var.usage_id
        env_type = var.env_type
        exp_date = var.exp_date
        endpoint = var.endpoint
        sd_period = var.sd_period
    }

    network_access_policy = "AllowPrivate" 
    disk_access_id = azurerm_disk_access.example.id

    depends_on = [ # This block is not needed if Disk Access, Private Endpoint and Disk Enryption Set already EXIST in the environmnet and are NOT needed to be created through Terraform !
      azurerm_disk_access.example,
      azurerm_private_endpoint.example,
      azurerm_disk_encryption_set.example
    ]
}

#  Ensure that least privilege access method is implemented using Role-based access control (RBAC)
resource "azurerm_role_assignment" "example" {
  scope              = var.rbac_role_assignment.scope 
  role_definition_name = var.rbac_role_assignment.roleName                                                                        
  principal_id         = var.rbac_role_assignment.objectId             
}


#  Ensure managed disk is Encrypted with Customer Managed Keys   <------ NOTE: If Disc Encryption Set is NOT created already in the environment and approproate roles added to KeyVault this code is needed, otherwise, please see resource configuration under req. n. 1 !
resource "azurerm_disk_encryption_set" "example" {
  name                = var.key_encryption_set
  resource_group_name = var.resource_group.name
  location            = var.resource_group.location
  key_vault_key_id    = var.key_vault_key.keyURL

  identity {
    type = "SystemAssigned"
  }
}
resource "azurerm_role_assignment" "role1" {
  scope                = "${var.key_vault_key.keyVaultId}/keys/${var.key_vault_key.keyName}"
  role_definition_name = var.role_name
  principal_id         = azurerm_disk_encryption_set.example.identity[0].principal_id

  depends_on = [
    azurerm_disk_encryption_set.example
  ]
}

/*
# Alternative code: If Disk Encryption Set already exists in the environment and it does NOT need to be created through Terraform !
resource "azurerm_role_assignment" "role1" {
  scope                = "${var.key_vault_key.keyVaultId}/keys/${var.key_vault_key.keyName}"
  role_definition_name = var.role_name
  principal_id         = var.disk_encryption_set_objectId
}
*/

#  Ensure That managed disk snapshots are Created prior to Encryption and snapshots are Encrypted with Customer Managed Keys - INVALIDATED (cannot be accomplished through Terraform) !

#  Ensure activity logs are enabled for managed disk - INVALIDATED (implemented at susbscription level requirements)
