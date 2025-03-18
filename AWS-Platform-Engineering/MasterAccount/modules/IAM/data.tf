data "template_file" "compliance_logging_Policy_template" {
  template = "${file("${path.module}/Policies/IAMP0009-PlatformComplianceLoggingPolicy/policy.json.tpl")}"

  vars = {
    irmaccountid = "${var.irm_account_id}",
    irmenvironment = "${var.irm_environment}"
  }
}

data "template_file" "atl_terraformbackend_policy_template" {
  template = "${file("${path.module}/Policies/IAMP00010-PlatformATLTerraformBackendPolicy/policy.json.tpl")}"

  vars = {
    masteraccountid = "${var.master_account}"
    atlterraformbackendbucket = "${var.atl_terraform_backend_bucket_name}"
    atlterraformbackenddynamodb = "${var.atl_terraform_backend_dynamodb}"
  }
}

data "template_file" "cloud_health_policy_template" {
  template = "${file("${path.module}/Policies/IAMP0002-PlatformCloudHealthPolicy/policy.json.tpl")}"

  vars = {
    cloudhelthbucket = "${var.cloudhelth_bucket_name}"
  }
}

data "template_file" "ec2instance_policy_template" {
  template = "${file("${path.module}/Policies/IAMP00011-PlatformEC2InstancePolicy/policy.json.tpl")}"

  vars = {
    envtype = "${var.env_type}"
  }
}

# Creating platform emailing user policy data document
data "aws_iam_policy_document" "data_emailing_user_policy" {
  statement {
    effect    = "Allow"
    actions   = ["ses:SendEmail"]
    resources = ["*"]
  }
}







