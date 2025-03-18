module "us-east-1-backup" {
  source = "./Backup"
  dloftheAccount = var.ProvisionedProduct.AccountDL
  SSMParameters = var.SSMParameters
  child_accountnumber = var.ProvisionedProduct.AccountNumber
}

module "eu-west-1-backup" {
  source = "./Backup"
  dloftheAccount = var.ProvisionedProduct.AccountDL
  SSMParameters = var.SSMParameters
  child_accountnumber = var.ProvisionedProduct.AccountNumber

providers = {
    aws = aws.eu-west-1
   }
}


module "eu-west-2-backup" {
  source = "./Backup"
  dloftheAccount = var.ProvisionedProduct.AccountDL
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  child_accountnumber = var.ProvisionedProduct.AccountNumber

providers = {
    aws = aws.eu-west-2
   }
}

module "us-east-2-backup" {
  source = "./Backup"
  dloftheAccount = var.ProvisionedProduct.AccountDL
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  child_accountnumber = var.ProvisionedProduct.AccountNumber

providers = {
    aws = aws.us-east-2
   }
}

module "us-west-1-backup" {
  source = "./Backup"
  dloftheAccount = var.ProvisionedProduct.AccountDL
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  child_accountnumber = var.ProvisionedProduct.AccountNumber
providers = {
    aws = aws.us-west-1
   }
}

module "us-west-2-backup" {
  source = "./Backup"
  dloftheAccount = var.ProvisionedProduct.AccountDL
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  child_accountnumber = var.ProvisionedProduct.AccountNumber
providers = {
    aws = aws.us-west-2
   }
}

module "ap-south-1-backup" {
  source = "./Backup"
  dloftheAccount = var.ProvisionedProduct.AccountDL
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  child_accountnumber = var.ProvisionedProduct.AccountNumber
providers = {
    aws = aws.ap-south-1
   }
}

module "ap-southeast-2-backup" {
  source = "./Backup"
  dloftheAccount = var.ProvisionedProduct.AccountDL
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  child_accountnumber = var.ProvisionedProduct.AccountNumber
providers = {
    aws = aws.ap-southeast-2
   }
}

module "ap-southeast-1-backup" {
  source = "./Backup"
  dloftheAccount = var.ProvisionedProduct.AccountDL
  SSMParameters = var.SSMParameters
  child_accountnumber = var.ProvisionedProduct.AccountNumber
providers = {
    aws = aws.ap-southeast-1
   }
}

module "eu-central-1-backup" {
  source = "./Backup"
  dloftheAccount = var.ProvisionedProduct.AccountDL
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  child_accountnumber = var.ProvisionedProduct.AccountNumber
providers = {
    aws = aws.eu-central-1
   }
}

module "ap-northeast-2-backup" {
  source = "./Backup"
  dloftheAccount = var.ProvisionedProduct.AccountDL
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  child_accountnumber = var.ProvisionedProduct.AccountNumber
providers = {
    aws = aws.ap-northeast-2
   }
}

module "eu-north-1-backup" {
  source = "./Backup"
  dloftheAccount = var.ProvisionedProduct.AccountDL
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  child_accountnumber = var.ProvisionedProduct.AccountNumber
providers = {
    aws = aws.eu-north-1
   }
}

module "ap-northeast-1-backup" {
  source = "./Backup"
  dloftheAccount = var.ProvisionedProduct.AccountDL
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  child_accountnumber = var.ProvisionedProduct.AccountNumber
providers = {
    aws = aws.ap-northeast-1
   }
}

module "ca-central-1-backup" {
  source = "./Backup"
  dloftheAccount = var.ProvisionedProduct.AccountDL
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  child_accountnumber = var.ProvisionedProduct.AccountNumber
providers = {
    aws = aws.ca-central-1
   }
}