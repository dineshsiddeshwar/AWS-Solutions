module "iam" {
  source = "./IAM"
  platform_cloudhealth_external_id = var.platform_cloudhealth_external_id
  platform_cloudhealth_account = var.platform_cloudhealth_account
  s3_bucket = var.s3_bucket
  service_now_itom_discovery_child_instance_profile = var.service_now_itom_discovery_child_instance_profile
  account_id = var.account_id
  payer_account_id = var.payer_account_id
  notifyRole_id = var.notifyRole_id
  customactionrole_id = var.customactionrole_id
  orchestratorrole_id = var.orchestratorrole_id
  remediatewithsharreventsrule_id = var.remediatewithsharreventsrule_id
  cis41eventsrulerole_id = var.cis41eventsrulerole_id
}

module "us-east-1" {
  source = "./Lambda"
  region = "us-east-1"
  env_type = var.env_type
  event_rule_name = var.event_rule_name
  rule_id = var.rule_id
  sechublambda = 1
}


module "eu-west-1" {
  source = "./Lambda"
  region = "eu-west-1"
  env_type = var.env_type
  event_rule_name = var.event_rule_name
  rule_id = var.rule_id
  sechublambda = 0
  providers = {
    aws = aws.eu-west-1
   }
}

module "us-east-2" {
  source = "./Lambda"
  region = "us-east-2"
  env_type = var.env_type
  event_rule_name = var.event_rule_name
  rule_id = var.rule_id
  sechublambda = 0
  providers = {
    aws = aws.us-east-2
   }
}

module "us-west-1" {
  source = "./Lambda"
  region = "us-west-1"
  env_type = var.env_type
  event_rule_name = var.event_rule_name
  rule_id = var.rule_id
  sechublambda = 0
  
  providers = {
    aws = aws.us-west-1
   }
}

module "us-west-2" {
  source = "./Lambda"
  region = "us-west-2"
  env_type = var.env_type
  event_rule_name = var.event_rule_name
  rule_id = var.rule_id
  sechublambda = 0
  providers = {
    aws = aws.us-west-2
   }
}

module "ap-south-1" {
  source = "./Lambda"
  region = "ap-south-1"
  env_type = var.env_type
  event_rule_name = var.event_rule_name
  rule_id = var.rule_id
  sechublambda = 0
  providers = {
    aws = aws.ap-south-1
   }
}

module "ap-southeast-2" {
  source = "./Lambda"
  region = "ap-southeast-2"
  env_type = var.env_type
  event_rule_name = var.event_rule_name
  rule_id = var.rule_id
  sechublambda = 0
  providers = {
    aws = aws.ap-southeast-2
   }
}

module "ap-southeast-1" {
  source = "./Lambda"
  region = "ap-southeast-1"
  env_type = var.env_type
  event_rule_name = var.event_rule_name
  rule_id = var.rule_id
  sechublambda = 0
  providers = {
    aws = aws.ap-southeast-1
   }
}

module "eu-central-1" {
  source = "./Lambda"
  region = "eu-central-1"
  env_type = var.env_type
  event_rule_name = var.event_rule_name
  rule_id = var.rule_id
  sechublambda = 0
  providers = {
    aws = aws.eu-central-1
   }
}

module "ap-northeast-2" {
  source = "./Lambda"
  region = "ap-northeast-2"
  env_type = var.env_type
  event_rule_name = var.event_rule_name
  rule_id = var.rule_id
  sechublambda = 0
  providers = {
    aws = aws.ap-northeast-2
   }
}

module "eu-north-1" {
  source = "./Lambda"
  region = "eu-north-1"
  env_type = var.env_type
  event_rule_name = var.event_rule_name
  rule_id = var.rule_id
  sechublambda = 0
  providers = {
    aws = aws.eu-north-1
   }
}

module "ap-northeast-1" {
  source = "./Lambda"
  region = "ap-northeast-1"
  env_type = var.env_type
  event_rule_name = var.event_rule_name
  rule_id = var.rule_id
  sechublambda = 0
  providers = {
    aws = aws.ap-northeast-1
   }
}

module "ca-central-1" {
  source = "./Lambda"
  region = "ca-central-1"
  env_type = var.env_type
  event_rule_name = var.event_rule_name
  rule_id = var.rule_id
  sechublambda = 0
  providers = {
    aws = aws.ca-central-1
   }
}

module "ssm" {
  source = "./SSM"
}

module "securityhub" {
  source = "./SecurityHub"
}

module "kms" {
  source = "./KMS"
  account_id = var.account_id

}

module "sns" {
  source = "./SNS"
}

module "sf" {
  source = "./StepFunction"
  account_id = var.account_id
  orchestratorrole_id = var.orchestratorrole_id
}

module "sharr" {
  source = "./Sharr"
  account_id = var.account_id
  payer_account_id = var.payer_account_id
  CIS41AutoEventRule_statement_id = var.CIS41AutoEventRule_statement_id
  SCEC214AutoEventRule_statement_id = var.SCEC214AutoEventRule_statement_id
  SCEC213AutoEventRule_statement_id = var.SCEC213AutoEventRule_statement_id
  CIS42AutoEventRule_statement_id = var.CIS42AutoEventRule_statement_id
  notifyRole_id = var.notifyRole_id
  customactionrole_id = var.customactionrole_id
  remediatewithsharreventsrule_id = var.remediatewithsharreventsrule_id
}

module "dbcontrols" {
  source = "./DBControls"
  ScoreCardBucketName = var.ScoreCardBucketName
  env_type = var.env_type
  account_id = var.account_id
}