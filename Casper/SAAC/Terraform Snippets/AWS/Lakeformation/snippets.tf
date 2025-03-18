#  Ensure establishment of fine grained access controls
# Data Lake Admin Settings
resource "aws_lakeformation_data_lake_settings" "lakeformation_data_lake_settings" {
  admins = var.lakeformation_list_of_admins # List of admins created by organization DevSecOps

  create_database_default_permissions {
    permissions = var.lakeformation_database_permissions
    principal   = var.lakeformation_database_principal
  }

  # Roles - Developer, Operator, Security
  create_table_default_permissions {
    permissions = var.lakeformation_create_table_permissions
    principal   = var.lakeformation_create_table_principal
  }
}

# LF-Tags with the specified name and values
resource "aws_lakeformation_lf_tag" "lakeformation_lf_tag" {
  key    = var.lakeformation_lf_tag_key
  values = var.lakeformation_lf_tag_values
}

resource "aws_lakeformation_resource_lf_tags" "lakeformation_resource_lf_tags" {
  database {
    name = var.lakeformation_resource_s3_glue_catalog_database_name
  }

  lf_tag {
    key   = var.lakeformation_lf_tag_key
    value = var.lf_tag_values
  }

  depends_on = [
    aws_lakeformation_data_lake_settings.lakeformation_data_lake_settings,
    aws_glue_catalog_database.lakeformation_resource_s3_glue_catalog_database
  ]
}

resource "aws_lakeformation_resource" "lakeformation_resource_s3" {
  arn = var.lakeformation_resource_s3_arn
}

# Ensure AWS Glue Data Catalog is encrypted using organization's managed key
# Reference glue catalog database
resource "aws_glue_catalog_database" "lakeformation_resource_s3_glue_catalog_database" {
  name = var.lakeformation_resource_s3_glue_catalog_database_name
}

resource "aws_glue_data_catalog_encryption_settings" "data_catalog_encryption_settings" {
  data_catalog_encryption_settings {
    connection_password_encryption {
      aws_kms_key_id                       = data.aws_kms_alias.cg_cmk_key_alias.arn
      return_connection_password_encrypted = true
    }

    encryption_at_rest {
      catalog_encryption_mode = "SSE-KMS" # Static value
      sse_aws_kms_key_id      = data.aws_kms_alias.cg_cmk_key_alias.arn
    }
  }
}

# Ensure default permissions for newly created databases and tables are set to be disabled
# Grant Permissions Using Tag-Based Access Control
resource "aws_lakeformation_permissions" "lakeformation_permissions_tags" {
  principal   = var.lakeformation_permissions_principal
  permissions = var.lakeformation_permissions_permissions

  lf_tag_policy {
    resource_type = var.lakeformation_permissions_lf_tag_policy_resource_type

    expression {
      key    = var.lakeformation_permissions_lf_tag_policy_expression_key1
      values = var.lakeformation_permissions_lf_tag_policy_expression_values2
    }

    /** 
     * Add additional expressions as needed
     */
    # expression {
    #  key    = var.lf_tag_policy_expression_key
    #  values = var.lf_tag_policy_expression_values
    # }
  }

  depends_on = [
    aws_lakeformation_data_lake_settings.lakeformation_data_lake_settings,
    aws_lakeformation_lf_tag.lakeformation_lf_tag
  ]
}

# Grant Permissions For A Lake Formation S3 Resource
resource "aws_lakeformation_permissions" "lakeformation_permissions_s3" {
  principal   = var.lakeformation_permissions_s3_principal
  permissions = var.lakeformation_permissions_s3_permissions

  data_location {
    arn = var.lakeformation_permissions_s3_data_location_arn
  }
  depends_on = [
    aws_lakeformation_data_lake_settings.lakeformation_data_lake_settings,
  ]
}

# Ensure 'Super' right is not associated with 'IAMAllowedPrincipals' on Glue Catalog Table and Database
resource "aws_lakeformation_permissions" "aws_glue_catalog_database_security" {
  principal   = var.lakeformation_security_role_arn
  permissions = var.aws_glue_catalog_database_permissions

  database {
    name       = var.aws_glue_catalog_database_name
    catalog_id = var.aws_glue_catalog_database_id
  }
}

#  Ensure lake formation is communicating with services inside VPC via VPC end-point
resource "aws_vpc_endpoint" "lakeformation_vpc_endpoint" {
  vpc_id              = var.lakeformation_vpc_id
  service_name        = var.lakeformation_service_name
  vpc_endpoint_type   = var.lakeformation_endpoint_type      # String
  security_group_ids  = var.lakeformation_security_group_ids # Array
  private_dns_enabled = true
  tags                = var.lakeformation_tags # Map ( Ensure resource tagging is added to AWS lake formation)
}

# 6. Ensure to prevent cross-service confused deputy problem
resource "aws_iam_role" "lakeformation_iam_role_confused_deputy_prevention" {
  name               = var.lakeformation_iam_role_confused_deputy_prevention_name
  description        = var.lakeformation_iam_role_confused_deputy_prevention_description
  assume_role_policy = data.template_file.ConfusedDeputyPreventionExamplePolicy.rendered
  tags               = var.lakeformation_tags #( Ensure resource tagging is added to AWS lake formation)
  depends_on = [
    data.template_file.ConfusedDeputyPreventionExamplePolicy
  ]
}

# Ensure AWS IAM permission on AWS KMS key is only granted to the trusted-list of principals 
# who are identified to grant Lake Formation permissions on Data Catalog resources
resource "aws_iam_role" "lakeformation_security_role_key_access" {
  name               = var.lakeformation_security_role_key_access_name
  description        = var.lakeformation_security_role_key_access_description
  assume_role_policy = data.aws_iam_policy_document.security_role_access_policy.json
  tags               = var.lakeformation_tags #( Ensure resource tagging is added to AWS lake formation)
  depends_on = [
    data.aws_iam_policy_document.security_role_access_policy
  ]
}

#  Ensure cloudtrail logging is enabled for AWS Lakeformation
resource "aws_s3_bucket" "lakeformation_cloudtrail_s3_bucket" {
  bucket        = var.lakeformation_cloudtrail_bucket
  force_destroy = var.lakeformation_cloudtrail_force_destroy
  tags          = var.lakeformation_tags
}

resource "aws_cloudtrail" "lakeformation_cloudtrail" {
  name                          = var.lakeformation_cloudtrail_name                #<------- (Required) Name of the trail.
  s3_bucket_name                = aws_s3_bucket.lakeformation_cloudtrail_s3_bucket.bucket #<------- (Required) Name of the S3 bucket designated for publishing log files.
  s3_key_prefix                 = var.lakeformation_cloudtrail_s3_key_prefix
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  include_global_service_events = true
  tags                          = var.lakeformation_tags
}

resource "aws_iam_role" "lakeformation_security_role_trail_policy" {
  name               = var.lakeformation_security_role_trail_policy_name
  description        = var.lakeformation_security_role_trail_policy_description
  assume_role_policy = data.template_file.TrailPolicy.rendered
  tags               = var.lakeformation_tags
  depends_on = [
    data.template_file.TrailPolicy
  ]
}

#  Ensure lakeformation permission are given only to organization AWS accounts - The policy have place holder to add organization accounts variables.
