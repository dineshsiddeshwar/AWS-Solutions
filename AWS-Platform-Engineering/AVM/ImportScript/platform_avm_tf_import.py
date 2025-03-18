import os

## Importing SSM associations
def import_aws_avm_ssm_associations (tf_resource_name, id):
    try:  
          cmd = "terraform import aws_ssm_association.{} {}".format(tf_resource_name, id)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing SSM Association {}".format(str(exception)))

## Importing SSM Parameters
def import_aws_avm_ssm_parameters (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_ssm_parameter.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing SSM Parameters {}".format(str(exception)))

## Importing VPC
def import_aws_avm_vpc_creation (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_vpc.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing VPC {}".format(str(exception)))

## Importing VPC Subnet
def import_aws_avm_vpc_subnet_creation (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_subnet.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing VPC subnet {}".format(str(exception)))

## Importing VPC Flow logs
def import_aws_avm_vpc_flowlogs_creation (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_flow_log.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing VPC flow log creation {}".format(str(exception)))

## Importing VPC Extension
def import_aws_avm_vpc_extension (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_vpc_ipv4_cidr_block_association.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing VPC extension {}".format(str(exception)))

## Importing VPC Extension subnet creation
def import_aws_avm_vpc_extend_subnet_creation (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_subnet.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing VPC subnet {}".format(str(exception)))

## Importing VPC Association Authorization
def import_aws_avm_vpc_association_authorization (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_route53_vpc_association_authorization.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing VPC Route53 association authorise {}".format(str(exception)))

## Importing VPC Route53 zone association
def import_aws_avm_vpc_route53_association (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_route53_zone_association.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing VPC route53 zone association {}".format(str(exception)))

## Importing route53 resolver rule
def import_aws_avm_vpc_route53_resolver_rule_association (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_route53_resolver_rule_association.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing VPC route53 resolver rule association {}".format(str(exception)))

## Importing VPC s3 and dynamodb gateway endpoint -- need to invoke two times
def import_aws_avm_vpc_gateway_endpoint (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_vpc_endpoint.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing VPC s3 gateway endpoint {}".format(str(exception)))

## Importing AVM budget            
def import_aws_budget (tf_resource_name, parametername):
    try:  
          # Parametername should of the form :- AccountID:BudgetName
          cmd = "terraform import aws_budgets_budget.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing Budget {}".format(str(exception)))

## Importing platform IAM policies
def import_aws_avm_iam_policies (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_iam_policy.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing AVM IAM Policies {}".format(str(exception)))


## Importing platform IAM roles 
def import_aws_avm_iam_roles (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_iam_role.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing AVM IAM Roles {}".format(str(exception)))

## Importing platform IAM instance profile roles 
def import_aws_avm_iam_instance_profile_roles (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_iam_instance_profile.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing AVM IAM Instance Profile Roles {}".format(str(exception)))

## Importing Security hub Insights
def import_aws_avm_securityhub_insight (tf_resource_name, insightarn):
    try:
          cmd = "terraform import aws_securityhub_insight.{} {}".format(tf_resource_name, insightarn)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing securityhub_insight {}".format(str(exception)))

## Importing Backup Vaults
def import_aws_backup_vaults (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_backup_vault.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing Backup Vault {}".format(str(exception)))

## Importing Backup Vault SNS Topics
def import_aws_backup_vault_sns_topics (tf_resource_name, backup_topic_arn):
    try:  
          cmd = "terraform import aws_sns_topic.{} {}".format(tf_resource_name, backup_topic_arn)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing Backup Vault SNS Topic {}".format(str(exception)))

## Importing Backup Vault SNS Topic Policy
def import_aws_backup_vault_sns_topic_policy (tf_resource_name, backup_topic_arn):
    try:  
          cmd = "terraform import aws_sns_topic_policy.{} {}".format(tf_resource_name, backup_topic_arn)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing Backup Vault SNS Topic Policy {}".format(str(exception)))

## Importing Backup Vault SNS Topic Subscription
def import_aws_backup_vault_sns_topic_subscription (tf_resource_name, backup_topic_subscription_arn):
    try:  
          cmd = "terraform import aws_sns_topic_subscription.{} {}".format(tf_resource_name, backup_topic_subscription_arn)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing Backup Vault SNS Topic Subsription {}".format(str(exception)))

## Importing Backup Vault SNS Topic Notifications
def import_aws_backup_vault_sns_topic_notifications (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_backup_vault_notifications.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing Backup Vault SNS Topic Notifications {}".format(str(exception)))

## Importing SSO(IAM Identity center) permission set assignments via static groups on account.
def import_aws_ssoadmin_account_assignment (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_ssoadmin_account_assignment.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing SSO permission set assignment on static groups {}".format(str(exception)))

## Importing Access Analyzer configurations.
def import_aws_accessanalyzer_analyzer (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_accessanalyzer_analyzer.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing IAM access analyzer {}".format(str(exception)))

## Importing Block EMR public access.
def import_aws_accessanalyzer_analyzer (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_emr_block_public_access_configuration.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing Block EMR public access {}".format(str(exception)))

## Importing Block S3 public access.
def import_aws_s3_account_public_access_block (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_s3_account_public_access_block.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing Block S3 public access {}".format(str(exception)))

## Importing EBS Encryption by default.
def import_aws_ebs_encryption_by_default (tf_resource_name, parametername):
    try:  
          cmd = "terraform import aws_ebs_encryption_by_default.{} {}".format(tf_resource_name, parametername)
          os.system(cmd)
    except Exception as exception:
            print("Exception occurred while importing EBS Encryption by default {}".format(str(exception)))