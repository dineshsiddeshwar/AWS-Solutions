module "iam" {
  source = "./IAM"
  platform_cloudhealth_external_id = var.platform_cloudhealth_external_id
  platform_cloudhealth_account = var.platform_cloudhealth_account
  s3_bucket = var.s3_bucket
  instance_profile_name = var.instance_profile_name
  account_id = var.account_id
}

module "lambda" {
  source = "./Lambda"
  env_type = var.env_type
  ou_id = var.ou_id
}


module "sqs" {
  source = "./SQS"
  env_type = var.env_type
  account_id = var.account_id
}

module "s3"{
  source = "./S3"
  env_type = var.env_type
  cloudtrail_bucket_rule_id = var.cloudtrail_bucket_rule_id
  config_bucket_rule_id = var.config_bucket_rule_id
  s3accesslogs_bucket_rule_id = var.s3accesslogs_bucket_rule_id
  vpcflowlogs_bucket_rule_id = var.vpcflowlogs_bucket_rule_id
}
