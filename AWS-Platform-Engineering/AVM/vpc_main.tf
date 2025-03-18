module "us-east-1-vpc" {
  source = "./VPC"

  RegionIpDictionary = contains(split("-", var.ProvisionedProduct.OU), "Private") || contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.RegionIpDictionary_US : tomap({})
  env_type = var.Env_type
  extension_index = var.VPC_cidr_extend_number_US
  Connectivity  = contains(split("-", var.ProvisionedProduct.OU), "Private") ? "PVT" : (contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "HYB" : "PUB")
  IsNonRoutable = var.Non_routable_requested_US
  SSMParameters = var.SSMParameters
  providers = {
    aws.sharedaccount = aws.sa-us-east-1
   }
}

module "eu-west-1-vpc" {
  source = "./VPC"

  RegionIpDictionary = contains(split("-", var.ProvisionedProduct.OU), "Private") || contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.RegionIpDictionary_EU : tomap({})
  env_type = var.Env_type
  extension_index = var.VPC_cidr_extend_number_EU
  Connectivity  = contains(split("-", var.ProvisionedProduct.OU), "Private") ? "PVT" : (contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "HYB" : "PUB")
  IsNonRoutable = var.Non_routable_requested_EU
  SSMParameters = var.SSMParameters
  providers = {
    aws = aws.eu-west-1
    aws.sharedaccount = aws.sa-eu-west-1
   }
}

module "ap-southeast-1-vpc" {
  source = "./VPC"

  RegionIpDictionary = contains(split("-", var.ProvisionedProduct.OU), "Private") || contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.RegionIpDictionary_SG : tomap({})
  env_type = var.Env_type
  extension_index = var.VPC_cidr_extend_number_SG
  Connectivity  = contains(split("-", var.ProvisionedProduct.OU), "Private") ? "PVT" : (contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "HYB" : "PUB")
  IsNonRoutable = var.Non_routable_requested_SG

  SSMParameters = var.SSMParameters
  providers = {
    aws = aws.ap-southeast-1
    aws.sharedaccount = aws.sa-ap-southeast-1
   }
}