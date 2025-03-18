locals {
  Snow_SGC_accountID = var.master_account_number == "364355817034" ? "836124460601" : (var.master_account_number == "136349175397"? "619315746980" : "595734864285" )
  AccountType        = var.Connectivity == "PVT" || var.Connectivity == "HYB" ? "Private" : "Public"
}

resource "aws_iam_role" "platform_service_cloudhealth_role" {
  name                = "platform_service_cloudhealth"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
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
}

resource "aws_iam_role" "platform_service_inflation_role" {
  name                = "platform_service_inflation"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": [
                                "arn:aws:iam::${var.master_account_number}:role/platform_Admin"
                            ],
                            "Service": [
                                "s3.amazonaws.com",
                                "lambda.amazonaws.com",
                                "access-analyzer.amazonaws.com",
                                "securityhub.amazonaws.com",
                                "cloudformation.amazonaws.com",
                                "config.amazonaws.com",
                                "vpc-flow-logs.amazonaws.com",
                                "cloudtrail.amazonaws.com",
                                "events.amazonaws.com",
                                "logs.amazonaws.com",
                                "ssm.amazonaws.com",
                            ]
                        },
                        "Action": "sts:AssumeRole",
                        "Condition": {}
                    }
                ]
            })
  managed_policy_arns = [aws_iam_policy.policy_platform_inflation_policy.arn, aws_iam_policy.policy_platform_inflation_policy_2.arn,  "arn:aws:iam::aws:policy/AWSLambda_ReadOnlyAccess"]
}

resource "aws_iam_role" "platform_service_instance_role" {
  name                = "platform_service_instance"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Default",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": [
                                "ec2.amazonaws.com",
                                "ssm.amazonaws.com",
                                "sns.amazonaws.com",
                                "lambda.amazonaws.com"
                            ]
                        },
                        "Action": "sts:AssumeRole",
                        "Condition": {}
                    }
                ]
            })
  managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore", "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy", "arn:aws:iam::aws:policy/AmazonSSMDirectoryServiceAccess", aws_iam_policy.policy_platform_iam_pass_role_policy.arn, "arn:aws:iam::aws:policy/AWSLambda_ReadOnlyAccess", aws_iam_policy.policy_platform_sts_full_access_policy.arn, aws_iam_policy.policy_platform_sts_ec2instance_policy.arn, "arn:aws:iam::aws:policy/AWSBackupFullAccess", "arn:aws:iam::aws:policy/AmazonEC2FullAccess"]
}

resource "aws_iam_instance_profile" "platform_service_instance" {
  name = "platform_service_instance"
  role = aws_iam_role.platform_service_instance_role.name
}

resource "aws_iam_role" "platform_service_readonly" {
  name                = "platform_service_readonly"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Default",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::${var.master_account_number}:role/platform_service_read_only"
                        },
                        "Action": "sts:AssumeRole",
                        "Condition": {}
                    }
                ]
            })
  managed_policy_arns = ["arn:aws:iam::aws:policy/ReadOnlyAccess"]
}

resource "aws_iam_role" "platform_backup" {
  name                = "platform_backup"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "backup.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
  managed_policy_arns = ["arn:aws:iam::aws:policy/AWSBackupFullAccess", aws_iam_policy.policy_platform_iam_pass_role_policy.arn, "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup", "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForRestores", "arn:aws:iam::aws:policy/AmazonSNSFullAccess"]
}

resource "aws_iam_role" "platform_ServiceNow_ITOM_Discovery_Child_Role" {
  name                = "ServiceNow_ITOM_Discovery_Child_Role"
  assume_role_policy  = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Default0",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::247990085610:role/ServiceNowEC2Role"
            },
            "Action": "sts:AssumeRole",
            "Condition": {}
        },
        {
            "Sid": "Default1",
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole",
            "Condition": {}
        }
    ]
})
  managed_policy_arns = [ aws_iam_policy.policy_platform_ITOM_Discovery_Child_Policy.arn ]
}

resource "aws_iam_role" "platform_business_cdf-execution-role" {
  count               =  var.IsIOTAccountrequested == "Yes" ? 1 : 0
  name                = "business_cdf-execution-role"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Default",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::923834859708:root"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
  managed_policy_arns = [ aws_iam_policy.IOT_Stackset_Execution_Child_Policy.arn ]
}

resource "aws_iam_role" "platform_SnowOrganizationAccountAccessRole" {
  name                = "platform_SnowOrganizationAccountAccessRole"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Default",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::${local.Snow_SGC_accountID}:root"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
  managed_policy_arns = [ aws_iam_policy.platform_SnowOrganizationAccountAccessPolicy.arn ]
}

resource "aws_iam_role" "Platform_Flexera_AwsConnect_Role" {
  name                = "Platform_Flexera_AwsConnect_Role"
  assume_role_policy  = jsonencode({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Default",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::${var.FlexeraBeaconServer}:role/ListEC2ForFNMSRole"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
  managed_policy_arns = [ "arn:aws:iam::aws:policy/AmazonSSMDirectoryServiceAccess", "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore","arn:aws:iam::aws:policy/AWSBackupFullAccess", "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy","arn:aws:iam::aws:policy/ReadOnlyAccess" , aws_iam_policy.policy_platform_sts_full_access_policy.arn , aws_iam_policy.policy_platform_sts_ec2instance_policy.arn , aws_iam_policy.policy_platform_iam_pass_role_policy.arn , aws_iam_policy.platform_ListEC2ForFNMSPolicy.arn  ]
}