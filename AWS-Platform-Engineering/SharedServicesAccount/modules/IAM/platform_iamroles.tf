resource "aws_iam_role" "platform_service_cloudhealth_role" {
  name                = "platform_service_cloudhealth"
  description           = "Role to assume in CloudHealth Actions"
  assume_role_policy  = jsonencode({
                "Version": "2008-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::${var.platform_cloudhealth_account}:root"
                        },
                        "Action": "sts:AssumeRole",
                        "Condition": {
                            "StringEquals": {
                                "sts:ExternalId": var.platform_cloudhealth_external_id
                            }
                        }
                    }
                ]
            })
  managed_policy_arns = [aws_iam_policy.policy_platform_cloud_health_policy.arn]
  tags = {
    "platform_donotdelete" = "yes"
  }
}


resource "aws_iam_role" "platform_ServiceNow_ITOM_Discovery_Child_Role" {
  name                = "ServiceNow_ITOM_Discovery_Child_Role"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ec2.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    },  
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::247990085610:role/ServiceNowEC2Role"
                        },
                        "Action": "sts:AssumeRole"
                    }                                      
                ]
            })
  managed_policy_arns = [ aws_iam_policy.policy_platform_ITOM_Discovery_Child_Policy.arn ]
}

resource "aws_iam_instance_profile" "platform_ServiceNow_ITOM_Discovery_Child_InstanceProfile" {
  name = "platform-ServiceEndpoints-ServiceNowITOMDiscoveryChildInstanceProfile-${var.env_instanceprofile_suffix}"
  role = aws_iam_role.platform_ServiceNow_ITOM_Discovery_Child_Role.name
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
                            "Federated": "arn:aws:iam::${var.platform_shared_account}:oidc-provider/app.terraform.io"
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
                            "Federated": "arn:aws:iam::${var.platform_shared_account}:oidc-provider/token.actions.githubusercontent.com"
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
  managed_policy_arns = ["arn:aws:iam::aws:policy/AdministratorAccess", aws_iam_policy.policy_platform_master_admin_policy.arn]
}