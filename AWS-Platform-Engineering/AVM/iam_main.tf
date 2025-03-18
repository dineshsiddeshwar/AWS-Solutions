module "us-east-1-iam" {
  source = "./IAM"

  platform_cloudhealth_account     = var.SSMParameters.platform_cloudhealth_account
  platform_cloudhealth_external_id = var.SSMParameters.platform_cloudhealth_external_id
  master_account_number            = var.SSMParameters.admin_account
  FlexeraBeaconServer              = contains(split("-", var.ProvisionedProduct.OU), "Private") || contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "093543580259" : "443534543078"
  IsIOTAccountrequested            = var.RequestEventData.IsIOTAccount
  Connectivity                     = contains(split("-", var.ProvisionedProduct.OU), "Private") ? "PVT" : (contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "HYB" : "PUB")
  Env_type                         = var.Env_type
  child_accountnumber              = var.ProvisionedProduct.AccountNumber
  platform_cloudhealth_bucket      = var.SSMParameters.platform_cloudhealth_bucket

}
