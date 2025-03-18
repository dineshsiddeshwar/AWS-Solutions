# Ensure SQL Server deployed with public access disabled
resource "azurerm_network_security_rule" "network_security_rule" {
  name                        = var.ns_rule.name
  priority                    = var.ns_rule.priority
  direction                   = var.ns_rule.direction
  access                      = var.ns_rule.access
  protocol                    = var.ns_rule.protocol
  source_port_range           = var.ns_rule.source_port_range
  destination_port_range      = var.ns_rule.destination_port_range
  source_address_prefix       = var.ns_rule.source_address_prefix
  resource_group_name         = var.resource_group.name
  network_security_group_name = data.azurerm_network_security_group.nsg.name
}

# terraform import azurerm_mssql_server.example /subscriptions/xxxxxx-xxxxxx-xxxxxx-xxxxxx-xxxxxx/resourceGroups/yourvaluehere/providers/Microsoft.Compute/sqlserver/yourvaluehere
resource "azurerm_mssql_server" "mssql_server" {
  name                          = var.mssql_server.name
  resource_group_name           = var.resource_group.name
  location                      = var.resource_group.location
  version                       = var.mssql_server.version
  administrator_login           = data.azurerm_key_vault_secret.user.value
  administrator_login_password  = data.azurerm_key_vault_secret.password.value
  public_network_access_enabled = false #----------> Ensure SQL VMs are not associated with any Public IP address
  minimum_tls_version           = var.mssql_server.tls #----------> Ensure SQL Database connections are encrypted in transit using TLS 1.2

  identity {
    type = var.mssql_server.identity #------>  Ensure application level access is granted using Managed Identities
  }
}

#  Ensure least privilege access method for SQL Server is implemented using Role-based access control (RBAC)
resource "azurerm_role_assignment" "sql_server_role_assignment" {
  scope              = azurerm_mssql_server.mssql_server.id
  role_definition_id = var.sql_server_role_definition_id
  principal_id       = azurerm_mssql_server.mssql_server.identity.0.principal_id
}

resource "azurerm_network_interface" "network_interface" {
  name                = var.nic.name
  location            = var.resource_group.location
  resource_group_name = var.resource_group.name

  ip_configuration {
    name                          = var.nic.ip_config_name
    subnet_id                     = data.azurerm_subnet.subnet
    private_ip_address_allocation = var.nic.private_ip_address_allocation
    public_ip_address_id          = null
  }
}

# Ensure Azure SQL VM is deployed in the Virtual networks and Network Security Groups are used to protect the Azure SQL VM
resource "azurerm_network_interface_security_group_association" "nic_sec_group" {
  network_interface_id      = azurerm_network_interface.network_interface.id
  network_security_group_id = data.azurerm_network_security_group.nsg.id
}

resource "azurerm_virtual_machine" "virtual_machine" {
  name                  = var.virtual_machine.name
  location              = var.resource_group.location
  resource_group_name   = var.resource_group.name
  network_interface_ids = [azurerm_network_interface.network_interface.id]
  vm_size               = var.virtual_machine.size
  vtpm_enabled          = true # Ensure Trusted Launch is enabled for Azure SQL Virtual Machine

  storage_image_reference {
    publisher = var.vmstorage_image_reference_details.publisher
    offer     = var.vmstorage_image_reference_details.offer
    sku       = var.vmstorage_image_reference_details.sku
    version   = var.vmstorage_image_reference_details.version
  }
  storage_os_disk {
    name              = var.storage_os_disk_details.name
    caching           = var.storage_os_disk_details.caching
    create_option     = var.storage_os_disk_details.create_option
    managed_disk_type = var.storage_os_disk_details.managed_disk_type # The Manged disk terraform documents Encrypting customer Manged Key 3. Ensure managed disk in Azure SQL VM is Encrypted Managed keys
  }
  os_profile {
    computer_name  = var.os_profile_details.computer_name
    admin_username = data.azurerm_key_vault_secret.user.value
    admin_password = data.azurerm_key_vault_secret.password.value
  }
  os_profile_windows_config {
    timezone                  = var.os_profile_windows_config_details.timezone
    provision_vm_agent        = var.os_profile_windows_config_details.provision_vm_agent
    enable_automatic_upgrades = var.os_profile_windows_config_details.enable_automatic_upgrades
  }
  identity {
    type = var.virtual_machine.identity # ---------> Ensure application level access is granted using Managed Identities
  }
}

resource "azurerm_mssql_virtual_machine" "mssql_vm" {
  virtual_machine_id               = azurerm_virtual_machine.virtual_machine.id
  sql_license_type                 = var.mssql_vm.sql_license_type
  r_services_enabled               = var.mssql_vm.r_services_enabled
  sql_connectivity_port            = var.mssql_vm.sql_connectivity_port
  sql_connectivity_type            = var.mssql_vm.sql_connectivity_type
  sql_connectivity_update_password = data.azurerm_key_vault_secret.password.value
  sql_connectivity_update_username = data.azurerm_key_vault_secret.user.value
  auto_patching {
    day_of_week                            = var.mssql_vm.day_of_week
    maintenance_window_duration_in_minutes = var.mssql_vm.maintenance_window_duration_in_minutes
    maintenance_window_starting_hour       = var.mssql_vm.maintenance_window_starting_hour
  }
  
  # Ensure that SQL VM secrets are vaulted securely in Azure Keyvault
  key_vault_credential{
    name                     = var.mssql_vm_key_vault_credential.name
    key_vault_url            = data.azurerm_key_vault.kv.vault_uri
    service_principal_name   = var.mssql_vm_key_vault_credential.service_principal_name
    service_principal_secret = var.mssql_vm_key_vault_credential.service_principal_secret
  }

  /*
  storage_configuration {
    disk_type             = "NEW"  # (Required) The type of disk configuration to apply to the SQL Server. Valid values include NEW, EXTEND, or ADD.
    storage_workload_type = "OLTP" # (Required) The type of storage workload. Valid values include GENERAL, OLTP, or DW.
    # The storage_settings block supports the following:
    data_settings {
      default_file_path = var.default_file_path_data # (Required) The SQL Server default path
      luns              = [0]                        #azurerm_virtual_machine_data_disk_attachment.datadisk_attach[count.index].lun]
    }
    log_settings {
      default_file_path = var.default_file_path_log # (Required) The SQL Server default path
      luns              = [1]                       #azurerm_virtual_machine_data_disk_attachment.logdisk_attach[count.index].lun] # (Required) A list of Logical Unit Numbers for the disks.
    }
  }*/
  # Ensure that Azure SQL VM uses standard organizational resource tagging method
  tags = var.sql_vm_tags
}

resource "azurerm_mssql_database" "mssql_database" {
  name      = var.mssql_database_name
  server_id = azurerm_mssql_server.mssql_server.id
}

#  Ensure only organization approved SQL VM images are used for deployment (This is a policy assignment) NOTE: It is assumed that Azure Policy has already been created with the array of approved images whether custom or third-party ! 
/*
ATTENTION: Choose ONE of the below code blocks, depending on the desired scope where policy should apply !
I
resource "azurerm_management_group_policy_assignment" "management_policy_assignment" {
  name                 = var.policy.name
  policy_definition_id = var.policy.policy_definition_id 
  management_group_id  = var.policy.management_group_id
}
II
resource "azurerm_subscription_policy_assignment" "subscription_policy_assignment" {
  name                 = var.policy.name
  policy_definition_id = var.policy.policy_definition_id
  subscription_id      = var.policy.subscription_id
}
III
resource "azurerm_resource_group_policy_assignment" "resource_group_policy_assignment" {
  name                 = var.policy.name
  resource_group_id    = var.policy.resource_group_id
  policy_definition_id = var.policy.policy_definition_id
}
IV
resource "azurerm_resource_policy_assignment" "resource_policy_assignment" {
  name                 = var.policy.name
  resource_id          = var.policy.resource_id
  policy_definition_id = var.policy.policy_definition_id
}
*/
# Ensure SQL virtual machine are constantly scanned by Malware and Vulnerability scanning tool - This is implemented on Microsoft defender for cloud 
# Ensure Azure Activity logging is enabled for Azure SQL Virtual Machine - Implemented on Organizational runbook at Subscription level

