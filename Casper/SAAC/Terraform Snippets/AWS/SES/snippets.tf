######################################################################################################################################################################
############################################################       REQUIREMENTS SECTION        #######################################################################
######################################################################################################################################################################

# current account id
locals {account_id = data.aws_caller_identity.current.account_id}

# Ensure SES is configured with VPC Endpoints to communicate with services inside VPC

resource "aws_vpc_endpoint" "ses_vpc_endpoint_id" {
  vpc_id              = data.aws_vpc.ses_vpc_id.id
  service_name        = var.ses_service_name
  vpc_endpoint_type   = var.ses_vpc_endpoint_type
  security_group_ids  = var.ses_vpc_sg
  private_dns_enabled = true
}

# Ensure SES is deployed with appropriate IAM permissions that enforce least privilege

resource "aws_iam_user" "ses_user" {
  name = var.ses_user_name
}
resource "aws_iam_policy" "ses_user_policy" {
  name   = var.ses_user_policy
  policy = data.template_file.ses_least_privilege_access.rendered
}
resource "aws_iam_user_policy_attachment" "ses_policy_attach" {
  user       = aws_iam_user.ses_user.name
  policy_arn = aws_iam_policy.ses_user_policy.arn
  depends_on = [
    data.template_file.ses_approved_listof_domain_policy   #  Ensure SES is deployed using an approved list of Recipient Domains only
  ]
}

# Ensure SES is deployed using the Approved Email Sub-Domain only
# The SESApprovedEmailSubdomainPolicy.json is an SCP and applied at organization level and thus applies to all accross organization AWS Accounts by default.

# Ensure SES is deployed using a Dedicated AWS Sender Source Address
# AWS provides a possibility to configure IP pools and assign it to AWS SES Configuration Set but this seems not to be described in Terraform.

# Ensure SES is encrypted in transit using TLS 1.2 or higher
resource "aws_ses_configuration_set" "ses_configuration_set" {
  name = var.ses_configuration_set

  delivery_options {
    tls_policy = "Require"
  }
}

# Ensure SES verified identity is created using organization owned domain

resource "aws_ses_domain_identity" "ses_domain_name" {
  domain = var.ses_domain_name
}

# Ensure SES verified identity is created using DKIM signatures enabled to protect messages from being forged in transit

resource "aws_ses_domain_dkim" "ses_domain_dkim" {
  domain = aws_ses_domain_identity.ses_domain_name.domain
}

# Ensure SES Utilizes Resource Based Policy to Prevent Public Access
resource "aws_iam_role" "ses_iam_role" {
  name               = var.ses_role_name
  assume_role_policy = data.template_file.ses_assumerole_policy.rendered
}

resource "aws_iam_policy" "ses_iam_policy" {
  name   = var.ses_iam_policy_name
  policy = data.template_file.ses_resource_based_iam_role_policy.rendered
}

resource "aws_iam_role_policy_attachment" "ses_iam_role_policy_attach" {
  role       = aws_iam_role.ses_iam_role.name
  policy_arn = aws_iam_policy.ses_iam_policy.arn
}
