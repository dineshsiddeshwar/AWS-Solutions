resource "aws_iam_role" "platform_log_admin_role" {
  name                = "Platform_LogAdmin"
  description         =  "Role to assume in Logging Account to perform actions"
  assume_role_policy  = jsonencode({
                "Version": "2008-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": [
                                "lambda.amazonaws.com",
                                "s3.amazonaws.com"
                            ]
                        },
                        "Action": "sts:AssumeRole",
                    }
                ]
            })
  managed_policy_arns = [aws_iam_policy.policy_platform_log_admin.arn]
}

resource "aws_iam_role" "platform_service_cloudhealth_role" {
  name                = "platform_service_cloudhealth"
  description         = "Role to assume in CloudHealth Actions"
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
    platform_donotdelete = "yes"
  }
}

resource "aws_iam_role" "platform_splunk_role" {
  name                = "Platform_Splunk"
  description         = "Role to assume by Splunk in Logging Account to perform actions"
  assume_role_policy  = jsonencode({
                "Version": "2008-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ec2.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                     }
                ]
            })
  managed_policy_arns = [aws_iam_policy.policy_platform_splunk.arn]
}
resource "aws_iam_role" "platform_ServiceNow_ITOM_Discovery_Child_Role" {
  name                = "ServiceNow_ITOM_Discovery_Child_Role"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        #"Sid": "Default0",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ec2.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole",
                    },
                    {
                        #"Sid": "Default1",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::247990085610:role/ServiceNowEC2Role"
                        },
                        "Action": "sts:AssumeRole",
                    }                    
                ]
            })
  managed_policy_arns = [ aws_iam_policy.policy_platform_ITOM_Discovery_Child_Policy.arn]
}

resource "aws_iam_instance_profile" "platform_ServiceNow_ITOM_Discovery_Child_InstanceProfile" {
  name = var.instance_profile_name
  role = aws_iam_role.platform_ServiceNow_ITOM_Discovery_Child_Role.name
}

resource "aws_iam_role" "platform_tfc_logging_role" {
  name                = "platform_tfc_logging_role"
  description = "Role to assume by TFC in Logging Account to perform actions"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            Federated = "arn:aws:iam::${var.account_id}:oidc-provider/app.terraform.io"
                        },
                        "Action": "sts:AssumeRoleWithWebIdentity",
                        "Condition":{
                            "StringEquals": {
                                "app.terraform.io:aud": "aws.workload.identity"
                            },
                            "StringLike": {
                               "app.terraform.io:sub": "organization:ecp-shell-prod:project:*:workspace:*:run_phase:*"
                            }
                        }
                    }
                ]
            })
  managed_policy_arns = [aws_iam_policy.policy_platform_log_admin.arn]
  tags = {
    platform_donotdelete = "yes"
  }
}

resource "aws_iam_role" "platform_pytest" {
  name                = "platform_pytest"
  description = "This role will be used by github actions for running pytest in this account."
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            Federated = "arn:aws:iam::${var.account_id}:oidc-provider/token.actions.githubusercontent.com"
                        },
                        "Action": "sts:AssumeRoleWithWebIdentity",
                        "Condition":{
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
  managed_policy_arns = [aws_iam_policy.policy_platform_log_admin.arn]
  tags = {
    platform_donotdelete = "yes"
  }
}