module "s3_bucket" {
  source = "./modules/S3"
 
  s3_bucket_name = "test"
  s3_bucket_object_lock_config_retention_mode = "Compliance"
  s3_bucket_object_lock_config_retention_period = 10
  s3_vpc_id = module.vpc.vpc_arn
  s3_vpc_endpoint_type = "Interface"
  s3_sse_key = module.kms.kms_outputs
  s3_region = var.aws_region
  s3_vpc_sgs = ["testSg"]
}

module "kms" {
  source = "./modules/KMS"
  kms_deletion_window_in_days = var.kms_deletion_window_in_days
}

module "vpc" {
  source = "./modules/VPC"
}
