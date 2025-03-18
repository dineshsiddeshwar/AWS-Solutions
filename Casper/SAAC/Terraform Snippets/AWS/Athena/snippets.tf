######################################################################################################################################################################
############################################################       REQUIREMENTS SECTION        #######################################################################
######################################################################################################################################################################

# current account id
locals {
  account_id = data.aws_caller_identity.current.account_id
}

#  Ensure IAM roles to access Athena are following least privilege model
resource "aws_iam_user" "athena_user" {
  name = var.athena_user_name
}
resource "aws_iam_policy" "athena_user_policy" {
  name   = var.athena_user_policy_name
  policy = data.template_file.athena_least_privilege_access.rendered
}
resource "aws_iam_user_policy_attachment" "athena_policy_attach" {
  user       = aws_iam_user.athena_user.name
  policy_arn = aws_iam_policy.athena_user_policy.arn
}

# Athena Database

resource "aws_athena_database" "athena_database_name" {
  name   = var.athena_database_name
  bucket = data.aws_s3_bucket.athena_bucket.bucket
}

# Athena Workgroup

resource "aws_athena_workgroup" "athena_workgroup" {
  name = var.athena_workgroup

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    engine_version {
      selected_engine_version = var.athena_engine_version #  Ensure Athena engine version is organization approved

    }

    result_configuration {
      output_location = var.athena_bucket_out #  Ensure Athena query result is stored in organization internal account S3 bucket

      encryption_configuration {
        encryption_option = "SSE_KMS"
        kms_key_arn       = data.aws_kms_alias.athena_cmk_key_alias.arn
      }
    }
  }
}

# an Athena Named Query resource
resource "aws_athena_named_query" "athena_named_query" {
  name      = var.athena_named_query
  workgroup = aws_athena_workgroup.athena_workgroup.id
  database  = aws_athena_database.athena_database_name.name
  query     = "SELECT * FROM ${aws_athena_database.athena_database_name.name} limit 10;"
}

#  Ensure to enforce encryption at rest for Athena with organization managed CMK
# Implementation is available on S3 terraform scripts
#  Ensure to enforce encryption in transit for Athena
# Implementation is available on S3 terraform scripts
#  Ensure CloudTrail logging is enabled 
# Implementation already deployed per organisation standard.
