######################################################################################################################################################################
############################################################       Variables        #######################################################################
######################################################################################################################################################################

data "azurerm_client_config" "current" {}

data "azurerm_resource_group" "example" {
  name = "kvresourcegroup"
}

data "azurerm_key_vault" "kv" {
  name                = "container-reg-kv"
  resource_group_name = data.azurerm_resource_group.example.name
}

data "azurerm_key_vault_secret" "admin" {
  name         = "database-admin"
  key_vault_id = data.azurerm_key_vault.kv.id
}

data "azurerm_key_vault_secret" "password" {
  name         = "database-password"
  key_vault_id = data.azurerm_key_vault.kv.id
}

variable "tags" {
  type = map
  description = "Company tags"
  default = {
    Env = "Stage"
    Owner = "Nikola"
  }
}

variable "rg_name" {
  type = string
  description = "Resource group name"
  default = "PosgreSQL-RG"
}

variable "rg_location" {
  type = string
  description = "Resource group location"
  default = "West Europe"
}

variable "sa_name" {
  type = string
  description = "Storage account name"
  default = "postgresqlsa123"
}

variable "sa_tier" {
  type = string
  description = "Storage account tier"
  default = "Standard"
}

variable "sa_replication" {
  type = string
  description = "Storage account tier"
  default = "GRS"
}

variable "vn_name" {
  type = string
  description = "Virtual network name"
  default = "PostgreSQL-PN"
}

variable "p_ip_name" {
  type = string
  description = "Public IP name"
  default = "postgre-public-ip"
}

variable "p_ip_sku" {
  type = string
  description = "Public IP SKU"
  default = "Standard"
}

variable "subnet_name" {
  type = string
  description = "Subnate name"
  default = "endpoint"
}

variable "nsg_name" {
  type = string
  description = "Network Sec Group name"
  default = "example-nsg"
}

variable "pe_name" {
  type = string
  description = "Private endpoint name"
  default = "postgresql-endpoint"
}

variable "ps_name" {
  type = string
  description = "Private service connection name"
  default = "postgresql-privateserviceconnection"
}

variable "postgre_name" {
  type = string
  description = "PostgreSQL server name"
  default = "postgresqlserver123"
}

variable "postgre_sku" {
  type = string
  description = "PostgreSQL SKU type"
  default = "GP_Gen5_2"
}

variable "postgre_version" {
  type = string
  description = "PostgreSQL version"
  default = "11"
}

variable "ssl_minimal" {
  type = string
  description = "SSL minimal TLS version"
  default = "TLS1_2"
}

variable "mds_name" {
  type = string
  description = "Monitoring Diagnostic Settings name"
  default = "DB-Monitoring"
}

variable "ra_scope" {
  type = string
  description = "The scope at which the Role Assignment applies to the resource."
}

variable "ra_user" {
  type = string
  description = "User or group ID"
}

######################################################################################################################################################################
############################################################       Resources for testing       #######################################################################
######################################################################################################################################################################

resource "azurerm_resource_group" "example" {
  name = var.rg_name
  location = var.rg_location
}

resource "azurerm_storage_account" "example" {
  name                     = var.sa_name
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = var.sa_tier
  account_replication_type = var.sa_replication
}
resource "azurerm_virtual_network" "example" {
  name                = var.vn_name
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
}

resource "azurerm_public_ip" "example" {
  name                = var.p_ip_name
  sku                 = var.p_ip_sku
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  allocation_method   = "Static"
}

resource "azurerm_subnet" "endpoint" {
  name                 = var.subnet_name
  resource_group_name  = azurerm_resource_group.example.name
  virtual_network_name = azurerm_virtual_network.example.name
  address_prefixes     = ["10.0.2.0/24"]

  enforce_private_link_endpoint_network_policies = true
}

resource "azurerm_network_security_group" "example" {
  name                = var.nsg_name
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  security_rule {
    name                       = "test123"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

######################################################################################################################################################################
############################################################       REQUIREMENTS SECTION        #######################################################################
######################################################################################################################################################################


resource "azurerm_private_endpoint" "example" {
  name                = var.pe_name
  location            = var.rg_location
  resource_group_name = azurerm_resource_group.example.name
  subnet_id           = azurerm_subnet.endpoint.id

  private_service_connection { #3. Ensure Private access to Azure Database for PostgreSQL is enabled using Virtual networks in delegated subnets and subnet should be associated with NSG
    name                           = var.ps_name
    private_connection_resource_id = azurerm_postgresql_server.example.id
    subresource_names              = [ "postgresqlServer" ]
    is_manual_connection           = false
  }
}

resource "azurerm_subnet_network_security_group_association" "example" {
  subnet_id                 = azurerm_subnet.endpoint.id
  network_security_group_id = azurerm_network_security_group.example.id
}

resource "azurerm_postgresql_server" "example" {
  name                = var.postgre_name
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  administrator_login          = data.azurerm_key_vault_secret.admin.value
  administrator_login_password = data.azurerm_key_vault_secret.password.value

  sku_name   = var.postgre_sku
  version    = var.postgre_version
  storage_mb = 5120

#  backup_retention_days        = 7
#  geo_redundant_backup_enabled = true
#  auto_grow_enabled            = true

#  public_network_access_enabled    = false
  ssl_enforcement_enabled          = true
  ssl_minimal_tls_version_enforced = var.ssl_minimal #1. Ensure Azure Database for PostgreSQL connections are encrypted in transit using TLS1.2

  threat_detection_policy { #4. Ensure Microsoft Defender for Azure Database for PostgreSQL is enabled at the subscription level to enable security alert and Vulnerability scanning
    enabled = true
    storage_account_access_key = azurerm_storage_account.example.id
  }

  tags = var.tags #12. Ensure that Azure Database for PostgreSQL uses standard organizational Resource tagging method
}

resource "azurerm_postgresql_active_directory_administrator" "example" { #13. Ensure that PostgreSQL Authentication is disabled and Azure Database for PostgreSQL is accessed only using Azure Active Directory single sign-on (SSO)
  server_name         = azurerm_postgresql_server.example.name
  resource_group_name = azurerm_resource_group.example.name
  login               = "sqladmin"
  tenant_id           = data.azurerm_client_config.current.tenant_id
  object_id           = data.azurerm_client_config.current.object_id
}

/*
resource "azurerm_postgresql_server_key" "example" { #2. Ensure that Azure Database for PostgreSQL is encrypted using Organization's Manged keys (CMK)
  server_id        = azurerm_postgresql_server.example.id
  key_vault_key_id = azurerm_key_vault_key.example.id
}
*/

resource "azurerm_monitor_diagnostic_setting" "example" {  #10. Ensure Azure activity logging for Azure Database for PostgreSQL is enabled and forwarded to Splunk
  name               = var.mds_name
  target_resource_id = azurerm_postgresql_server.example.id
  storage_account_id = azurerm_storage_account.example.id

  log {
    category = "PostgreSQLLogs" #11. Ensure Diagnostic logs for 'PostgreSQLLogs' is Enable and forwarded to Splunk
  }
  metric {
    category = "AllMetrics"
  }
}

/*
resource "azurerm_role_assignment" "example" { #6. Ensure least privilege access method for Azure Database for PostgreSQL is implemented using Role-based access control (RBAC)
  scope                = var.ra_scope #<------- (Required) The scope at which the Role Assignment applies to the resource.
  role_definition_name = "Viewer" #<------- Role for the user or group
  principal_id         = var.ra_user #<------- User or group ID
}
*/
