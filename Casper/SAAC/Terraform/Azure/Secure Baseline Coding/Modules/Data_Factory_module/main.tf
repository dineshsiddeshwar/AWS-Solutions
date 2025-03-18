provider "azurerm" {
  features {
  }
}

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
  name = var.resource_group_name
}

resource "azurerm_data_factory" "dfac" {
  name                = var.df_name
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name

  dynamic "github_configuration" {
    iterator = git
    for_each = var.github_configuration
    content {
      account_name    = lookup(git.value, "account_name")
      branch_name     = lookup(git.value, "branch_name")
      git_url         = lookup(git.value, "git_url")
      repository_name = lookup(git.value, "repository_name")
      root_folder     = lookup(git.value, "root_folder", "/")
    }
  }

  identity {
    type = "SystemAssigned"
  }

  dynamic "vsts_configuration" {
    for_each = var.vsts_configuration
    iterator = vsts
    content {
      account_name    = lookup(vsts.value, "account_name")
      branch_name     = lookup(vsts.value, "branch_name")
      project_name    = lookup(vsts.value, "project_name")
      repository_name = lookup(vsts.value, "repository_name")
      root_folder     = lookup(vsts.value, "root_folder", "/")
      tenant_id       = lookup(vsts.value, "tenant_id")
    }
  }

  public_network_enabled = var.public_network_enabled

  tags = var.tags
}

resource "azurerm_data_factory_linked_service_azure_blob_storage" "dfac" {
  for_each                 = var.dataset_azure_blob
  name                     = "${each.value.dataset_name}lnksvc"
  resource_group_name      = data.azurerm_resource_group.rg.name
  data_factory_name        = azurerm_data_factory.dfac.name
  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  connection_string     = lookup(each.value, "connection_string", null)
  sas_uri               = lookup(each.value, "sas_uri", null)
  service_endpoint      = lookup(each.value, "service_endpoint", null)
  use_managed_identity  = lookup(each.value, "use_managed_identity", null)
  service_principal_id  = lookup(each.value, "service_principal_id", null)
  service_principal_key = lookup(each.value, "service_principal_key", null)
  tenant_id             = lookup(each.value, "tenant_id", null)

}

resource "azurerm_data_factory_dataset_azure_blob" "dfac" {
  for_each            = var.dataset_azure_blob
  name                = each.value.dataset_name
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name
  linked_service_name = azurerm_data_factory_linked_service_azure_blob_storage.dfac[each.key].name

  path     = lookup(each.value, "path", null)
  filename = lookup(each.value, "filename", null)

  folder = lookup(each.value, "folder", null)
  dynamic "schema_column" {
    for_each = lookup(each.value, "schema_column", {}) != {} ? [1] : []
    content {
      name        = schema_column.value.name
      type        = lookup(schema_column.value, "type", null)
      description = lookup(schema_column.value, "description", null)
    }
  }
  description           = lookup(each.value, "description", null)
  annotations           = lookup(each.value, "annotations", null)
  parameters            = lookup(each.value, "parameters", null)
  additional_properties = lookup(each.value, "additional_properties", null)
}

resource "azurerm_data_factory_linked_service_cosmosdb" "dfac" {
  for_each            = var.dataset_cosmosdb_sqlapi
  name                = "${each.value.dataset_name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  account_endpoint  = lookup(each.value, "account_endpoint", null)
  account_key       = lookup(each.value, "account_key", null)
  database          = lookup(each.value, "database", null)
  connection_string = lookup(each.value, "connection_string", null)

}

resource "azurerm_data_factory_dataset_cosmosdb_sqlapi" "dfac" {
  for_each            = var.dataset_cosmosdb_sqlapi
  name                = each.value.dataset_name
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name
  linked_service_name = azurerm_data_factory_linked_service_cosmosdb.dfac[each.key].name

  collection_name = "bar"

  folder = lookup(each.value, "folder", null)

  dynamic "schema_column" {
    for_each = lookup(each.value, "schema_column", {}) != {} ? [1] : []
    content {
      name        = schema_column.value.name
      type        = lookup(schema_column.value, "type", null)
      description = lookup(schema_column.value, "description", null)
    }
  }

  description           = lookup(each.value, "description", null)
  annotations           = lookup(each.value, "annotations", null)
  parameters            = lookup(each.value, "parameters", null)
  additional_properties = lookup(each.value, "additional_properties", null)
}

resource "azurerm_data_factory_linked_service_web" "delim_txt" {
  for_each            = var.dataset_delimited_text
  name                = "${each.value.dataset_name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  authentication_type = lookup(each.value, "authentication_type", "Anonymous")
  url                 = each.value.url
}

resource "azurerm_data_factory_dataset_delimited_text" "delim_txt" {
  for_each            = var.dataset_delimited_text
  name                = each.value.dataset_name
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name
  linked_service_name = azurerm_data_factory_linked_service_web.delim_txt[each.key].name
  folder              = lookup(each.value, "folder", null)

  dynamic "schema_column" {
    for_each = lookup(each.value, "schema_column", {}) != {} ? [1] : []
    content {
      name        = schema_column.value.name
      type        = lookup(schema_column.value, "type", null)
      description = lookup(schema_column.value, "description", null)
    }
  }

  description           = lookup(each.value, "description", null)
  annotations           = lookup(each.value, "annotations", null)
  parameters            = lookup(each.value, "parameters", null)
  additional_properties = lookup(each.value, "additional_properties", null)

  dynamic "http_server_location" {
    for_each = lookup(each.value, "http_server_location", {}) != {} ? [1] : []
    iterator = location
    content {
      relative_url = location.value.relative_url
      path         = location.value.path
      filename     = location.value.filename
    }
  }

  dynamic "azure_blob_storage_location" {
    for_each = lookup(each.value, "azure_blob_storage_location", {}) != {} ? [1] : []
    iterator = location
    content {
      container = location.value.container
      path      = location.value.path
      filename  = location.value.filename
    }
  }

  column_delimiter    = each.value.column_delimiter
  row_delimiter       = each.value.row_delimiter
  encoding            = each.value.encoding
  quote_character     = each.value.quote_character
  escape_character    = each.value.escape_character
  first_row_as_header = each.value.first_row_as_header
  null_value          = lookup(each.value, "null_value", "NULL")
  compression_codec   = lookup(each.value, "compression_codec", null)
  compression_level   = lookup(each.value, "compression_level", "Optimal")

}

resource "azurerm_data_factory_linked_service_web" "http" {
  for_each            = var.dataset_http
  name                = "${each.value.dataset_name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  authentication_type = lookup(each.value, "authentication_type", "Anonymous")
  url                 = each.value.url
}

resource "azurerm_data_factory_dataset_http" "http" {
  for_each            = var.dataset_http
  name                = each.value.dataset_name
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name
  linked_service_name = azurerm_data_factory_linked_service_web.http[each.key].name
  folder              = lookup(each.value, "folder", null)

  dynamic "schema_column" {
    for_each = lookup(each.value, "schema_column", {}) != {} ? [1] : []
    content {
      name        = schema_column.value.name
      type        = lookup(schema_column.value, "type", null)
      description = lookup(schema_column.value, "description", null)
    }
  }

  description           = lookup(each.value, "description", null)
  annotations           = lookup(each.value, "annotations", null)
  parameters            = lookup(each.value, "parameters", null)
  additional_properties = lookup(each.value, "additional_properties", null)

  relative_url   = each.value.relative_url
  request_body   = each.value.request_body
  request_method = each.value.request_method

}

resource "azurerm_data_factory_linked_service_web" "json" {
  for_each            = var.dataset_json
  name                = "${each.value.dataset_name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  authentication_type = lookup(each.value, "authentication_type", "Anonymous")
  url                 = each.value.url
}

resource "azurerm_data_factory_dataset_json" "json" {
  for_each            = var.dataset_json
  name                = each.value.dataset_name
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name
  linked_service_name = azurerm_data_factory_linked_service_web.json[each.key].name
  folder              = lookup(each.value, "folder", null)

  dynamic "schema_column" {
    for_each = lookup(each.value, "schema_column", {}) != {} ? [1] : []
    content {
      name        = schema_column.value.name
      type        = lookup(schema_column.value, "type", null)
      description = lookup(schema_column.value, "description", null)
    }
  }

  description           = lookup(each.value, "description", null)
  annotations           = lookup(each.value, "annotations", null)
  parameters            = lookup(each.value, "parameters", null)
  additional_properties = lookup(each.value, "additional_properties", null)

  dynamic "http_server_location" {
    for_each = lookup(each.value, "http_server_location", {}) != {} ? [1] : []
    iterator = location
    content {
      relative_url = location.value.relative_url
      path         = location.value.path
      filename     = location.value.filename
    }
  }

  dynamic "azure_blob_storage_location" {
    for_each = lookup(each.value, "azure_blob_storage_location", {}) != {} ? [1] : []
    iterator = location
    content {
      container = location.value.container
      path      = location.value.path
      filename  = location.value.filename
    }
  }

  encoding = lookup(each.value, "encoding", "UTF-8")
}

resource "azurerm_data_factory_linked_service_mysql" "mysql" {
  for_each            = var.dataset_mysql
  name                = "${each.value.dataset_name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  connection_string = each.value.connnection_string
}

resource "azurerm_data_factory_dataset_mysql" "mysql" {
  for_each            = var.dataset_mysql
  name                = each.value.dataset_name
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name
  linked_service_name = azurerm_data_factory_linked_service_mysql.mysql[each.key].name
  folder              = lookup(each.value, "folder", null)

  dynamic "schema_column" {
    for_each = lookup(each.value, "schema_column", {}) != {} ? [1] : []
    content {
      name        = schema_column.value.name
      type        = lookup(schema_column.value, "type", null)
      description = lookup(schema_column.value, "description", null)
    }
  }

  description           = lookup(each.value, "description", null)
  annotations           = lookup(each.value, "annotations", null)
  parameters            = lookup(each.value, "parameters", null)
  additional_properties = lookup(each.value, "additional_properties", null)

  table_name = lookup(each.value, "table_name", null)
}

resource "azurerm_data_factory_linked_service_web" "parquet" {
  for_each            = var.dataset_parquet
  name                = "${each.value.dataset_name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  authentication_type = lookup(each.value, "authentication_type", "Anonymous")
  url                 = each.value.url
}

resource "azurerm_data_factory_dataset_parquet" "parquet" {
  for_each            = var.dataset_parquet
  name                = each.value.dataset_name
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name
  linked_service_name = azurerm_data_factory_linked_service_web.parquet[each.key].name
  folder              = lookup(each.value, "folder", null)

  dynamic "schema_column" {
    for_each = lookup(each.value, "schema_column", {}) != {} ? [1] : []
    content {
      name        = schema_column.value.name
      type        = lookup(schema_column.value, "type", null)
      description = lookup(schema_column.value, "description", null)
    }
  }

  description           = lookup(each.value, "description", null)
  annotations           = lookup(each.value, "annotations", null)
  parameters            = lookup(each.value, "parameters", null)
  additional_properties = lookup(each.value, "additional_properties", null)

  dynamic "http_server_location" {
    for_each = lookup(each.value, "http_server_location", {}) != {} ? [1] : []
    iterator = location
    content {
      relative_url = location.value.relative_url
      path         = location.value.path
      filename     = location.value.filename
    }
  }

  dynamic "azure_blob_storage_location" {
    for_each = lookup(each.value, "azure_blob_storage_location", {}) != {} ? [1] : []
    iterator = location
    content {
      container = location.value.container
      path      = location.value.path
      filename  = location.value.filename
    }
  }

  compression_codec = lookup(each.value, "compression_codec", null)
}

resource "azurerm_data_factory_linked_service_postgresql" "postgresql" {
  for_each            = var.dataset_postgresql
  name                = "${each.value.dataset_name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name
  connection_string   = each.value.connection_string

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)
}

resource "azurerm_data_factory_dataset_postgresql" "postgresql" {
  for_each            = var.dataset_postgresql
  name                = each.value.dataset_name
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name
  linked_service_name = azurerm_data_factory_linked_service_postgresql.postgresql[each.key].name
  folder              = lookup(each.value, "folder", null)
  table_name          = lookup(each.value, "table_name", null)

  dynamic "schema_column" {
    for_each = lookup(each.value, "schema_column", {}) != {} ? [1] : []
    content {
      name        = schema_column.value.name
      type        = lookup(schema_column.value, "type", null)
      description = lookup(schema_column.value, "description", null)
    }
  }

  description           = lookup(each.value, "description", null)
  annotations           = lookup(each.value, "annotations", null)
  parameters            = lookup(each.value, "parameters", null)
  additional_properties = lookup(each.value, "additional_properties", null)
}

resource "azurerm_data_factory_linked_service_sql_server" "sql_server_table" {
  for_each            = var.dataset_sql_server_table
  name                = "${each.value.dataset_name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  connection_string = each.value.connnection_string

  dynamic "key_vault_password" {
    for_each = lookup(each.value, "key_vault_password", {}) != {} ? [1] : []
    iterator = vault
    content {
      linked_service_name = vault.value.linked_service_name
      secret_name         = vault.value.secret_name
    }
  }
}

resource "azurerm_data_factory_dataset_sql_server_table" "sql_server_table" {
  for_each            = var.dataset_sql_server_table
  name                = each.value.dataset_name
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name
  linked_service_name = azurerm_data_factory_linked_service_sql_server.sql_server_table[each.key].name
  folder              = lookup(each.value, "folder", null)

  dynamic "schema_column" {
    for_each = lookup(each.value, "schema_column", {}) != {} ? [1] : []
    content {
      name        = schema_column.value.name
      type        = lookup(schema_column.value, "type", null)
      description = lookup(schema_column.value, "description", null)
    }
  }

  description           = lookup(each.value, "description", null)
  annotations           = lookup(each.value, "annotations", null)
  parameters            = lookup(each.value, "parameters", null)
  additional_properties = lookup(each.value, "additional_properties", null)

  table_name = lookup(each.value, "table_name", null)
}

resource "azurerm_data_factory_integration_runtime_azure" "azure" {
  for_each            = var.azure_runtime
  name                = "${each.value.name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name
  location            = lookup(each.value, "location", data.azurerm_resource_group.rg.location)
  description         = lookup(each.value, "description", null)
  compute_type        = lookup(each.value, "compute_type", null)
  core_count          = lookup(each.value, "core_count", null)
  time_to_live_min    = lookup(each.value, "time_to_live_min", null)
}

resource "azurerm_data_factory_integration_runtime_azure_ssis" "azure_ssis" {
  for_each            = var.azure_ssis_runtime
  name                = "${each.value.name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name
  location            = lookup(each.value, "location", data.azurerm_resource_group.rg.location)
  description         = lookup(each.value, "description", null)

  node_size                        = each.value.node_size
  number_of_nodes                  = lookup(each.value, "number_of_nodes", 1)
  max_parallel_executions_per_node = lookup(each.value, "max_parallel_executions_per_node", 1)
  edition                          = lookup(each.value, "edition", "Standard")
  license_type                     = lookup(each.value, "license_type", "LicenseIncluded")

  dynamic "catalog_info" {
    for_each = lookup(each.value, "catalog_info", {}) != {} ? [1] : []
    iterator = itr
    content {
      server_endpoint        = itr.value.server_endpoint
      administrator_login    = lookup(itr.value, "administrator_login ", null)
      administrator_password = lookup(itr.value, "administrator_password", null)
      pricing_tier           = lookup(itr.value, "pricing_tier", "Standard")
    }
  }

  dynamic "custom_setup_script" {
    for_each = lookup(each.value, "custom_setup_script", {}) != {} ? [1] : []
    iterator = itr
    content {
      blob_container_uri = itr.value.blob_container_uri
      sas_token          = itr.value.sas_token
    }
  }

  dynamic "vnet_integration" {
    for_each = lookup(each.value, "vnet_integration", {}) != {} ? [1] : []
    iterator = itr
    content {
      vnet_id     = itr.value.bvnet_idlob_container_uri
      subnet_name = itr.value.subnet_name
    }
  }
}

resource "azurerm_data_factory_linked_service_azure_file_storage" "azure_file_storage_lnk" {
  for_each            = var.azure_file_storage_lnk_svc
  name                = "${each.value.name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  connection_string = each.value.connnection_string
  file_share        = lookup(each.value, "file_share", null)
}

resource "azurerm_data_factory_linked_service_azure_function" "azure_function_lnk" {
  for_each            = var.azure_function_lnk_svc
  name                = "${each.value.name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  url = each.value.url
  key = each.value.key

}

resource "azurerm_data_factory_linked_service_azure_sql_database" "azure_sql_database_lnk" {
  for_each            = var.azure_sql_database_lnk_svc
  name                = "${each.value.name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  connection_string = each.value.connnection_string
}

resource "azurerm_data_factory_linked_service_azure_table_storage" "azure_table_storage" {
  for_each            = var.azure_table_storage_lnk_svc
  name                = "${each.value.name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  connection_string = each.value.connnection_string
}

resource "azurerm_data_factory_linked_service_data_lake_storage_gen2" "data_lake_storage_gen2" {
  for_each            = var.data_lake_storage_gen2_lnk_svc
  name                = "${each.value.name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  url                   = each.value.url
  use_managed_identity  = lookup(each.value, "use_managed_identity", null)
  service_principal_id  = lookup(each.value, "service_principal_id", null)
  service_principal_key = lookup(each.value, "service_principal_key", null)
  tenant                = each.value.tenant
}

resource "azurerm_data_factory_linked_service_sftp" "sftp" {
  for_each            = var.sftp_lnk_svc
  name                = "${each.value.name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  authentication_type = each.value.authentication_type
  host                = each.value.host
  port                = each.value.port
  username            = each.value.username
  password            = each.value.password
}

resource "azurerm_data_factory_linked_service_key_vault" "snowflake_kv" {
  # for_each            = var.key_vault_lnk_svc
  for_each = {
    for key, val in var.snowflake_lnk_svc :
    key => val
    if try(val.key_vault_id, "") != ""
  }
  name                = "${each.value.name}kvlink"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  key_vault_id = each.value.key_vault_id
}

resource "azurerm_data_factory_linked_service_snowflake" "snowflake" {
  for_each            = var.snowflake_lnk_svc
  name                = "${each.value.dataset_name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  connection_string = each.value.connection_string
  dynamic "key_vault_password" {
    for_each = lookup(each.value, "key_vault_id", {}) != {} ? [1] : []
    content {
      linked_service_name = azurerm_data_factory_linked_service_key_vault.snowflake_kv[each.key].name
      secret_name         = each.value.secret_name
    }
  }
}

resource "azurerm_data_factory_linked_service_key_vault" "synapse_kv" {
  # for_each            = var.key_vault_lnk_svc
  for_each = {
    for key, val in var.synapse_lnk_svc :
    key => val
    if try(val.key_vault_id, "") != ""
  }
  name                = "${each.value.name}kvlink"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  key_vault_id = each.value.key_vault_id
}

resource "azurerm_data_factory_linked_service_synapse" "synapse" {
  for_each            = var.synapse_lnk_svc
  name                = "${each.value.dataset_name}lnksvc"
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  integration_runtime_name = lookup(each.value, "integration_runtime_name", null)
  description              = lookup(each.value, "description", null)
  annotations              = lookup(each.value, "annotations", null)
  parameters               = lookup(each.value, "parameters", null)
  additional_properties    = lookup(each.value, "additional_properties", null)

  connection_string = each.value.connection_string
  dynamic "key_vault_password" {
    for_each = lookup(each.value, "key_vault_id", {}) != {} ? [1] : []
    content {
      linked_service_name = azurerm_data_factory_linked_service_key_vault.synapse_kv[each.key].name
      secret_name         = each.value.secret_name
    }
  }
}

resource "azurerm_data_factory_pipeline" "df_pipeline" {
  for_each            = var.df_pipeline
  name                = each.value.name
  resource_group_name = data.azurerm_resource_group.rg.name
  data_factory_name   = azurerm_data_factory.dfac.name

  description           = lookup(each.value, "description", null)
  annotations           = lookup(each.value, "annotations", null)
  parameters            = lookup(each.value, "parameters", null)  

  activities_json = lookup(each.value, "activities_json", null)
}

resource "azurerm_data_factory_trigger_schedule" "trigger_schedule" {
  for_each            = var.df_pipeline
  name                = each.value.trigger_name
  data_factory_name   = azurerm_data_factory.dfac.name
  resource_group_name = data.azurerm_resource_group.rg.name
  pipeline_name       = azurerm_data_factory_pipeline.df_pipeline[each.key].name

  start_time          = lookup(each.value, "start_time", null)
  end_time            = lookup(each.value, "end_time", null)
  interval            = lookup(each.value, "interval", null)
  frequency           = lookup(each.value, "frequency", null)
  pipeline_parameters = lookup(each.value, "pipeline_parameters", null)
  annotations         = lookup(each.value, "annotations", null)
}


# azurerm_data_factory.dfac

module "monitoring" {
  source = "../Diagnostic_module"
  name = azurerm_data_factory.dfac.name
  resource_id = azurerm_data_factory.dfac.id
}

