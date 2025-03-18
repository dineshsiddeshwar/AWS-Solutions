module "us-east-1-securityhub" {
  source = "./Securityhub"

  cis_securityhub_controls = var.cis_aws_securityhub_controls.cis_securityhub_controls 
  aws_securityhub_controls = var.cis_aws_securityhub_controls.aws_securityhub_controls
  aws_region = "us-east-1"
  current_account_number = var.ProvisionedProduct.AccountNumber

}

 module "eu-west-1-securityhub" {
  source = "./Securityhub"

  cis_securityhub_controls = var.cis_aws_securityhub_controls.cis_securityhub_controls 
  aws_securityhub_controls = var.cis_aws_securityhub_controls.aws_securityhub_controls
  aws_region = "eu-west-1"
  current_account_number = var.ProvisionedProduct.AccountNumber
  providers = {
    aws = aws.eu-west-1
   }
}

 module "eu-west-2-securityhub" {
  source = "./Securityhub"

  cis_securityhub_controls = var.cis_aws_securityhub_controls.cis_securityhub_controls 
  aws_securityhub_controls = var.cis_aws_securityhub_controls.aws_securityhub_controls
  aws_region = "eu-west-2"
  current_account_number = var.ProvisionedProduct.AccountNumber
  providers = {
    aws = aws.eu-west-2
   }
}

module "us-east-2-securityhub" {
  source = "./Securityhub"

  cis_securityhub_controls = var.cis_aws_securityhub_controls.cis_securityhub_controls 
  aws_securityhub_controls = var.cis_aws_securityhub_controls.aws_securityhub_controls
  aws_region = "us-east-2"
  current_account_number = var.ProvisionedProduct.AccountNumber
  providers = {
    aws = aws.us-east-2
   }
}

#module "us-west-1-securityhub" {
#  source = "./Securityhub"
#
#  cis_securityhub_controls = var.cis_aws_securityhub_controls.cis_securityhub_controls 
#  aws_securityhub_controls = var.cis_aws_securityhub_controls.aws_securityhub_controls
#  aws_region = "us-west-1"
#  current_account_number = var.ProvisionedProduct.AccountNumber
#  providers = {
#    aws = aws.us-west-1
#   }
#}

module "us-west-2-securityhub" {
  source = "./Securityhub"

  cis_securityhub_controls = var.cis_aws_securityhub_controls.cis_securityhub_controls 
  aws_securityhub_controls = var.cis_aws_securityhub_controls.aws_securityhub_controls
  aws_region = "us-west-2"
  current_account_number = var.ProvisionedProduct.AccountNumber
  providers = {
    aws = aws.us-west-2
   }
}

module "ap-south-1-securityhub" {
  source = "./Securityhub"

  cis_securityhub_controls = var.cis_aws_securityhub_controls.cis_securityhub_controls 
  aws_securityhub_controls = var.cis_aws_securityhub_controls.aws_securityhub_controls
  aws_region = "ap-south-1"
  current_account_number = var.ProvisionedProduct.AccountNumber
  providers = {
    aws = aws.ap-south-1
   }
}

module "ap-southeast-2-securityhub" {
  source = "./Securityhub"

  cis_securityhub_controls = var.cis_aws_securityhub_controls.cis_securityhub_controls 
  aws_securityhub_controls = var.cis_aws_securityhub_controls.aws_securityhub_controls
  aws_region = "ap-southeast-2"
  current_account_number = var.ProvisionedProduct.AccountNumber
  providers = {
    aws = aws.ap-southeast-2
   }
}

module "ap-southeast-1-securityhub" {
  source = "./Securityhub"

  cis_securityhub_controls = var.cis_aws_securityhub_controls.cis_securityhub_controls 
  aws_securityhub_controls = var.cis_aws_securityhub_controls.aws_securityhub_controls
  aws_region = "ap-southeast-1"
  current_account_number = var.ProvisionedProduct.AccountNumber
  providers = {
    aws = aws.ap-southeast-1
   }
}

module "eu-central-1-securityhub" {
  source = "./Securityhub"

  cis_securityhub_controls = var.cis_aws_securityhub_controls.cis_securityhub_controls 
  aws_securityhub_controls = var.cis_aws_securityhub_controls.aws_securityhub_controls
  aws_region = "eu-central-1"
  current_account_number = var.ProvisionedProduct.AccountNumber
  providers = {
    aws = aws.eu-central-1
   }
}

module "ap-northeast-2-securityhub" {
  source = "./Securityhub"

  cis_securityhub_controls = var.cis_aws_securityhub_controls.cis_securityhub_controls 
  aws_securityhub_controls = var.cis_aws_securityhub_controls.aws_securityhub_controls
  aws_region = "ap-northeast-2"
  current_account_number = var.ProvisionedProduct.AccountNumber
  providers = {
    aws = aws.ap-northeast-2
   }
}

module "eu-north-1-securityhub" {
  source = "./Securityhub"

  cis_securityhub_controls = var.cis_aws_securityhub_controls.cis_securityhub_controls 
  aws_securityhub_controls = var.cis_aws_securityhub_controls.aws_securityhub_controls
  aws_region = "eu-north-1"
  current_account_number = var.ProvisionedProduct.AccountNumber
  providers = {
    aws = aws.eu-north-1
   }
}

module "ap-northeast-1-securityhub" {
  source = "./Securityhub"

  cis_securityhub_controls = var.cis_aws_securityhub_controls.cis_securityhub_controls 
  aws_securityhub_controls = var.cis_aws_securityhub_controls.aws_securityhub_controls
  aws_region = "ap-northeast-1"
  current_account_number = var.ProvisionedProduct.AccountNumber
  providers = {
    aws = aws.ap-northeast-1
   }
}

module "ca-central-1-securityhub" {
  source = "./Securityhub"

  cis_securityhub_controls = var.cis_aws_securityhub_controls.cis_securityhub_controls 
  aws_securityhub_controls = var.cis_aws_securityhub_controls.aws_securityhub_controls
  aws_region = "ca-central-1"
  current_account_number = var.ProvisionedProduct.AccountNumber
  providers = {
    aws = aws.ca-central-1
   }
}
