module "azsynapse" {

  source        = "../Modules/Azure_Synapse_module"
  resource_group_name = "EYGDSSECbaseline-rg"
  datalake_name = var.datalake_name
  synapse_name  = var.synapse_name

  adminlogin    = var.adminlogin
  adminpassword = var.adminpassword
  tags          = var.tags

  synapse_sql_pool = var.synapse_sql_pool
  #   sql pool

  firewallrule     = var.firewallrule
  start_ip_address = var.start_ip_address
  end_ip_address   = var.end_ip_address

  # storage_acc_id     = var.storage_acc_id
  storage_account_name= "eygdsbaselinedatalake"
  account_tier             = var.account_tier
  account_replication_type = var.account_replication_type
  account_kind             = var.account_kind

  endpoint_name    = var.endpoint_name
  subresource_name = var.subresource_name

  synapse_role = var.synapse_role
  
  synapse_spark_pool = var.synapse_spark_pool

}
