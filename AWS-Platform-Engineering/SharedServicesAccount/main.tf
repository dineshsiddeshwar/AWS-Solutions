# IAM MODULE 
module "iam-module" {
  source = "./modules/IAM"
  platform_cloudhealth_account     = var.iam.platform_cloudhealth_account
  platform_cloudhealth_external_id = var.iam.platform_cloudhealth_external_id
  platform_shared_account = var.iam.platform_shared_account
  s3_bucket = var.iam.s3_bucket
  env_instanceprofile_suffix = var.env_instanceprofile_suffix
  providers = {
    aws = aws.sa-us-east-1
   }
}


# VPC MODULE FOR us-east-1
module "vpc-module-us-east-1" {
  source = "./modules/VPC"

  vpc_cidr_details = var.vpc_all_details["us-east-1"].action_type
  env_type = var.env_type
  isproduction = var.isproduction
  providers = {
    aws = aws.sa-us-east-1
   }
}

#VPC MODULE FOR eu-west-1
module "vpc-module-eu-west-1" {
  source = "./modules/VPC"

  vpc_cidr_details = var.vpc_all_details["eu-west-1"].action_type
  env_type = var.env_type
  isproduction = var.isproduction
  providers = {
    aws = aws.sa-eu-west-1
   }
}

# VPC MODULE FOR ap-southeast-1
module "vpc-module-ap-southeast-1" {
  source = "./modules/VPC"

  vpc_cidr_details = var.vpc_all_details["ap-southeast-1"].action_type
  env_type = var.env_type
  isproduction = var.isproduction
  providers = {
    aws = aws.sa-ap-southeast-1
   }
   
}

# SECURITYGROUP MODULE FOR us-east-1
module "sg-module-us-east-1" {
  source = "./modules/SecurityGroup"

  
  vpc_id = tostring(module.vpc-module-us-east-1.vpc_id)
  
  name = var.vpc_all_details["us-east-1"].action_type["createVPC"].securitygroupname
  ingress_cidr_blocks = var.vpc_all_details["us-east-1"].action_type["createVPC"].private
  rules = var.rules
  ingress_rules = var.ingress_rules
  providers = {
    aws = aws.sa-us-east-1
   }
}

# SECURITYGROUP MODULE FOR eu-west-1
module "sg-module-eu-west-1" {
  source = "./modules/SecurityGroup"

  vpc_id = tostring(module.vpc-module-eu-west-1.vpc_id)
  name = var.vpc_all_details["eu-west-1"].action_type["createVPC"].securitygroupname
  ingress_cidr_blocks = var.vpc_all_details["eu-west-1"].action_type["createVPC"].private
  rules = var.rules
  ingress_rules = var.ingress_rules
  providers = {
    aws = aws.sa-eu-west-1
   }
}

# SECURITYGROUP MODULE FOR ap-southeast-1
module "sg-module-ap-southeast-1" {
  source = "./modules/SecurityGroup"


  vpc_id = tostring(module.vpc-module-ap-southeast-1.vpc_id)
  name = var.vpc_all_details["ap-southeast-1"].action_type["createVPC"].securitygroupname
  ingress_cidr_blocks = var.vpc_all_details["ap-southeast-1"].action_type["createVPC"].private
  rules = var.rules
  ingress_rules = var.ingress_rules
  providers = {
    aws = aws.sa-ap-southeast-1
   }
   
}

# ROUTE53 MODULE FOR us-east-1
module "route53-module-us-east-1" {
  source = "./modules/Route53"
  Infoblox1 = var.vpc_all_details["us-east-1"].action_type["createVPC"].Infoblox1
  Infoblox2 = var.vpc_all_details["us-east-1"].action_type["createVPC"].Infoblox2
  
  security_group_ids=[module.sg-module-us-east-1.security_group_id]
  endpoint_ips_subnet1a = var.vpc_all_details["us-east-1"].action_type["createVPC"].subnets["subnet1a"].route53_iplist
  endpoint_ips_subnet1b = var.vpc_all_details["us-east-1"].action_type["createVPC"].subnets["subnet1b"].route53_iplist
  sharedsubnet1a = module.vpc-module-us-east-1.sharedsubnet1a
  sharedsubnet1b = module.vpc-module-us-east-1.sharedsubnet1b
  ou_principals = var.ou_principals
  region= "us-east-1"
  vpc_id = tostring(module.vpc-module-us-east-1.vpc_id)
  
  providers = {
    aws = aws.sa-us-east-1
   }
}

# ROUTE53 MODULE FOR eu-west-1
module "route53-module-eu-west-1" {
  source = "./modules/Route53"
  Infoblox1 = var.vpc_all_details["eu-west-1"].action_type["createVPC"].Infoblox1
  Infoblox2 = var.vpc_all_details["eu-west-1"].action_type["createVPC"].Infoblox2
  
  security_group_ids=[module.sg-module-eu-west-1.security_group_id]
  endpoint_ips_subnet1a = var.vpc_all_details["eu-west-1"].action_type["createVPC"].subnets["subnet1a"].route53_iplist
  endpoint_ips_subnet1b = var.vpc_all_details["eu-west-1"].action_type["createVPC"].subnets["subnet1b"].route53_iplist
  
  sharedsubnet1a = module.vpc-module-eu-west-1.sharedsubnet1a
  sharedsubnet1b = module.vpc-module-eu-west-1.sharedsubnet1b
  ou_principals = var.ou_principals
  region= "eu-west-1"
  vpc_id = tostring(module.vpc-module-eu-west-1.vpc_id)
  providers = {
    aws = aws.sa-eu-west-1
   }
}

# ROUTE53 MODULE FOR ap-southeast-1
module "route53-module-ap-southeast-1" {
  source = "./modules/Route53"
  Infoblox1 = var.vpc_all_details["ap-southeast-1"].action_type["createVPC"].Infoblox1
  Infoblox2 = var.vpc_all_details["ap-southeast-1"].action_type["createVPC"].Infoblox2
  
  security_group_ids=[module.sg-module-ap-southeast-1.security_group_id]
  
  endpoint_ips_subnet1a = var.vpc_all_details["ap-southeast-1"].action_type["createVPC"].subnets["subnet1a"].route53_iplist
  endpoint_ips_subnet1b = var.vpc_all_details["ap-southeast-1"].action_type["createVPC"].subnets["subnet1b"].route53_iplist
  sharedsubnet1a = module.vpc-module-ap-southeast-1.sharedsubnet1a
  sharedsubnet1b = module.vpc-module-ap-southeast-1.sharedsubnet1b
  ou_principals = var.ou_principals
  region= "ap-southeast-1"
  vpc_id = tostring(module.vpc-module-ap-southeast-1.vpc_id)
  providers = {
    aws = aws.sa-ap-southeast-1
   }
}

# vpcEndpoint MODULE FOR us-east-1
module "vpcendpoint-module-us-east-1" {
  source = "./modules/vpc_endpoints"

  vpc_id = tostring(module.vpc-module-us-east-1.vpc_id)
  security_group_ids=[module.sg-module-us-east-1.security_group_id]
  isproduction = var.isproduction
  endpoints = var.endpoints
  endpoint_extended = var.endpoint_extended
  env_type=var.env_type
  sharedsubnet1a = module.vpc-module-us-east-1.sharedsubnet1a
  sharedsubnet1b = module.vpc-module-us-east-1.sharedsubnet1b
  sharedsubnet2a = module.vpc-module-us-east-1.sharedsubnet2a
  sharedsubnet2b =  module.vpc-module-us-east-1.sharedsubnet2b
  region= "us-east-1"
  providers = {
    aws = aws.sa-us-east-1
   }
}

# vpcEndpoint MODULE FOR eu-west-1
module "vpcendpoint-module-eu-west-1" {
  source = "./modules/vpc_endpoints"

  vpc_id=tostring(module.vpc-module-eu-west-1.vpc_id)
  security_group_ids=[module.sg-module-eu-west-1.security_group_id]
  isproduction = var.isproduction
  endpoints = var.endpoints
  endpoint_extended = var.endpoint_extended
  env_type=var.env_type
  sharedsubnet1a = module.vpc-module-eu-west-1.sharedsubnet1a
  sharedsubnet1b = module.vpc-module-eu-west-1.sharedsubnet1b
  sharedsubnet2a = module.vpc-module-eu-west-1.sharedsubnet2a
  sharedsubnet2b = module.vpc-module-eu-west-1.sharedsubnet2b
  region= "eu-west-1"
  providers = {
    aws = aws.sa-eu-west-1
   }
}

# vpcEndpoint MODULE FOR ap-southeast-1
module "vpcendpoint-module-ap-southeast-1" {
  source = "./modules/vpc_endpoints"

  vpc_id=tostring(module.vpc-module-ap-southeast-1.vpc_id)
  security_group_ids=[module.sg-module-ap-southeast-1.security_group_id]
  isproduction = var.isproduction
  endpoints = var.endpoints
  endpoint_extended = var.endpoint_extended
  env_type=var.env_type
  sharedsubnet1a = module.vpc-module-ap-southeast-1.sharedsubnet1a
  sharedsubnet1b = module.vpc-module-ap-southeast-1.sharedsubnet1b
  sharedsubnet2a = module.vpc-module-ap-southeast-1.sharedsubnet2a
  sharedsubnet2b = module.vpc-module-ap-southeast-1.sharedsubnet2b
  region= "ap-southeast-1"
  providers = {
    aws = aws.sa-ap-southeast-1
   }
}


