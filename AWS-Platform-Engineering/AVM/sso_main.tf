module "us-east-1-sso" {
  source = "./SSO"

    child_account_number = var.ProvisionedProduct.AccountNumber
    SSMParameters = var.SSMParameters
    providers = {
    aws.pa-us-east-1 = aws.pa-us-east-1
   }

   depends_on = [ module.us-east-1-iam ]
}