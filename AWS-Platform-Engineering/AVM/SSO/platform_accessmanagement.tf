provider "aws" {
  alias = "pa-us-east-1"
}

data "aws_ssoadmin_instances" "awsatshellplatfromsso" {
  provider = aws.pa-us-east-1
}

data "aws_ssoadmin_permission_set" "irm_permission_set" {
  provider = aws.pa-us-east-1

  instance_arn = tolist(data.aws_ssoadmin_instances.awsatshellplatfromsso.arns)[0]
  name         = var.SSMParameters.irm_permission_set_name
}

data "aws_identitystore_group" "irm_sso_group" {
  provider = aws.pa-us-east-1

  identity_store_id = tolist(data.aws_ssoadmin_instances.awsatshellplatfromsso.identity_store_ids)[0]

  alternate_identifier {
    unique_attribute {
      attribute_path  = "DisplayName"
      attribute_value = var.SSMParameters.platform_irm_group_name
    }
  }
}

resource "aws_ssoadmin_account_assignment" "irm_permission_set_assignment" {
  provider = aws.pa-us-east-1

  instance_arn       = tolist(data.aws_ssoadmin_instances.awsatshellplatfromsso.arns)[0]
  permission_set_arn = data.aws_ssoadmin_permission_set.irm_permission_set.arn

  principal_id   = data.aws_identitystore_group.irm_sso_group.group_id
  principal_type = "GROUP"

  target_id   = var.child_account_number
  target_type = "AWS_ACCOUNT"
}

data "aws_ssoadmin_permission_set" "platform_readonly_permission_set" {
  provider = aws.pa-us-east-1

  instance_arn = tolist(data.aws_ssoadmin_instances.awsatshellplatfromsso.arns)[0]
  name         = var.SSMParameters.platform_readonly_permission_set_name
}

data "aws_identitystore_group" "platform_readonly_group" {
  provider = aws.pa-us-east-1

  identity_store_id = tolist(data.aws_ssoadmin_instances.awsatshellplatfromsso.identity_store_ids)[0]

  alternate_identifier {
    unique_attribute {
      attribute_path  = "DisplayName"
      attribute_value = var.SSMParameters.platform_readonly_group_name
    }
  }
}

resource "aws_ssoadmin_account_assignment" "platform_read_only_permission_set_assignment" {
  provider = aws.pa-us-east-1

  instance_arn       = tolist(data.aws_ssoadmin_instances.awsatshellplatfromsso.arns)[0]
  permission_set_arn = data.aws_ssoadmin_permission_set.platform_readonly_permission_set.arn

  principal_id   = data.aws_identitystore_group.platform_readonly_group.group_id
  principal_type = "GROUP"

  target_id   = var.child_account_number
  target_type = "AWS_ACCOUNT"
}

data "aws_ssoadmin_permission_set" "itom_readonly_permission_set" {
  provider = aws.pa-us-east-1

  instance_arn = tolist(data.aws_ssoadmin_instances.awsatshellplatfromsso.arns)[0]
  name         = var.SSMParameters.itom_readonly_permission_set_name
}

data "aws_identitystore_group" "itom_readonly_group" {
  provider = aws.pa-us-east-1

  identity_store_id = tolist(data.aws_ssoadmin_instances.awsatshellplatfromsso.identity_store_ids)[0]

  alternate_identifier {
    unique_attribute {
      attribute_path  = "DisplayName"
      attribute_value = var.SSMParameters.itom_readonly_group_name
    }
  }
}

resource "aws_ssoadmin_account_assignment" "itom_readonly_permission_set_assignment" {
  provider = aws.pa-us-east-1
  
  instance_arn       = tolist(data.aws_ssoadmin_instances.awsatshellplatfromsso.arns)[0]
  permission_set_arn = data.aws_ssoadmin_permission_set.itom_readonly_permission_set.arn

  principal_id   = data.aws_identitystore_group.itom_readonly_group.group_id
  principal_type = "GROUP"

  target_id   = var.child_account_number
  target_type = "AWS_ACCOUNT"
}