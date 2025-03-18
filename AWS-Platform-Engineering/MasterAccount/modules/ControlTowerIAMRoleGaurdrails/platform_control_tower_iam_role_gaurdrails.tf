# Control tower iam role gairdrail Stack
resource "aws_cloudformation_stack" "control_tower_iam_role_gaurdrails_stack" {
  name = var.control_tower_gaurdrails_stack_name
  capabilities = [
    "CAPABILITY_IAM",
    "CAPABILITY_NAMED_IAM"
  ]
  parameters = {
    S3BucketName = var.release_bucket_name
    FolderName = "ReleaseNumber"
  }
  iam_role_arn = var.master_admin_role_arn

  template_url = "https://s3.amazonaws.com/${var.release_bucket_name}/TFC-Master/10/CloudFormationTemplates/control-tower-iam-role-guardrails.yaml"
}