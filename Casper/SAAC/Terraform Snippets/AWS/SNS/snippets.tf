# Ensure SNS is deployed with VPC Endpoints

resource "aws_vpc_endpoint" "sns_vpc_endpoint_id" {
  vpc_id              = data.aws_vpc.aws_vpc_id.id
  service_name        = var.sns_service_name
  vpc_endpoint_type   = var.sns_vpc_endpoint_type
  security_group_ids  = var.sns_vpc_sgs
  private_dns_enabled = true
}

resource "aws_sns_topic" "user_updates" {
  name = var.sns_topic_name

  # Ensure SNS Resources are Encrypted at-rest using organization Managed Keys
  kms_master_key_id = data.aws_kms_key.cg_cmk_key.arn 

  delivery_policy = data.template_file.sns_delivery_policy.rendered
}

# Ensure SNS is deployed with appropriate permissions to enforce least privilege
resource "aws_sns_topic_policy" "sns_least_privilege_policy" {
  arn    = aws_sns_topic.user_updates.arn
  policy = data.template_file.sns_least_privilege_policy.rendered #  Ensure Amazon SNS topics only allow cross account access for organization AWS accounts 
}

# Ensure CloudTrail logging enabled 
# Implementation already deployed per organization standard.

# Ensure SNS topics are not exposed to everyone
resource "aws_iam_policy" "sns_topics_not_exposed_to_everyone_policy" {
  description = "IAM role policy for the SNS users"
  policy      = data.template_file.sns_topics_not_exposed_to_everyone_policy.rendered
}

# Ensure SNS has a Resource Based Policy attached restricting source principles to Organization only
resource "aws_iam_policy" "sns_role_access_policy" {
  description = "IAM role policy for the SNS users"
  policy      = data.template_file.sns_role_access_policy.rendered
}

# Ensure AWS SNS Data is Encrypted in transit with TLS 1.2 or above is not included.
# Implementation is defaultly enabled, see the following documentaiton for more details:
#
# Ensure SNS resources when no longer needed are decommissioned is not included.
# TODO: include CG documentation link for resource lifecycle policies.
