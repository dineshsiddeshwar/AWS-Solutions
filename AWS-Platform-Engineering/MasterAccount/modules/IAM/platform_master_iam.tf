# Creating platform emailing user
resource "aws_iam_user" "emailing_user" {
  name = "platform_emailing_user"

}

resource "aws_iam_policy" "emailing_user_policy" {
  name   = "platform_emailing_user_policy"
  description   = "platform emailing user policy"
  path = "/"
  policy = data.aws_iam_policy_document.data_emailing_user_policy.json
}

resource "aws_iam_user_policy_attachment" "emailing_user_policy_attachment" {
  user       = aws_iam_user.emailing_user.name
  policy_arn = aws_iam_policy.emailing_user_policy.arn
}

resource "aws_iam_access_key" "emailing_user_access_key" {
  user = aws_iam_user.emailing_user.name
  status = "Active"
}

resource "aws_iam_policy" "policy_platform_cloud_health_policy" {
  name        = "platform_cloud_health_policy"
  path        = "/"
  description = "Policy for creating a test database"

  policy = data.template_file.cloud_health_policy_template.rendered
}

resource "aws_iam_policy" "policy_platform_inflation_policy" {
  name        = "platform_inflation_policy"
  path        = "/"
  description = "Policy for creating a test database"

  policy = file("${path.module}/Policies/IAMP0005-PlatformInflationPolicy/policy.json")
}

resource "aws_iam_policy" "policy_platform_inflation_policy_2" {
  name        = "platform_inflation_policy_2"
  path        = "/"
  description = "Policy for creating a test database"

  policy = file("${path.module}/Policies/IAMP0006-PlatformInflationPolicy2/policy.json")
}

resource "aws_iam_policy" "policy_platform_iam_pass_role_policy" {
  name        = "platform_iam_pass_role_policy"
  path        = "/"
  description = "Policy for creating a test database"

  policy = file("${path.module}/Policies/IAMP0003-PlatformIamPassRolePolicy/policy.json")
}

resource "aws_iam_policy" "policy_platform_sts_full_access_policy" {
  name        = "platform_sts_full_access"
  path        = "/"
  description = "Policy for creating a test database"

  policy = file("${path.module}/Policies/IAMP0004-PlatformStsFullAccessPolicy/policy.json")
}

resource "aws_iam_policy" "policy_platform_master_admin_policy" {
  name        = "platform_master_admin"
  path        = "/"
  description = "Policy for creating a test database"

  policy = file("${path.module}/Policies/IAMP0001-PlatformMasterAdminPolicy/policy.json")
}

resource "aws_iam_policy" "policy_platform_AWS_CloudFormation_Administration_Policy" {
  name        = "AWSCloudFormationAdministrationPolicy"
  path        = "/"
  description = "AWS CloudFormation Administration Policy"

  policy = file("${path.module}/Policies/IAMP0007-PlatformAWSCloudFormationAdministrationPolicy/policy.json")
}

resource "aws_iam_policy" "policy_platform_AWS_CloudFormation_Execution_Policy" {
  name        = "AWSCloudFormationExecutionPolicy"
  path        = "/"
  description = "AWS CloudFormation Execution Policy"

  policy = file("${path.module}/Policies/IAMP0008-PlatformAWSCloudFormationExecutionPolicy/policy.json")
}

resource "aws_iam_policy" "policy_platform_compliance_logging_Policy" {
  name        = "platform_compliance_logging_policy"
  path        = "/"
  description = "Policy for Events Rule to send events to IRM"

  policy = data.template_file.compliance_logging_Policy_template.rendered
}

resource "aws_iam_policy" "policy_platform_atl_terraformbackend_Policy" {
  name        = "platform_atl_terraformbackend_policy"
  path        = "/"
  description = "Policy for ATL Terraform backend configuration"

  policy = data.template_file.atl_terraformbackend_policy_template.rendered
}

resource "aws_iam_policy" "policy_platform_ec2instance_Policy" {
  name        = "platform_ec2instance_policy"
  path        = "/"
  description = "Custom Policy For Agent Instance"

  policy = data.template_file.ec2instance_policy_template.rendered
}

resource "aws_iam_policy" "policy_platform_ServiceNow_ITOM_Discovery_Policy" {
  name        = "ServiceNow_ITOM_Discovery_Policy"
  path        = "/"

  policy = file("${path.module}/Policies/IAMP00012-PlatformServiceNowITOMDiscoveryChildPolicy/policy.json")
}

resource "aws_iam_policy" "policy_platform_IOT_Stackset_Execution_Child_Policy" {
  name        = "IOT_Stackset_Execution_Child_Policy"
  path        = "/"
  description = "IOT@Shell CDF stackset Exrcution Child Policy"

  policy = file("${path.module}/Policies/IAMP00013-PlatformIOTCDFExecutionChildPolicy/policy.json")
}

resource "aws_iam_role" "platform_service_read_only_role" {
  name                = "platform_service_read_only"
  path                = "/"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::${var.master_account}:root"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
  managed_policy_arns = ["arn:aws:iam::aws:policy/ReadOnlyAccess",  "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_iam_role" "platform_admin_role" {
  name                = "platform_Admin"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": [
                                "apigateway.amazonaws.com",
                                "sts.amazonaws.com",
                                "amplify.amazonaws.com",
                                "lambda.amazonaws.com",
                                "servicecatalog.amazonaws.com",
                                "events.amazonaws.com",
                                "states.amazonaws.com",
                                "cloudformation.amazonaws.com"
                            ]
                        },
                        "Action": "sts:AssumeRole"
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Federated": "arn:aws:iam::${var.master_account}:oidc-provider/app.terraform.io"
                        },
                        "Action": "sts:AssumeRoleWithWebIdentity",
                        "Condition": {
                            "StringEquals": {
                                "app.terraform.io:aud": "aws.workload.identity"
                            },
                            "StringLike": {
                                "app.terraform.io:sub": "organization:ecp-shell-prod:project:titan:workspace:*:run_phase:*"
                            }, 
                        }
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Federated": "arn:aws:iam::${var.master_account}:oidc-provider/token.actions.githubusercontent.com"
                        },
                        "Action": "sts:AssumeRoleWithWebIdentity",
                        "Condition": {
                            "StringEquals": {
                                "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                            },
                            "StringLike": {
                                "token.actions.githubusercontent.com:sub": "repo:sede-x/AWS-at-Shell-Platform-Engineering:*"
                            }
                        }
                    }
                ]
            })
  managed_policy_arns = ["arn:aws:iam::aws:policy/AdministratorAccess", aws_iam_policy.policy_platform_master_admin_policy.arn, "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_role" "platform_compliance_logging_role" {
  name                = "platform_compliance_logging_role"
  description           = "Role for EventRule to send events to IRM Event Bus"
  assume_role_policy  = jsonencode({
                "Version": "2008-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "events.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
  managed_policy_arns = [aws_iam_policy.policy_platform_compliance_logging_Policy.arn, "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_iam_role" "platform_snow_itom_role" {
  name                = "ServiceNow_ITOM_Discovery_Role"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::${var.snow_itom_prod_account}:root"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
  managed_policy_arns = [aws_iam_policy.policy_platform_ServiceNow_ITOM_Discovery_Policy.arn,"arn:aws:iam::aws:policy/AWSOrganizationsReadOnlyAccess",  "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_role" "platform_wiz_scanner_role" {
  name                =  "${var.wiz_env_type}-WizScannerRole_us-east-1"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::${var.wiz_orchestrator_account_id}:root"
                        },
                        "Action": "sts:AssumeRole",
                        "Condition": {
                            "StringEquals": {
                                "sts:ExternalId": var.wiz_external_id
                            }
                        }
                    }
                ]
            })
  managed_policy_arns = ["arn:aws:iam::aws:policy/job-function/ViewOnlyAccess", "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_role_policy" "platform_wiz_scanner_inline_policy_1" {
  name = "WizDataScanningPolicy"
  role = aws_iam_role.platform_wiz_scanner_role.id
  policy = file("${path.module}/Policies/IAMP00014-PlatformWizScannerPolicy/WizDataScanningPolicy.json")
}

resource "aws_iam_role_policy" "platform_wiz_scanner_inline_policy_2" {
  name = "WizScannerPolicy"
  role = aws_iam_role.platform_wiz_scanner_role.id
  policy = file("${path.module}/Policies/IAMP00014-PlatformWizScannerPolicy/WizScannerPolicy.json")
}

resource "aws_iam_role_policy" "platform_wiz_scanner_inline_policy_3" {
  name = "WizServerlessScanningPolicy"
  role = aws_iam_role.platform_wiz_scanner_role.id
  policy = file("${path.module}/Policies/IAMP00014-PlatformWizScannerPolicy/WizServerlessScanningPolicy.json")
}

resource "aws_iam_role" "platform_wiz_access_role" {
  name                = "${var.wiz_env_type}-WizAccess-Role_us-east-1"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::${var.wiz_access_account_id}:root"
                        },
                        "Action": "sts:AssumeRole",
                        "Condition": {
                            "StringEquals": {
                                "sts:ExternalId": var.wiz_external_id
                            }
                        }
                    }
                ]
            })
  managed_policy_arns = ["arn:aws:iam::aws:policy/SecurityAudit", "arn:aws:iam::aws:policy/job-function/ViewOnlyAccess", "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_role_policy" "platform_wiz_access_inline_policy" {
  name = "WizFullPolicy"
  role = aws_iam_role.platform_wiz_access_role.id
  policy = file("${path.module}/Policies/IAMP00015-PlatformWizAccessPolicy/policy.json")
}

resource "aws_iam_role" "platform_AWS_CloudFormation_StackSet_Administration_Role" {
  name                = "AWSCloudFormationStackSetAdministrationRole"
  path                = "/"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "cloudformation.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }                    
                ]
            })
  managed_policy_arns = [ aws_iam_policy.policy_platform_AWS_CloudFormation_Administration_Policy.arn,  "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

resource "aws_iam_role" "platform_AWS_CloudFormation_StackSet_Execution_Role" {
  name                = "AWSCloudFormationStackSetExecutionRole"
  path                = "/"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "cloudformation.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    },
                    {
                        "Sid": "Default",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::${var.master_account}:role/AWSCloudFormationStackSetAdministrationRole"
                        },
                        "Action": "sts:AssumeRole",
                        "Condition": {}
                    }                  
                ]
            })
  managed_policy_arns = [ aws_iam_policy.policy_platform_AWS_CloudFormation_Execution_Policy.arn,  "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]

  tags = {
    "platform_donotdelete" = "yes"
  }
}

#Dynatrace Monitoring Role
resource "aws_iam_role" "dynatrace_monitoring_role" {
  name                = var.DynatraceRoleNameMaster
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::${var.DynatraceAccountID}:role/Dynatrace_ActiveGate_role"
                        },
                        "Action": "sts:AssumeRole",
                        "Condition": {
                            "StringEquals": {
                                "sts:ExternalId": "9f0ace73-5c27-4247-95c4-26cd51d42e00"
                            },
                        }
                    }                  
                ]
            })
  #managed_policy_arns = [ aws_iam_policy.dynatrace_monitoring_role_Policy.arn ]
}

resource "aws_iam_role_policy" "dynatrace_monitoring_role_Policy" {
  name        = "Dynatrace_monitoring_policy"
  role = aws_iam_role.dynatrace_monitoring_role.id
  policy = file("${path.module}/Policies/IAMP00016-Dynatrace_monitoring_policy/policy.json")
}

#SnowOrganizationAccountAccess Role
resource "aws_iam_role" "snow_organization_account_access_role" {
  name                = "platform_SnowOrganizationAccountAccessRole"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::${var.SNOWSGCAccountID}:root"
                        },
                        "Action": "sts:AssumeRole"
                    }                  
                ]
            })
  managed_policy_arns = [ aws_iam_policy.snow_organization_account_access_policy.arn,  "arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_iam_policy" "snow_organization_account_access_policy" {
  name        = "platform_SnowOrganizationAccountAccessPolicy"
  path        = "/"
  description = "SnowOrganizationAccountAccessPolicy"

  policy = file("${path.module}/Policies/IAMP00017-SnowOrganizationAccountAccessPolicy/policy.json")
}

resource "aws_iam_policy" "policy_billing_flexera_policy" {
  name        = "billing_flexera_policy"
  path        = "/"
  description = "Policy for creating a test database"

  policy = file("${path.module}/Policies/IAMP00018-PlatformBillingFlexeraPolicy/iam${var.env_type}policy.json")
}

resource "aws_iam_role" "billing_flexera_role" {
  name                = "Billing_Flexera_Role"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::451234325714:root"
                        },
                        "Action": "sts:AssumeRole"
                        "Condition": {
                          "StringEquals": {
                            "sts:ExternalId": "32226"
                }
            }
                    }
                ]
            })
  managed_policy_arns = [aws_iam_policy.policy_billing_flexera_policy.arn,"arn:aws:iam::${var.master_account}:policy/platform_deny_assume_control_tower_role_policy"]
}

resource "aws_s3_bucket_policy" "policy_billing_flexera" {
  bucket = "${var.billing_bucket_name}"
  policy = file("${path.module}/Policies/IAMP00018-PlatformBillingFlexeraPolicy/${var.env_type}policy.json")
}