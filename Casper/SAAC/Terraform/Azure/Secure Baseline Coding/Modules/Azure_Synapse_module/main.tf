locals {
  storage_account_id = element(coalescelist([var.storage_acc_id], azurerm_storage_account.storage_connect.*.id, [""]), 0)
  principal_id       = var.principal_id != "" ? var.principal_id : data.azurerm_client_config.current.object_id
  resource_group_name = element(coalescelist(data.azurerm_resource_group.rgrp.*.name, azurerm_resource_group.rg.*.name, [""]), 0)
  location            = element(coalescelist(data.azurerm_resource_group.rgrp.*.location, azurerm_resource_group.rg.*.location, [""]), 0)
}

data azurerm_resource_group "rgrp" {
  count = var.create_resource_group == false ? 1 : 0
  name = var.resource_group_name
}

resource "azurerm_resource_group" "rg" {
  count    = var.create_resource_group ? 1 : 0
  name     = var.resource_group_name
  location = var.location
  tags     = merge({ "Name" = format("%s", var.resource_group_name) }, var.tags, )
}

data "azurerm_client_config" "current" {}

resource "azurerm_storage_data_lake_gen2_filesystem" "storagefs" {
  name               = var.datalake_name
  storage_account_id = local.storage_account_id
}

resource "azurerm_synapse_workspace" "azsynapse" {
  name                                 = var.synapse_name
  resource_group_name                  = local.resource_group_name
  location                             = local.location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.storagefs.id
  sql_administrator_login              = var.adminlogin
  sql_administrator_login_password     = var.adminpassword
  managed_virtual_network_enabled      = var.managed_virtual_network_enabled
  sql_identity_control_enabled         = var.sql_identity_control_enabled
  managed_resource_group_name          = var.managed_resource_group_name != "" ? var.managed_resource_group_name : null
  tags                                 = var.tags

  dynamic "aad_admin" {
    for_each = var.aad_admin != null ? [var.aad_admin] : []
    content {
      login     = aad_admin.value.login
      object_id = aad_admin.value.object_id
      tenant_id = aad_admin.value.tenant_id
    }
  }

  dynamic "azure_devops_repo" {
    for_each = var.azure_devops_repo != null ? [var.azure_devops_repo] : []
    content {
      account_name = azure_devops_repo.value.account_name
      branch_name = azure_devops_repo.value.branch_name
      project_name = azure_devops_repo.value.project_name
      repository_name = azure_devops_repo.value.repository_name
      root_folder = lookup(azure_devops_repo.value, "root_folder", "/")
    }
  }

  dynamic "github_repo" {
    for_each = var.github_repo != null ? [var.github_repo] : []
    content {
      account_name = github_repo.value.account_name
      branch_name = github_repo.value.branch_name
      repository_name = github_repo.value.repository_name
      root_folder = lookup(github_repo.value, "root_folder", "/")
      git_url = lookup(github_repo.value, "git_url", null)
    }
  }
}

resource "azurerm_synapse_sql_pool" "sqlpool" {
  for_each             = var.synapse_sql_pool
  name                 = each.key
  synapse_workspace_id = azurerm_synapse_workspace.azsynapse.id
  sku_name             = lookup(each.value, "sku_name", "DW100c")

  collation = lookup(each.value, "collation", null)
  create_mode    = lookup(each.value, "create_mode", "Default")
  data_encrypted = lookup(each.value, "data_encrypted", false)
  recovery_database_id = lookup(each.value, "recovery_database_id", null)
  
  dynamic "restore" {
    for_each = lookup(each.value, "restore", {})
    content {
      source_database_id = lookup(restore.value, "source_database_id", null)
      point_in_time = lookup(restore.value, "point_in_time", null)
    }
  }

}

resource "azurerm_synapse_firewall_rule" "synapsefwrule" {
  name                 = var.firewallrule
  synapse_workspace_id = azurerm_synapse_workspace.azsynapse.id
  start_ip_address     = var.start_ip_address
  end_ip_address       = var.end_ip_address
}

resource "azurerm_storage_account" "storage_connect" {
  count                    = var.storage_account_name != "" ? 1 : 0
  name                     = var.storage_account_name
  resource_group_name      = local.resource_group_name
  location                 = local.location
  account_tier             = var.account_tier
  account_replication_type = var.account_replication_type
  account_kind             = var.account_kind
  is_hns_enabled           = "true"
}

resource "azurerm_synapse_managed_private_endpoint" "pvt_endoint" {
  name                 = var.endpoint_name
  synapse_workspace_id = azurerm_synapse_workspace.azsynapse.id
  target_resource_id   = local.storage_account_id
  subresource_name     = var.subresource_name
  depends_on           = [azurerm_synapse_firewall_rule.synapsefwrule]
}

resource "azurerm_synapse_role_assignment" "azsynapse_role" {
  synapse_workspace_id = azurerm_synapse_workspace.azsynapse.id
  role_name            = var.synapse_role
  principal_id         = local.principal_id

  depends_on = [azurerm_synapse_firewall_rule.synapsefwrule]
}

resource "azurerm_synapse_spark_pool" "sparkpool" {
  for_each = var.synapse_spark_pool

  name                 = each.key
  synapse_workspace_id = azurerm_synapse_workspace.azsynapse.id
  node_size_family     = each.value.node_size_family
  # lookup(each.value, "node_size_family", "MemoryOptimized")
  node_size = lookup(each.value, "node_size", "Small")
  # node_count should be in the range (3 - 200)
  node_count = lookup(each.value, "node_count", null)

  dynamic "auto_scale" {
    for_each = lookup(each.value, "auto_scale", {})
    content {
      max_node_count = auto_scale.value.max_node_count
      min_node_count = auto_scale.value.min_node_count
    }
  }

  dynamic "auto_pause" {
    for_each = lookup(each.value, "auto_pause", {})
    content {
      delay_in_minutes = auto_pause.value.delay_in_minutes
    }
  }

  dynamic "library_requirement" {
    for_each = lookup(each.value, "library_requirement", {})
    content {
      content = library_requirement.value.content
      filename = library_requirement.value.filename
    }
  }

  spark_log_folder = lookup(each.value, "spark_log_folder", "/logs")
  spark_events_folder = lookup(each.value, "spark_events_folder", "/events")
  spark_version = "2.4"
  tags = var.tags

}

module "monitoring" {
  source = "../Diagnostic_module"
  name = azurerm_synapse_workspace.azsynapse.name
  resource_id = azurerm_synapse_workspace.azsynapse.id
}

resource "azurerm_advanced_threat_protection" "example" {
  target_resource_id = azurerm_synapse_workspace.azsynapse.id
  enabled            = true
}
