locals {
  environment = var.env_type

  shell_sso = (
    local.environment == "dev" ? "sso-dev" :
    local.environment == "uat" ? "sso-uat" :
    local.environment == "prod" ? "sso" :
    null
  )

  domain_name = (
    local.environment == "dev" ? "aws-dev.shell.com" :
    local.environment == "uat" ? "aws-uat.shell.com" :
    local.environment == "prod" ? "aws.shell.com" :
    null
  )

  app_name          = format("AWS-Access-Portal-Landing-Page-%s", local.environment)
  identity_store_id = tolist(data.aws_ssoadmin_instances.current.identity_store_ids)[0]
  redirect_base     = "https://${local.shell_sso}.shell.com/idp/startSSO.ping?PartnerSpId=https%3A%2F%2Fus-east-1.signin.aws.amazon.com%2Fplatform%2Fsaml%2F"
  redirect_url      = "${local.redirect_base}${local.identity_store_id}"
}

data "aws_caller_identity" "current" {}

data "aws_ssoadmin_instances" "current" {}

resource "aws_amplify_app" "landing" {
  name     = local.app_name
  platform = "WEB"

  custom_rule {
    source = "/<*>"
    status = "301"
    target = local.redirect_url
  }

  environment_variables = {
    "_CUSTOM_IMAGE" = "amplify:al2"
  }
}

resource "aws_amplify_branch" "deployment" {
  app_id      = aws_amplify_app.landing.id
  branch_name = local.environment
  stage       = "PRODUCTION"
}

resource "aws_amplify_domain_association" "deployment" {
  app_id                 = aws_amplify_app.landing.id
  domain_name            = local.domain_name
  enable_auto_sub_domain = false
  wait_for_verification  = false

  sub_domain {
    branch_name = aws_amplify_branch.deployment.branch_name
    prefix      = ""
  }
}

output "app_id" {
  value = aws_amplify_app.landing.id
}

output "app_arn" {
  value = aws_amplify_app.landing.arn
}

output "app_dns_name" {
  value = format("%s.%s", local.environment, aws_amplify_app.landing.default_domain)
}

output "certificate_verification_dns_record" {
  value = aws_amplify_domain_association.deployment.certificate_verification_dns_record
}

output "sub_domain" {
  value = aws_amplify_domain_association.deployment.sub_domain
}
