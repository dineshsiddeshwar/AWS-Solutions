module "us-east-1-ebs" {
  source = "./EBS"
  SSMParameters = var.SSMParameters
}

module "eu-west-1-ebs" {
  source = "./EBS"
  SSMParameters = var.SSMParameters
  providers = {
    aws = aws.eu-west-1
   }
}

module "eu-west-2-ebs" {
  source = "./EBS"
  
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  providers = {
    aws = aws.eu-west-2
   }
}

module "us-east-2-ebs" {
  source = "./EBS"
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  providers = {
    aws = aws.us-east-2
   }
}

module "us-west-1-ebs" {
  source = "./EBS"
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  providers = {
    aws = aws.us-west-1
   }
}

module "us-west-2-ebs" {
  source = "./EBS"
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  providers = {
    aws = aws.us-west-2
   }
}

module "ap-south-1-ebs" {
  source = "./EBS"
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  providers = {
    aws = aws.ap-south-1
   }
}

module "ap-southeast-2-ebs" {
  source = "./EBS"
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  providers = {
    aws = aws.ap-southeast-2
   }
}

module "ap-southeast-1-ebs" {
  source = "./EBS"
  SSMParameters = var.SSMParameters
  providers = {
    aws = aws.ap-southeast-1
   }
}

module "eu-central-1-ebs" {
  source = "./EBS"
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  providers = {
    aws = aws.eu-central-1
   }
}

module "ap-northeast-2-ebs" {
  source = "./EBS"
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  providers = {
    aws = aws.ap-northeast-2
   }
}

module "eu-north-1-ebs" {
  source = "./EBS"
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  providers = {
    aws = aws.eu-north-1
   }
}

module "ap-northeast-1-ebs" {
  source = "./EBS"
  
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  providers = {
    aws = aws.ap-northeast-1
   }
}

module "ca-central-1-ebs" {
  source = "./EBS"
  SSMParameters =  !contains(split("-", var.ProvisionedProduct.OU), "Private") && !contains(split("-", var.ProvisionedProduct.OU), "Hybrid") ? var.SSMParameters : tomap({})
  providers = {
    aws = aws.ca-central-1
   }
}