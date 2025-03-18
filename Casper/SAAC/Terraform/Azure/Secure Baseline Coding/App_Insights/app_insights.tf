module "name" {
  source = "../Modules/App_insights_module"

  resource_group_name = "EYGDSSECbaseline-rg"
  app_insights_name = "eygdsappinsight"
  application_type = "other"
}
