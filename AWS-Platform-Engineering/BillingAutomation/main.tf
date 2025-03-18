module "lambda" {
  source = "./Lambda"
  athena_database = var.athena_database
  athena_table = var.athena_table
  s3_output_location = var.s3_output_location
  s3_bucket = var.s3_bucket
  account_id = var.account_id
  cost_tracker = var.cost_tracker
  main_billing_file = var.main_billing_file
  from_email = var.from_email
  to_email = var.to_email
}

module "s3" {
  source = "./s3"
  account_id = var.account_id
}


