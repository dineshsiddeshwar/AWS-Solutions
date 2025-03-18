module "us-east-1" {
  source = "./Config"

  ProvisionedProduct = var.ProvisionedProduct
  RequestEventData = var.RequestEventData
  SSMParameters =   var.SSMParameters
  Connectivity  =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "PUB" : "PVT"
}

module "eu-west-1" {
  source = "./Config"


  ProvisionedProduct = var.ProvisionedProduct
  RequestEventData = var.RequestEventData
  SSMParameters =   var.SSMParameters
  Connectivity  =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "PUB" : "PVT"
  providers = {
    aws = aws.eu-west-1
   }
}

module "eu-west-2" {
  source = "./Config"


  ProvisionedProduct = var.ProvisionedProduct
  RequestEventData = var.RequestEventData
  SSMParameters =  var.SSMParameters
  Connectivity  =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "PUB" : "PVT"
  providers = {
    aws = aws.eu-west-2
   }
}

module "us-east-2" {
  source = "./Config"

  ProvisionedProduct = var.ProvisionedProduct
  RequestEventData = var.RequestEventData
  SSMParameters =  var.SSMParameters
  Connectivity  =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "PUB" : "PVT"
  providers = {
    aws = aws.us-east-2
   }
}

module "us-west-1" {
  source = "./Config"


  ProvisionedProduct = var.ProvisionedProduct
  RequestEventData = var.RequestEventData
  SSMParameters =  var.SSMParameters
  Connectivity  =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "PUB" : "PVT"
  providers = {
    aws = aws.us-west-1
   }
}

module "us-west-2" {
  source = "./Config"

  ProvisionedProduct = var.ProvisionedProduct
  RequestEventData = var.RequestEventData
  SSMParameters =  var.SSMParameters
  Connectivity  =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "PUB" : "PVT"
  providers = {
    aws = aws.us-west-2
   }
}

module "ap-south-1" {
  source = "./Config"

  ProvisionedProduct = var.ProvisionedProduct
  RequestEventData = var.RequestEventData
  SSMParameters =  var.SSMParameters
  Connectivity  =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "PUB" : "PVT"
  providers = {
    aws = aws.ap-south-1
   }
}

module "ap-southeast-2" {
  source = "./Config"

  ProvisionedProduct = var.ProvisionedProduct
  RequestEventData = var.RequestEventData
  SSMParameters =  var.SSMParameters
  Connectivity  =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "PUB" : "PVT"
  providers = {
    aws = aws.ap-southeast-2
   }
}

module "ap-southeast-1" {
  source = "./Config"

  ProvisionedProduct = var.ProvisionedProduct
  RequestEventData = var.RequestEventData
  SSMParameters =  var.SSMParameters
  Connectivity  =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "PUB" : "PVT"
  providers = {
    aws = aws.ap-southeast-1
   }
}

module "eu-central-1" {
  source = "./Config"

  ProvisionedProduct = var.ProvisionedProduct
  RequestEventData = var.RequestEventData
  SSMParameters =  var.SSMParameters
  Connectivity  =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "PUB" : "PVT"
  providers = {
    aws = aws.eu-central-1
   }
}

module "ap-northeast-2" {
  source = "./Config"

  ProvisionedProduct = var.ProvisionedProduct
  RequestEventData = var.RequestEventData
  SSMParameters =   var.SSMParameters
  Connectivity  =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "PUB" : "PVT"
  providers = {
    aws = aws.ap-northeast-2
   }
}

module "eu-north-1" {
 source = "./Config"

  ProvisionedProduct = var.ProvisionedProduct
  RequestEventData = var.RequestEventData
  SSMParameters = var.SSMParameters
  Connectivity  =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "PUB" : "PVT"
  providers = {
    aws = aws.eu-north-1
   }
}

module "ap-northeast-1" {
  source = "./Config"

  ProvisionedProduct = var.ProvisionedProduct
  RequestEventData = var.RequestEventData
  SSMParameters =  var.SSMParameters
  Connectivity  =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "PUB" : "PVT"
  providers = {
    aws = aws.ap-northeast-1
   }
}

module "ca-central-1-config" {
  source = "./Config"

  ProvisionedProduct = var.ProvisionedProduct
  RequestEventData = var.RequestEventData
  SSMParameters =  var.SSMParameters
  Connectivity  =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? "PUB" : "PVT"
  providers = {
    aws = aws.ca-central-1
   }
}
