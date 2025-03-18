######################################################################################################################################################################
############################################################       REQUIREMENTS SECTION        #######################################################################
######################################################################################################################################################################

# current account id
locals {
  account_id = data.aws_caller_identity.current.account_id
}

#  Ensure Glacier is deployed with appropriate IAM permissions that enforce least privilege

resource "aws_iam_role" "glacier_iam_role" {
  name               = var.glacier_role_name
  assume_role_policy = data.template_file.GlacierAssumeRolePolicy

}

resource "aws_iam_policy" "glacier_iam_policy" {
  name   = var.glacier_iam_policy_name
  policy = data.template_file.GlacierManagedPermissionPolicy
  depends_on = [
    data.template_file.GlacierCrossAccountPermission,
    data.template_file.GlacierCrossAccountMFADeleteOperations
  ]
}

resource "aws_iam_role_policy_attachment" "glacier_iam_role_policy_attach" {
  role       = aws_iam_role.glacier_iam_role.name
  policy_arn = aws_iam_policy.glacier_iam_policy.arn
}

#  Ensure data within SS Glacier is encrypted at rest using organization managed key (CMK) 
# Already implemented in S3 Module

#  Ensure data are encrypted in transit using TLS 1.2
# Already implemented in S3 Module

#  Ensure to enable Cloudtrail for Amazon S3 Glacier
# Cloudtrail is enabled at organization level

#  Ensure to monitor Amazon S3 Glacier using Cloudwatch
resource "aws_s3_bucket_metric" "glacier_bucket" {
  bucket = var.glcaier_bucket_id
  name   = var.glacier_bucket_name
  filter {
    prefix = var.filter_name_prefix
    tags = {
      priority = var.filter_name_priority
      class    = var.filter_name_class
    }
  }
  
}
