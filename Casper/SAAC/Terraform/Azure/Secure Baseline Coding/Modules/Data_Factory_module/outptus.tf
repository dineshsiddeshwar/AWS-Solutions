output "data_factory_id" {
  value = azurerm_data_factory.dfac.id
}

output "data_factory_principal_id" {
  value = azurerm_data_factory.dfac.identity.*.principal_id
}

# output "data_factory_pipeline_ids" {
#   value = azurerm_data_factory_pipeline.df_pipeline.*.id
# }
