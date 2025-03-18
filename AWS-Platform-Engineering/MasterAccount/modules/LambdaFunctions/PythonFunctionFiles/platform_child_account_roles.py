import json
import boto3
import logging
import random
import datetime
import time

CLOUDHEALTH_ROLE_NAME = "platform_service_cloudhealth"
ACCOUNT_INFLATION_ROLE_NAME = "platform_service_inflation"
INSTANCE_ROLE_NAME = "platform_service_instance"
READONLY_ROLE_NAME = "platform_service_readonly"
CUSTSERVICE_ROLE_NAME = "business_service_admin"            # ON UPDATE, DELETES; ON CREATE, IGNORES
CUSTSERVICE_READONLY_ROLE_NAME="business_service_readonly"  # ON UPDATE, DELETES; ON CREATE, IGNORES
PLATFORM_BACK_UP="platform_backup"
IAM_ATTACH_POLICY_MAX_RETRIES = 4
PLATFORM_ITOM_ROLE="ServiceNow_ITOM_Discovery_Child_Role"
IOT_SHELL_CDF_EXECUTION_ROLE = "business_cdf-execution-role"
PLATFORM_SNOW_SGC_ROLE = "platform_SnowOrganizationAccountAccessRole"
PLATFORM_ListEC2ForFNM_ROLE = "Platform_Flexera_AwsConnect_Role"
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

"""
This Lambda function is used to create roles in the business account from the AVM
"""

class AccountAuthorization(object):
    def __init__(self, event, context):
        try:
            self.cloudhealth_externalid = ""
            ssm_client = boto3.client('ssm')
            self.cloudhealth_externalid = event['SSMParametres']['platform_cloudhealth_external_id']
            self.cloudhealth_account = event['SSMParametres']['platform_cloudhealth_account']
            self.master_account_number = event['SSMParametres']['admin_account']
            self.iam_account_number = event['SSMParametres']['iam_mgmnt_account']
            self.admin_account = event['SSMParametres']['admin_account']
            self.IsIOTAccount = event['ResourceProperties']['IsIOTAccount']
            self.AccountType = event['ResourceProperties']['AccountType']
            self.account_number = event['accountNumber']
            self.RequestType = event['RequestType']
            self.IsDatabricksAccount = event['ResourceProperties']['IsDatabricksAccount']
            if self.IsDatabricksAccount == 'Yes':
                self.DatabricksEnvironment = event['ResourceProperties']['DatabricksEnvironment'].lower()
                self.Databricks_projectID = event['ResourceProperties']['DatabricksProjectID'].lower()
                self.Databricks_role_name_us_east_1 = self.Databricks_projectID + "-" + self.account_number + "-us-east-1-" + self.DatabricksEnvironment + "-platform-role"
                self.Databricks_role_name_eu_west_1 = self.Databricks_projectID + "-" + self.account_number + "-eu-west-1-" + self.DatabricksEnvironment + "-platform-role"
                self.databricks_role_name = [self.Databricks_role_name_eu_west_1, self.Databricks_role_name_us_east_1]

                self.Databricks_policy_name = self.Databricks_projectID + "-" + self.account_number + "-" + self.DatabricksEnvironment + "-platform-policy"
                self.DatabricksVolumeRequired = event['ResourceProperties']['DatabricksVolumeRequired']
                if self.DatabricksVolumeRequired == 'Yes':
                    self.DatabricksS3Region = event['ResourceProperties']['DatabricksS3Region']
                    self.Databricks_s3_name = self.Databricks_projectID + "-" + self.account_number + "-" + self.DatabricksS3Region + "-" + self.DatabricksEnvironment + "-volume-" + str(random.randint(1, 100000))
                    self.Databricks_volume_policy_name = self.Databricks_projectID + "-" + self.account_number + "-" + self.DatabricksS3Region + "-" + self.DatabricksEnvironment + "-volume-policy"

            self.event = event
            self.context = context
            self.iam_arn_string_1 = "arn:aws:iam::"
            self.str_sts_assume_role = "sts:AssumeRole"
            self.str_lambda_arn = "lambda.amazonaws.com"
            self.session_client = boto3.session.Session()
            self.sts_master_client = self.session_client.client('sts')
            self.child_account_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))
            self.master_account_session_name = "MasterAccountSession-" + str(random.randint(1, 100000))
            self.child_account_role_arn = self.iam_arn_string_1 + str(self.account_number) + ":role/AWSControlTowerExecution"
            self.master_account_role_arn = self.iam_arn_string_1 + str(self.master_account_number) + ":role/platform_Admin"

            """Assume Role into the child account"""
            master_account_role_creds = self.sts_master_client.assume_role(RoleArn=self.master_account_role_arn,
                                                                           RoleSessionName=self.master_account_session_name)
            master_credentials = master_account_role_creds.get('Credentials')
            master_access_key_id = master_credentials.get('AccessKeyId')
            master_secret_access_key = master_credentials.get('SecretAccessKey')
            master_session_token = master_credentials.get('SessionToken')
            self.master_assume_role_session = boto3.Session(master_access_key_id, master_secret_access_key,
                                                            master_session_token)
            self.iam_masteraccount_client = self.master_assume_role_session.client('iam')

            child_account_role_creds = self.sts_master_client.assume_role(RoleArn=self.child_account_role_arn,
                                                                          RoleSessionName=self.child_account_session_name)
            child_credentials = child_account_role_creds.get('Credentials')
            child_access_key_id = child_credentials.get('AccessKeyId')
            child_secret_access_key = child_credentials.get('SecretAccessKey')
            child_session_token = child_credentials.get('SessionToken')
            self.child_assume_role_session = boto3.Session(child_access_key_id, child_secret_access_key,
                                                           child_session_token)
            self.iam_childaccount_client = self.child_assume_role_session.client('iam')
        except Exception as e:
            print(str(e))
            raise Exception(str(e))


    def role_policy_document (self):
        policy_document_created_status = False
        try:
            self.cloud_health_policy_arn = self.iam_arn_string_1 + str(
                self.master_account_number) + ":policy/platform_cloud_health_policy"

            cloudhealth_account = self.cloudhealth_account

            self.child_inflation_policy_arn = ""
            self.child_inflation_policy_2_arn = ""
            self.inflation_policy_arn = self.iam_arn_string_1 + str(
                self.master_account_number) + ":policy/platform_inflation_policy"
            self.inflation_policy_2_arn = self.iam_arn_string_1 + str(
                self.master_account_number) + ":policy/platform_inflation_policy_2"
            self.ec2instance_policy_arn = self.iam_arn_string_1 + str(
                self.master_account_number) + ":policy/platform_ec2instance_policy"
            self.readonly_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
            self.ssm_policy_arn = "arn:aws:iam::aws:policy/AmazonSSMFullAccess"
            self.cloudwatch_plicy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
            self.child_iam_passrole_policy_arn = ""
            self.ccs_iam_passrole_policy_arn = self.iam_arn_string_1 + str(
                self.master_account_number) + ":policy/platform_iam_pass_role_policy"
            self.cloudwatch_fullaccess = "arn:aws:iam::aws:policy/CloudWatchFullAccessV2"
            self.sts_fullaccess = self.iam_arn_string_1 + str(self.master_account_number) + ":policy/platform_sts_full_access"
            self.readonly_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"

            self.admin_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
            self.lambda_readonly_policy_arn = "arn:aws:iam::aws:policy/AWSLambda_ReadOnlyAccess"
            self.lambda_deprecated_readonly_policy_arn = "arn:aws:iam::aws:policy/AWSLambdaReadOnlyAccess"
            self.ec2_readonly_policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
            self.ec2_fullaccess_policy_arn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
            self.back_up_arn = "arn:aws:iam::aws:policy/AWSBackupFullAccess"
            self.sns_full_access = "arn:aws:iam::aws:policy/AmazonSNSFullAccess"
            self.back_up_servicerole_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"
            self.restore_servicerole_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForRestores"
            self.itom_policy_arn = self.iam_arn_string_1 + str(
                self.master_account_number) + ":policy/ServiceNow_ITOM_Discovery_Child_Policy"
            self.child_itom_policy_arn = ""
            self.iot_policy_arn = self.iam_arn_string_1 + str(
                self.master_account_number) + ":policy/IOT_Stackset_Execution_Child_Policy"
            self.child_iot_cdf_policy_arn = ""
            self.snow_sgc_policy_arn = self.iam_arn_string_1 + str(
                self.master_account_number) + ":policy/platform_SnowOrganizationAccountAccessPolicy"
            self.child_snow_sgc_policy_arn = ""
            # SSM Managed Instance Core Policy required for SSM Document to Auto Assign ROle
            self.ssm_managed_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
            self.ssm_managed_arn_directory_Service = "arn:aws:iam::aws:policy/AmazonSSMDirectoryServiceAccess"
            #Policy platform_ListEC2ForFNMSPolicy created in master account
            self.ListEC2ForFNMSpvt_policy_arn = self.iam_arn_string_1 + str(
                self.master_account_number) + ":policy/platform_ListEC2ForFNMSPolicyPrivate"
            self.child_ListEC2ForFNMSpvt_policy_arn = ""
            self.ListEC2ForFNMSpub_policy_arn = self.iam_arn_string_1 + str(
                self.master_account_number) + ":policy/platform_ListEC2ForFNMSPolicyPublic"
            self.child_ListEC2ForFNMSpub_policy_arn = ""

            """Create Role Trust Policy JSON for cloudhealth"""
            self.assume_role_policy_document_for_cloudhealth = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": self.iam_arn_string_1 + cloudhealth_account + ":root"
                        },
                        "Action": self.str_sts_assume_role,
                        "Condition": {
                            "StringEquals": {
                                "sts:ExternalId": self.cloudhealth_externalid
                            }
                        }
                    }
                ]
            }
            """Create Role Trust Policy JSON for acclunt inflation"""
            self.assume_role_policy_document_for_account_inflation = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": [
                                self.iam_arn_string_1+ self.master_account_number + ":role/platform_Admin"
                            ],
                            "Service": [
                                "s3.amazonaws.com",
                                self.str_lambda_arn,
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
                        "Action": self.str_sts_assume_role,
                        "Condition": {}
                    }
                ]
            }
            """Create Role Trust Policy JSON for ec2 instance role"""
            self.assume_role_policy_document_for_instance_role = {
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
                                self.str_lambda_arn
                            ]
                        },
                        "Action": self.str_sts_assume_role,
                        "Condition": {}
                    }
                ]
            }
            """Create Role Trust Policy JSON for for read only role which trust's the read only role in master account"""
            self.assume_role_policy_document_for_readonly = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Default",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": self.iam_arn_string_1 + self.master_account_number + ":role/platform_service_read_only"
                        },
                        "Action": self.str_sts_assume_role,
                        "Condition": {}
                    }
                ]
            }

            """Create Role Trust Policy JSON for business admin role"""
            self.assume_role_policy_document_for_account_custservice = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Default",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": [
                                "athena.amazonaws.com",
                                "glue.amazonaws.com",
                                "elasticmapreduce.amazonaws.com",
                                "cloudformation.amazonaws.com",
                                "sagemaker.amazonaws.com",
                                "eks.amazonaws.com",
                                self.str_lambda_arn,
                                "appsync.amazonaws.com"
                            ]
                        },
                        "Action": self.str_sts_assume_role,
                        "Condition": {}
                    }
                ]
            }
            """Create Role Trust Policy JSON for back up role"""
            self.assume_role_policy_back_up = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "backup.amazonaws.com"
                        },
                        "Action": self.str_sts_assume_role
                    }
                ]
            }
            """Create Role Trust Policy JSON for ITOM read only role which trust's the read only role in servicenow account"""
            self.assume_role_policy_itom_readonly = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Default0",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::247990085610:role/ServiceNowEC2Role"
                        },
                        "Action": self.str_sts_assume_role,
                        "Condition": {}
                    },
                    {
                        "Sid": "Default1",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ec2.amazonaws.com"
                        },
                        "Action": self.str_sts_assume_role,
                        "Condition": {}
                    }
                ]
            }
            """Create Role Trust Policy JSON for IOT CDF excecution role in IOT accounts"""
            self.assume_role_policy_iot_cdf = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Default",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::923834859708:root"
                        },
                        "Action": self.str_sts_assume_role
                    }
                ]
            }
            """Create Role Trust Policy JSON for Flexera Beacon accounts excecution role in public accounts"""
            self.assume_role_policy_FlexeraBeacon_pub = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Default",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::443534543078:role/ListEC2ForFNMSRole"
                        },
                        "Action": self.str_sts_assume_role
                    }
                ]
            }
            """Create Role Trust Policy JSON for Flexera Beacon accounts excecution role in private accounts"""
            self.assume_role_policy_FlexeraBeacon_pvt = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Default",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::093543580259:role/ListEC2ForFNMSRole"
                        },
                        "Action": self.str_sts_assume_role
                    }
                ]
            }
            if self.admin_account == "364355817034":
                Snow_SGC_accountID = "836124460601"
            elif self.admin_account == "136349175397 ":
                Snow_SGC_accountID = "619315746980 "
            else:
                Snow_SGC_accountID = "595734864285"
            self.assume_role_policy_SNOW_SGC = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Default1",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": self.iam_arn_string_1 + Snow_SGC_accountID +":root"
                        },
                        "Action": self.str_sts_assume_role,
                        "Condition": {}
                    }
                ]
            }
            policy_document_created_status = True
        except Exception as e:
            policy_document_created_status = False
            print ("role_policy_document")
            print (str(e))
        return policy_document_created_status

    def attach_role_policy_routine(self,CHILD_ROLE_NAME,child_role_policy_arn):
        """
        function: attach role policy with exponential back-off in case of throttling issue.
        param: role name
        param: policy arn
        output: status of the operation
        """
        LOGGER.info("attach_role_policy_routine function has been started")
        retries = 0
        retry_policy_attach_status = 'False'
        try:
            while retries < IAM_ATTACH_POLICY_MAX_RETRIES and retry_policy_attach_status == 'False':
                response = self.iam_childaccount_client.attach_role_policy(RoleName=CHILD_ROLE_NAME,
                                                            PolicyArn=child_role_policy_arn)
                temp_res_code = response['ResponseMetadata']['HTTPStatusCode']
                if temp_res_code == 200:
                    retry_policy_attach_status = 'True'
                    LOGGER.info(" Policy %s has been attached successfully", str(CHILD_ROLE_NAME))
                else:
                    time_to_sleep = 2 ** retries
                    retries += 1
                    time.sleep(time_to_sleep)
        except Exception as exception_object:
            print(str(exception_object))
            print("Error occurred while retry Attach Role Policy %s", str(exception_object))
            retry_policy_attach_status = False
        return retry_policy_attach_status


    """Check and list if the role is created before"""
    def list_iam_roles(self):
        roles = []
        try:
            response = self.iam_childaccount_client.list_roles()
            response_roles = response['Roles']
            is_truncated = response['IsTruncated']
            for role in response_roles:
                roles.append(role['RoleName'])
            while is_truncated is True:
                marker = response['Marker']
                response = self.iam_childaccount_client.list_roles(Marker=marker)
                response_roles = response['Roles']
                is_truncated = response['IsTruncated']
                for role in response_roles:
                    roles.append(role['RoleName'])
            return roles
        except Exception as exception_object:
            print(str(exception_object))
            print("Error occurred while listing IAM roles")
            return roles

    """Update the trust policy of the platform inflation role"""
    def update_assume_role_policy_from_child_account(self, role_name):
        print("Inside update_assume_role_policy_from_child_account")
        try:
            response_role = self.iam_childaccount_client.get_role(RoleName=role_name)['Role']
            child_assume_custadmin_role_policy_document = response_role['AssumeRolePolicyDocument']
            print("Child assume role policy for child account: " + str(child_assume_custadmin_role_policy_document))
            print("Automation assume role policy: " + str(self.assume_role_policy_document_for_account_inflation))
            child_custadmin_role_services = \
            child_assume_custadmin_role_policy_document['Statement'][0]['Principal']['Service']
            automation_custadmin_role_services = \
            self.assume_role_policy_document_for_account_inflation['Statement'][0]['Principal']['Service']
            for role_service in automation_custadmin_role_services:
                child_custadmin_role_services.append(role_service)
            set_child_custadmin_role_services = set(child_custadmin_role_services)
            child_assume_custadmin_role_policy_document['Statement'][0]['Principal']['Service'] = list(
                set_child_custadmin_role_services)
            print("final child_assume_platform_service_inflation_document>>>>>",
                  child_assume_custadmin_role_policy_document)

            return child_assume_custadmin_role_policy_document
        except Exception as exception_object:
            print("Error occurred while modifying trusted entities in {} role in inflation update".format(role_name))
            print(str(exception_object))


    # Append Trusted users from both Automation Account and Child Account in platform_service_readonly Role
    def update_assume_role_policy_for_readonly(self, role_name):
        print("Inside update_assume_role_policy_for_readonly")
        try:
            response_role = self.iam_childaccount_client.get_role(RoleName=role_name)['Role']
            child_assume_role_policy_document = response_role['AssumeRolePolicyDocument']
            print("Child assume role policy for readonly: " + str(child_assume_role_policy_document))
            if 'AWS' in child_assume_role_policy_document['Statement'][0]['Principal'].keys():
                print("{} Role having trusted entity in child account. So update this document".format(role_name))
            print("Final child_assume_role_policy_document>>>>>", child_assume_role_policy_document)

            return child_assume_role_policy_document
        except Exception as exception_object:
            print("Error occurred while modifying trusted entities in {} role in read only update".format(role_name))
            print(str(exception_object))


    """Create/Update the cloud health role policy"""
    def create_update_cloud_helth(self,policy_arr):
        policy_create_update_status = False
        try:
            print("Before Platform_CloudHealthPolicy")
            policy_response = self.iam_masteraccount_client.get_policy(
                PolicyArn=self.cloud_health_policy_arn)

            self.child_cloudhealth_policy_arn = "arn:aws:iam::{}:policy/platform_cloud_health_policy".format(
                self.account_number)
            latest_policy_version = (policy_response.get('Policy')).get('DefaultVersionId')
            policy_document_response = \
                self.iam_masteraccount_client.get_policy_version(
                    PolicyArn=self.cloud_health_policy_arn, VersionId=latest_policy_version)
            cloudhealth_policy_document = (
                policy_document_response.get('PolicyVersion')).get('Document')
            if "platform_cloud_health_policy" not in policy_arr:
                self.iam_childaccount_client.create_policy(
                    PolicyName="platform_cloud_health_policy",
                    PolicyDocument=json.dumps(cloudhealth_policy_document),
                    Description="platform_cloud_health_policy")
            else:
                response = self.iam_childaccount_client.list_policy_versions(
                    PolicyArn=self.child_cloudhealth_policy_arn)

                if (response['Versions'].__len__() == 5):
                    response = self.iam_childaccount_client.delete_policy_version(
                        PolicyArn=self.child_cloudhealth_policy_arn,
                        VersionId=response['Versions'][response['Versions'].__len__() - 1]['VersionId'])
                self.iam_childaccount_client.create_policy_version(
                    PolicyArn=self.child_cloudhealth_policy_arn,
                    PolicyDocument=json.dumps(cloudhealth_policy_document),
                    SetAsDefault=True)
            print("After Platform_CloudHealthPolicy")
            policy_create_update_status = True
        except Exception as e:
            print (str(e))
            policy_create_update_status = False
        return policy_create_update_status

    """Create/Update the platform service inflation role policy"""
    def crete_update_inflation_policy(self,policy_arr):
        policy_create_update_status = False
        try:
            print("Before Inflation Policy")
            policy_response = self.iam_masteraccount_client.get_policy(
                PolicyArn=self.inflation_policy_arn)
            self.child_inflation_policy_arn = \
                "arn:aws:iam::{}:policy/platform_inflation_policy".format(self.account_number)
            latest_policy_version = (policy_response.get('Policy')).get('DefaultVersionId')
            policy_document_response = \
                self.iam_masteraccount_client.get_policy_version(
                    PolicyArn=self.inflation_policy_arn, VersionId=latest_policy_version)
            inflation_policy_document = (
                policy_document_response.get('PolicyVersion')).get('Document')
            inflation_policy_document['Statement'][1]['Resource'] = ["*",
                "arn:aws:iam::{}:role/aws-service-role/guardduty.amazonaws.com/AWSServiceRoleForAmazonGuardDuty".format(
                    self.account_number)]
            print (inflation_policy_document)
            if "platform_inflation_policy" not in policy_arr:
                self.iam_childaccount_client.create_policy(
                    PolicyName="platform_inflation_policy",
                    PolicyDocument=json.dumps(inflation_policy_document),
                    Description="platform_inflation_policy")
            else:
                response = self.iam_childaccount_client.list_policy_versions(
                    PolicyArn=self.child_inflation_policy_arn)
                if (response['Versions'].__len__() == 5):
                    response = self.iam_childaccount_client.delete_policy_version(
                        PolicyArn=self.child_inflation_policy_arn,
                        VersionId=response['Versions'][response['Versions'].__len__() - 1]['VersionId'])
                self.iam_childaccount_client.create_policy_version(
                    PolicyArn=self.child_inflation_policy_arn,
                    PolicyDocument=json.dumps(inflation_policy_document),
                    SetAsDefault=True)
            print("After Inflation Policy")
            policy_create_update_status = True
        except Exception as e:
            print (str(e))
            policy_create_update_status = False
        return policy_create_update_status

    """Create/Update the platform service inflation role policy_2"""
    def crete_update_inflation_policy_2(self,policy_arr):
        policy_create_update_status = False
        try:
            print("Before Inflation Policy_2")
            policy_response = self.iam_masteraccount_client.get_policy(
                PolicyArn=self.inflation_policy_2_arn)
            self.child_inflation_policy_2_arn = \
                "arn:aws:iam::{}:policy/platform_inflation_policy_2".format(self.account_number)
            latest_policy_version = (policy_response.get('Policy')).get('DefaultVersionId')
            policy_document_response = \
                self.iam_masteraccount_client.get_policy_version(
                    PolicyArn=self.inflation_policy_2_arn, VersionId=latest_policy_version)
            inflation_policy_2_document = (
                policy_document_response.get('PolicyVersion')).get('Document')
            inflation_policy_2_document['Statement'][1]['Resource'] = ["*",
                "arn:aws:iam::{}:role/aws-service-role/guardduty.amazonaws.com/AWSServiceRoleForAmazonGuardDuty".format(
                    self.account_number)]
            print (inflation_policy_2_document)
            if "platform_inflation_policy_2" not in policy_arr:
                self.iam_childaccount_client.create_policy(
                    PolicyName="platform_inflation_policy_2",
                    PolicyDocument=json.dumps(inflation_policy_2_document),
                    Description="platform_inflation_policy_2")
            else:
                response = self.iam_childaccount_client.list_policy_versions(
                    PolicyArn=self.child_inflation_policy_2_arn)
                if (response['Versions'].__len__() == 5):
                    response = self.iam_childaccount_client.delete_policy_version(
                        PolicyArn=self.child_inflation_policy_2_arn,
                        VersionId=response['Versions'][response['Versions'].__len__() - 1]['VersionId'])
                self.iam_childaccount_client.create_policy_version(
                    PolicyArn=self.child_inflation_policy_2_arn,
                    PolicyDocument=json.dumps(inflation_policy_2_document),
                    SetAsDefault=True)
            print("After Inflation Policy_2")
            policy_create_update_status = True
        except Exception as e:
            print (str(e))
            policy_create_update_status = False
        return policy_create_update_status

    """Create/Update the iam pass policy"""
    def create_update_iam_pass_policy(self,policy_arr):
        policy_create_update_status = False
        try:
            print("IAM_PASS_ROLE_POLICY")
            policy_response = self.iam_masteraccount_client.get_policy(
                PolicyArn=self.ccs_iam_passrole_policy_arn)
            latest_policy_version = (policy_response.get('Policy')).get('DefaultVersionId')
            policy_document_response = self.iam_masteraccount_client.get_policy_version(
                PolicyArn=self.ccs_iam_passrole_policy_arn, VersionId=latest_policy_version)
            ccs_iam_passrole_policy_document = (
                policy_document_response.get('PolicyVersion')).get('Document')
            self.child_iam_passrole_policy_arn = \
                "arn:aws:iam::{}:policy/platform_iam_pass_role_policy".format(self.account_number)
            if "platform_iam_pass_role_policy" not in policy_arr:
                print("inside if ")
                self.iam_childaccount_client.create_policy(PolicyName="platform_iam_pass_role_policy",
                                                           PolicyDocument=json.dumps(
                                                               ccs_iam_passrole_policy_document),
                                                           Description="Policy to pass IAM Role for Maintenance Window Task Orchestration")
            else:
                print("inside else ")
                response = self.iam_childaccount_client.list_policy_versions(
                    PolicyArn=self.child_iam_passrole_policy_arn)
                if (response['Versions'].__len__() == 5):
                    print("inside if 2")
                    del_response = self.iam_childaccount_client.delete_policy_version(
                        PolicyArn=self.child_iam_passrole_policy_arn,
                        VersionId=response['Versions'][response['Versions'].__len__() - 1]['VersionId'])
                self.iam_childaccount_client.create_policy_version(PolicyArn=self.child_iam_passrole_policy_arn,
                                                                   PolicyDocument=json.dumps(
                                                                       ccs_iam_passrole_policy_document),
                                                                   SetAsDefault=True)
            policy_create_update_status = True
        except Exception as e:
            print (str(e))
            policy_create_update_status = False
        return policy_create_update_status

    """Create/Update the sts full access policy"""
    def create_update_sts_full_access_policy(self,policy_arr):
        policy_create_update_status = False
        try:
            policy_response = self.iam_masteraccount_client.get_policy(
                PolicyArn=self.sts_fullaccess)
            latest_policy_version = (policy_response.get('Policy')).get('DefaultVersionId')
            policy_document_response = self.iam_masteraccount_client.get_policy_version(
                PolicyArn=self.sts_fullaccess, VersionId=latest_policy_version)
            platform_sts_fullaccess_policy_document = (
                policy_document_response.get('PolicyVersion')).get('Document')
            self.child_sts_fullaccess = \
                "arn:aws:iam::{}:policy/platform_sts_full_access".format(self.account_number)
            if "platform_sts_full_access" not in policy_arr:
                self.iam_childaccount_client.create_policy(PolicyName="platform_sts_full_access",
                                                           PolicyDocument=json.dumps(
                                                               platform_sts_fullaccess_policy_document),
                                                           Description="Policy to give full access to assume the role")
            else:
                response = self.iam_childaccount_client.list_policy_versions(
                    PolicyArn=self.child_sts_fullaccess)
                if (response['Versions'].__len__() == 5):
                    del_response = self.iam_childaccount_client.delete_policy_version(
                        PolicyArn=self.child_sts_fullaccess,
                        VersionId=response['Versions'][response['Versions'].__len__() - 1]['VersionId'])
                self.iam_childaccount_client.create_policy_version(PolicyArn=self.child_sts_fullaccess,
                                                                   PolicyDocument=json.dumps(
                                                                       platform_sts_fullaccess_policy_document),
                                                                   SetAsDefault=True)
            print("child_sts_fullaccess created")
            policy_create_update_status = True
        except Exception as e:
            print (str(e))
            policy_create_update_status = False

        return policy_create_update_status

    """Create/Update platform ec2instance policy"""
    def create_update_platform_ec2instance_policy(self,policy_arr):
        policy_create_update_status = False
        try:
            policy_response = self.iam_masteraccount_client.get_policy(
                PolicyArn=self.ec2instance_policy_arn)
            latest_policy_version = (policy_response.get('Policy')).get('DefaultVersionId')
            policy_document_response = self.iam_masteraccount_client.get_policy_version(
                PolicyArn=self.ec2instance_policy_arn, VersionId=latest_policy_version)
            platform_ec2instance_policy_document = (
                policy_document_response.get('PolicyVersion')).get('Document')
            self.child_ec2instance = \
                "arn:aws:iam::{}:policy/platform_ec2instance_policy".format(self.account_number)
            if "platform_ec2instance_policy" not in policy_arr:
                self.iam_childaccount_client.create_policy(PolicyName="platform_ec2instance_policy",
                                                           PolicyDocument=json.dumps(
                                                               platform_ec2instance_policy_document),
                                                           Description="Policy to give full access to assume the role")
            else:
                response = self.iam_childaccount_client.list_policy_versions(
                    PolicyArn=self.child_ec2instance)
                if (response['Versions'].__len__() == 5):
                    del_response = self.iam_childaccount_client.delete_policy_version(
                        PolicyArn=self.child_ec2instance,
                        VersionId=response['Versions'][response['Versions'].__len__() - 1]['VersionId'])
                self.iam_childaccount_client.create_policy_version(PolicyArn=self.child_ec2instance,
                                                                   PolicyDocument=json.dumps(
                                                                       platform_ec2instance_policy_document),
                                                                   SetAsDefault=True)
            print("child platform_ec2instance_policy created")
            policy_create_update_status = True
        except Exception as e:
            print (str(e))
            policy_create_update_status = False

        return policy_create_update_status

    """Create/Update platform itom policy"""
    def create_update_platform_itom_policy(self,policy_arr):
        policy_create_update_status = False
        try:
            print("Before ITOM Policy")
            policy_response = self.iam_masteraccount_client.get_policy(
                PolicyArn=self.itom_policy_arn)
            self.child_itom_policy_arn = \
                "arn:aws:iam::{}:policy/ServiceNow_ITOM_Discovery_Child_Policy".format(self.account_number)
            latest_policy_version = (policy_response.get('Policy')).get('DefaultVersionId')
            policy_document_response = \
                self.iam_masteraccount_client.get_policy_version(
                    PolicyArn=self.itom_policy_arn, VersionId=latest_policy_version)
            platform_itom_policy_document = (
                policy_document_response.get('PolicyVersion')).get('Document')
            print (platform_itom_policy_document)
            if "ServiceNow_ITOM_Discovery_Child_Policy" not in policy_arr:
                self.iam_childaccount_client.create_policy(
                    PolicyName="ServiceNow_ITOM_Discovery_Child_Policy",
                    PolicyDocument=json.dumps(platform_itom_policy_document),
                    Description="ServiceNow_ITOM_Discovery_Child_Policy")
            else:
                response = self.iam_childaccount_client.list_policy_versions(
                    PolicyArn=self.child_itom_policy_arn)
                if (response['Versions'].__len__() == 5):
                    response = self.iam_childaccount_client.delete_policy_version(
                        PolicyArn=self.child_itom_policy_arn,
                        VersionId=response['Versions'][response['Versions'].__len__() - 1]['VersionId'])
                self.iam_childaccount_client.create_policy_version(
                    PolicyArn=self.child_itom_policy_arn,
                    PolicyDocument=json.dumps(platform_itom_policy_document),
                    SetAsDefault=True)
            print("After ITOM Policy")
            policy_create_update_status = True
        except Exception as e:
            print (str(e))
            policy_create_update_status = False
        return policy_create_update_status

    """Create/Update business iot policy"""
    def create_update_business_cdf_execution_role(self, policy_arr):
        policy_create_update_status = False
        try:
            print("Before IOT Policy")
            policy_response = self.iam_masteraccount_client.get_policy(
                PolicyArn=self.iot_policy_arn)
            self.child_iot_cdf_policy_arn = \
                "arn:aws:iam::{}:policy/IOT_Stackset_Execution_Child_Policy".format(self.account_number)
            latest_policy_version = (policy_response.get('Policy')).get('DefaultVersionId')
            policy_document_response = \
                self.iam_masteraccount_client.get_policy_version(
                    PolicyArn=self.iot_policy_arn, VersionId=latest_policy_version)
            platform_iot_policy_document = (
                policy_document_response.get('PolicyVersion')).get('Document')
            print (platform_iot_policy_document)
            if "IOT_Stackset_Execution_Child_Policy" not in policy_arr:
                self.iam_childaccount_client.create_policy(
                    PolicyName="IOT_Stackset_Execution_Child_Policy",
                    PolicyDocument=json.dumps(platform_iot_policy_document),
                    Description="IOT_Stackset_Execution_Child_Policy")
            else:
                response = self.iam_childaccount_client.list_policy_versions(
                    PolicyArn=self.child_iot_cdf_policy_arn)
                if (response['Versions'].__len__() == 5):
                    response = self.iam_childaccount_client.delete_policy_version(
                        PolicyArn=self.child_iot_cdf_policy_arn,
                        VersionId=response['Versions'][response['Versions'].__len__() - 1]['VersionId'])
                self.iam_childaccount_client.create_policy_version(
                    PolicyArn=self.child_iot_cdf_policy_arn,
                    PolicyDocument=json.dumps(platform_iot_policy_document),
                    SetAsDefault=True)
            print("After IOT Policy")
            policy_create_update_status = True
        except Exception as e:
            print (str(e))
            policy_create_update_status = False
        return policy_create_update_status

    """Create/Update ListEC2ForFNMSPolicy policy Private"""
    def create_update_platform_ListEC2ForFNMSpvt_policy(self, policy_arr):
        policy_create_update_status = False
        try:
            print("Before ListEC2ForFNMSPolicy Policy")
            policy_response = self.iam_masteraccount_client.get_policy(
                PolicyArn=self.ListEC2ForFNMSpvt_policy_arn)
            self.child_ListEC2ForFNMSpvt_policy_arn = \
                "arn:aws:iam::{}:policy/platform_ListEC2ForFNMSPolicyPrivate".format(self.account_number)
            latest_policy_version = (policy_response.get('Policy')).get('DefaultVersionId')
            policy_document_response = \
                self.iam_masteraccount_client.get_policy_version(
                    PolicyArn=self.ListEC2ForFNMSpvt_policy_arn, VersionId=latest_policy_version)
            platform_ListEC2ForFNMS_policy_document = (
                policy_document_response.get('PolicyVersion')).get('Document')
            print (platform_ListEC2ForFNMS_policy_document)
            if "platform_ListEC2ForFNMSPolicyPrivate" not in policy_arr:
                self.iam_childaccount_client.create_policy(
                    PolicyName="platform_ListEC2ForFNMSPolicyPrivate",
                    PolicyDocument=json.dumps(platform_ListEC2ForFNMS_policy_document),
                    Description="platform_ListEC2ForFNMSPolicyPrivate")
            else:
                response = self.iam_childaccount_client.list_policy_versions(
                    PolicyArn=self.child_ListEC2ForFNMSpvt_policy_arn)
                if (response['Versions'].__len__() == 5):
                    response = self.iam_childaccount_client.delete_policy_version(
                        PolicyArn=self.child_ListEC2ForFNMSpvt_policy_arn,
                        VersionId=response['Versions'][response['Versions'].__len__() - 1]['VersionId'])
                self.iam_childaccount_client.create_policy_version(
                    PolicyArn=self.child_ListEC2ForFNMSpvt_policy_arn,
                    PolicyDocument=json.dumps(platform_ListEC2ForFNMS_policy_document),
                    SetAsDefault=True)
            print("After ListEC2ForFNMSPolicy Policy")
            policy_create_update_status = True
        except Exception as e:
            print (str(e))
            policy_create_update_status = False
        return policy_create_update_status

    """Create/Update ListEC2ForFNMSPolicy policy Public"""
    def create_update_platform_ListEC2ForFNMSpub_policy(self, policy_arr):
        policy_create_update_status = False
        try:
            print("Before ListEC2ForFNMSPolicy Policy")
            policy_response = self.iam_masteraccount_client.get_policy(
                PolicyArn=self.ListEC2ForFNMSpub_policy_arn)
            self.child_ListEC2ForFNMSpub_policy_arn = \
                "arn:aws:iam::{}:policy/platform_ListEC2ForFNMSPolicyPublic".format(self.account_number)
            latest_policy_version = (policy_response.get('Policy')).get('DefaultVersionId')
            policy_document_response = \
                self.iam_masteraccount_client.get_policy_version(
                    PolicyArn=self.ListEC2ForFNMSpub_policy_arn, VersionId=latest_policy_version)
            platform_ListEC2ForFNMS_policy_document = (
                policy_document_response.get('PolicyVersion')).get('Document')
            print (platform_ListEC2ForFNMS_policy_document)
            if "platform_ListEC2ForFNMSPolicyPublic" not in policy_arr:
                self.iam_childaccount_client.create_policy(
                    PolicyName="platform_ListEC2ForFNMSPolicyPublic",
                    PolicyDocument=json.dumps(platform_ListEC2ForFNMS_policy_document),
                    Description="platform_ListEC2ForFNMSPolicyPublic")
            else:
                response = self.iam_childaccount_client.list_policy_versions(
                    PolicyArn=self.child_ListEC2ForFNMSpub_policy_arn)
                if (response['Versions'].__len__() == 5):
                    response = self.iam_childaccount_client.delete_policy_version(
                        PolicyArn=self.child_ListEC2ForFNMSpub_policy_arn,
                        VersionId=response['Versions'][response['Versions'].__len__() - 1]['VersionId'])
                self.iam_childaccount_client.create_policy_version(
                    PolicyArn=self.child_ListEC2ForFNMSpub_policy_arn,
                    PolicyDocument=json.dumps(platform_ListEC2ForFNMS_policy_document),
                    SetAsDefault=True)
            print("After ListEC2ForFNMSPolicy Policy")
            policy_create_update_status = True
        except Exception as e:
            print (str(e))
            policy_create_update_status = False
        return policy_create_update_status


    """Create/Update SNOW_SGC policy"""
    def create_update_SNOW_SGC_role(self, policy_arr):
        policy_create_update_status = False
        try:
            print("Before SNOW_SGC Policy")
            policy_response = self.iam_masteraccount_client.get_policy(
                PolicyArn=self.snow_sgc_policy_arn)
            self.child_snow_sgc_policy_arn = \
                "arn:aws:iam::{}:policy/platform_SnowOrganizationAccountAccessPolicy".format(self.account_number)
            latest_policy_version = (policy_response.get('Policy')).get('DefaultVersionId')
            policy_document_response = \
                self.iam_masteraccount_client.get_policy_version(
                    PolicyArn=self.snow_sgc_policy_arn, VersionId=latest_policy_version)
            platform_SNOW_SGC_policy_document = (
                policy_document_response.get('PolicyVersion')).get('Document')
            print (platform_SNOW_SGC_policy_document)
            if "platform_SnowOrganizationAccountAccessPolicy" not in policy_arr:
                self.iam_childaccount_client.create_policy(
                    PolicyName="platform_SnowOrganizationAccountAccessPolicy",
                    PolicyDocument=json.dumps(platform_SNOW_SGC_policy_document),
                    Description="platform_SnowOrganizationAccountAccessPolicy")
            else:
                response = self.iam_childaccount_client.list_policy_versions(
                    PolicyArn=self.child_snow_sgc_policy_arn)
                if (response['Versions'].__len__() == 5):
                    response = self.iam_childaccount_client.delete_policy_version(
                        PolicyArn=self.child_snow_sgc_policy_arn,
                        VersionId=response['Versions'][response['Versions'].__len__() - 1]['VersionId'])
                self.iam_childaccount_client.create_policy_version(
                    PolicyArn=self.child_snow_sgc_policy_arn,
                    PolicyDocument=json.dumps(platform_SNOW_SGC_policy_document),
                    SetAsDefault=True)
            print("After SNOW_SGC Policy")
            policy_create_update_status = True
        except Exception as e:
            print (str(e))
            policy_create_update_status = False
        return policy_create_update_status


    """Create all the policies required by the roles in the business accounts"""
    def createPolicy(self):
        policy_cloud_health_status = False
        policy_inflation_status = False
        policy_iam_pass_status = False
        policy_sts_status = False
        platform_ec2instance_status = False
        policy_2_inflation_status = False
        policy_itom_status = False
        business_IOT_CDF_status = False
        platform_snow_sgc_status = False
        platform_ListEC2ForFNMSPolicy_status = False
        try:
            policy_arr = []
            response = self.iam_childaccount_client.list_policies(Scope='Local')
            policies = response['Policies']
            is_truncated = response['IsTruncated']
            for policy in policies:
                policy_arr.append(policy['PolicyName'])
            while is_truncated is True:
                marker = response['Marker']
                response = self.iam_childaccount_client.list_policies(Scope='Local', Marker=marker)
                policies = response['Policies']
                is_truncated = response['IsTruncated']
                for policy in policies:
                    policy_arr.append(policy['PolicyName'])


            #Create or update Cloud Health Policy
            policy_cloud_health_status = self.create_update_cloud_helth(policy_arr)

            #Create or update Inflation Policy
            policy_inflation_status = self.crete_update_inflation_policy(policy_arr)

            #Create or update Inflation_2 Policy
            policy_2_inflation_status = self.crete_update_inflation_policy_2(policy_arr)

            #IAM_PASS_ROLE_POLICY
            policy_iam_pass_status = self.create_update_iam_pass_policy(policy_arr)

            # create sts full access policy
            policy_sts_status = self.create_update_sts_full_access_policy(policy_arr)

            # create platform ec2instance policy
            platform_ec2instance_status = self.create_update_platform_ec2instance_policy(policy_arr)

            # create platform itom policy
            policy_itom_status = self.create_update_platform_itom_policy(policy_arr)

            # create Business CDF Execution stackset policy
            if self.IsIOTAccount == 'Yes':
                business_IOT_CDF_status = self.create_update_business_cdf_execution_role(policy_arr)
            else:
                business_IOT_CDF_status = False

            # create platform FNMSPolic policy pvt
            if self.AccountType == 'private' or self.AccountType == 'hybrid':
                platform_ListEC2ForFNMSPolicy_status = self.create_update_platform_ListEC2ForFNMSpvt_policy(policy_arr)
            else:
                # create platform FNMSPolic policy pub
                platform_ListEC2ForFNMSPolicy_status = self.create_update_platform_ListEC2ForFNMSpub_policy(policy_arr)


            # create SNOW_SGC poolicy
            platform_snow_sgc_status = self.create_update_SNOW_SGC_role(policy_arr)
        except Exception as e:
            print (str(e))
            policy_cloud_health_status = False
            policy_inflation_status = False
            policy_2_inflation_status = False
            policy_iam_pass_status = False
            policy_sts_status = False
            platform_ec2instance_status = False
            policy_itom_status = False
            business_IOT_CDF_status = False
            platform_ListEC2ForFNMSPolicy_status = False
        return policy_cloud_health_status,policy_inflation_status,policy_2_inflation_status,policy_iam_pass_status,policy_sts_status,platform_ec2instance_status,policy_itom_status,business_IOT_CDF_status,platform_ListEC2ForFNMSPolicy_status,platform_snow_sgc_status

    """Delete role and all its dependencies"""
    def delete_role(self, role_name):
        role_deletion = False
        role_deletion_status = False
        try:
            role = self.iam_childaccount_client.get_role(RoleName=role_name)['Role']
            role_last_used = role.get('RoleLastUsed', None)
            if not role_last_used or 'LastUsedDate' not in role_last_used:
                print("Role {} was never used so it will be deleted!!!".format(role_name))
                role_deletion = True
            else:
                last_used_delta = datetime.datetime.now() - role_last_used['LastUsedDate'].replace(tzinfo=None)
                msg = "Role {} was used {} days ago, on {} in region {}".format(role_name, last_used_delta.days, role_last_used['LastUsedDate'].isoformat(), role_last_used['Region'])
                if last_used_delta.days >= 180:
                    print("{}: >=180 days so delete!!!".format(msg))
                    role_deletion = True
                else:
                    print("{}: <180 days so do not delete but keep an eye!!!".format(msg))
                    role_deletion = False
            if role_deletion:
                role_policies = self.iam_childaccount_client.list_role_policies(RoleName=role_name)['PolicyNames']
                for rpn in role_policies:
                    self.iam_childaccount_client.delete_role_policy(RoleName=role_name, PolicyName=rpn)
                attached_role_policies = self.iam_childaccount_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
                for arp in attached_role_policies:
                    self.iam_childaccount_client.detach_role_policy(RoleName=role_name, PolicyArn=arp['PolicyArn'])
                instance_profiles = self.iam_childaccount_client.list_instance_profiles_for_role(RoleName=role_name)['InstanceProfiles']
                for ip in instance_profiles:
                    self.iam_childaccount_client.remove_role_from_instance_profile(RoleName=role_name, InstanceProfileName=ip['InstanceProfileName'])
                    if len(ip['Roles']) <= 1:
                        self.iam_childaccount_client.delete_instance_profile(InstanceProfileName=ip['InstanceProfileName'])
                self.iam_childaccount_client.delete_role(RoleName=role_name)
                print("Role " + role_name + " deleted successfully!!!")
            role_deletion_status = True
        except Exception as e:
            print("exception", str(e))
            role_deletion_status = False
        return role_deletion_status

    """Create all the roles in the business accounts"""
    def create_role(self,role_name):
        role_creation_update_status = False
        try:
            if role_name == CLOUDHEALTH_ROLE_NAME:
                self.iam_childaccount_client.create_role(RoleName=CLOUDHEALTH_ROLE_NAME,
                                                         AssumeRolePolicyDocument=
                                                         json.dumps(
                                                             self.assume_role_policy_document_for_cloudhealth),
                                                         Description='Role for Integration with Cloud Health')
                self.attach_role_policy_routine(CLOUDHEALTH_ROLE_NAME,self.child_cloudhealth_policy_arn)

                print("Cloud health role created successfully!!!")
            elif role_name == ACCOUNT_INFLATION_ROLE_NAME:
                self.iam_childaccount_client.create_role(RoleName=ACCOUNT_INFLATION_ROLE_NAME,
                                                         AssumeRolePolicyDocument=json.dumps(
                                                             self.assume_role_policy_document_for_account_inflation),
                                                         Description='Account Inflation Role')
                self.attach_role_policy_routine(ACCOUNT_INFLATION_ROLE_NAME,self.child_inflation_policy_arn)
                self.attach_role_policy_routine(ACCOUNT_INFLATION_ROLE_NAME,self.child_inflation_policy_2_arn)
                self.attach_role_policy_routine(ACCOUNT_INFLATION_ROLE_NAME,self.readonly_policy_arn)
                print("Inflation Role created successfully!!!")
            elif role_name == INSTANCE_ROLE_NAME:

                self.iam_childaccount_client.create_role(RoleName=INSTANCE_ROLE_NAME,
                                                         AssumeRolePolicyDocument=json.dumps(
                                                             self.assume_role_policy_document_for_instance_role),
                                                         Description='Role used by EC2 Instances')
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.ssm_managed_arn)
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.cloudwatch_plicy_arn)
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.ssm_managed_arn_directory_Service)
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.child_iam_passrole_policy_arn)
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.readonly_policy_arn)
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.child_sts_fullaccess)
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.child_ec2instance)
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.back_up_arn)
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.ec2_fullaccess_policy_arn)
                print("Instance Role created successfully!!!")

                self.iam_childaccount_client.create_instance_profile(
                    InstanceProfileName=INSTANCE_ROLE_NAME)
                print("Instance profile {} created successfully!!!".format(INSTANCE_ROLE_NAME))

                self.iam_childaccount_client.add_role_to_instance_profile(
                    InstanceProfileName=INSTANCE_ROLE_NAME, RoleName=INSTANCE_ROLE_NAME)
                print("Instance profile {} attached to IAM role {} successfully!!!".format(
                    INSTANCE_ROLE_NAME, INSTANCE_ROLE_NAME))
            elif role_name == READONLY_ROLE_NAME:
                self.iam_childaccount_client.create_role(RoleName=READONLY_ROLE_NAME,
                                                         AssumeRolePolicyDocument=json.dumps(
                                                             self.assume_role_policy_document_for_readonly),
                                                         Description='ReadOnly Role')
                self.attach_role_policy_routine(READONLY_ROLE_NAME,self.readonly_policy_arn)
                print("readonly role created successfully!!!")
            elif role_name == CUSTSERVICE_ROLE_NAME:
                print("Busness Role ignored!!!")
            elif role_name == CUSTSERVICE_READONLY_ROLE_NAME:
                print("Business readonly Role ignored!!!")
            elif role_name == PLATFORM_BACK_UP:
                self.iam_childaccount_client.create_role(RoleName=PLATFORM_BACK_UP,
                                                         AssumeRolePolicyDocument=json.dumps(
                                                             self.assume_role_policy_back_up),
                                                         Description='PLATFORM BACK UP ROLE')
                self.attach_role_policy_routine(PLATFORM_BACK_UP,self.back_up_arn)
                self.attach_role_policy_routine(PLATFORM_BACK_UP,self.child_iam_passrole_policy_arn)
                self.attach_role_policy_routine(PLATFORM_BACK_UP,self.back_up_servicerole_arn)
                self.attach_role_policy_routine(PLATFORM_BACK_UP,self.restore_servicerole_arn)
                self.attach_role_policy_routine(PLATFORM_BACK_UP,self.sns_full_access)
                print("Platform back up Role created successfully!!!")
            elif role_name == PLATFORM_ITOM_ROLE:
                self.iam_childaccount_client.create_role(RoleName=PLATFORM_ITOM_ROLE,
                                                         AssumeRolePolicyDocument=json.dumps(
                                                             self.assume_role_policy_itom_readonly),
                                                         Description='PLATFORM ITOM ROLE')
                self.attach_role_policy_routine(PLATFORM_ITOM_ROLE,self.child_itom_policy_arn)
                print("Platform ITOM Role created successfully!!!")

            elif role_name == IOT_SHELL_CDF_EXECUTION_ROLE:
                if self.IsIOTAccount == 'Yes':
                    self.iam_childaccount_client.create_role(RoleName=IOT_SHELL_CDF_EXECUTION_ROLE,
                                                             AssumeRolePolicyDocument=json.dumps(
                                                                 self.assume_role_policy_iot_cdf),
                                                             Description='Business CDF Execution Role',
                                                             Tags=[{'Key':'Platform',
                                                                     'Value':'CDF'}])
                    self.attach_role_policy_routine(IOT_SHELL_CDF_EXECUTION_ROLE,self.child_iot_cdf_policy_arn)
                    print("Business CDF Execution Role created successfully!!!")
                else:
                    print("Not an IOT Account hence skipping CDF execution Role")

            elif role_name == PLATFORM_ListEC2ForFNM_ROLE:
                if self.AccountType == 'private' or self.AccountType == 'hybrid':
                    self.iam_childaccount_client.create_role(RoleName=PLATFORM_ListEC2ForFNM_ROLE,
                                                             AssumeRolePolicyDocument=json.dumps(
                                                                 self.assume_role_policy_FlexeraBeacon_pvt),
                                                             Description='Business ListEC2ForFNM Execution Role',
                                                             Tags=[{'Key':'Platform',
                                                                     'Value':'Flexera_Beacon'}])
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.child_ListEC2ForFNMSpvt_policy_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.child_ec2instance)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.child_iam_passrole_policy_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.child_sts_fullaccess)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.readonly_policy_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.cloudwatch_plicy_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.ssm_managed_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.ssm_managed_arn_directory_Service)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.back_up_arn)
                    print("Business ListEC2ForFNM Execution Role created successfully!!!")
                else:
                    self.iam_childaccount_client.create_role(RoleName=PLATFORM_ListEC2ForFNM_ROLE,
                                                             AssumeRolePolicyDocument=json.dumps(
                                                                 self.assume_role_policy_FlexeraBeacon_pub),
                                                             Description='Business ListEC2ForFNM Execution Role',
                                                             Tags=[{'Key':'Platform',
                                                                     'Value':'Flexera_Beacon'}])
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.child_ListEC2ForFNMSpub_policy_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.child_ec2instance)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.child_iam_passrole_policy_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.child_sts_fullaccess)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.readonly_policy_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.cloudwatch_plicy_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.ssm_managed_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.ssm_managed_arn_directory_Service)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.back_up_arn)
                    print("Business ListEC2ForFNM Execution Role created successfully!!!")

            elif role_name == PLATFORM_SNOW_SGC_ROLE:
                self.iam_childaccount_client.create_role(RoleName=PLATFORM_SNOW_SGC_ROLE,
                                                            AssumeRolePolicyDocument=json.dumps(
                                                                self.assume_role_policy_SNOW_SGC),
                                                            Description='SNOW_SGC Role')
                self.attach_role_policy_routine(PLATFORM_SNOW_SGC_ROLE,self.child_snow_sgc_policy_arn)
                print("SNOW_SGC Role created successfully!!!")
            role_creation_update_status = True
        except Exception as e:
            print("exception",str(e))
            role_creation_update_status = False
        return role_creation_update_status

    """Update all the roles required in the business accounts"""
    def update_role(self,role_name):
        role_creation_update_status = False
        try:
            if role_name == CLOUDHEALTH_ROLE_NAME:
                self.iam_childaccount_client.update_assume_role_policy(RoleName=CLOUDHEALTH_ROLE_NAME,
                                                                       PolicyDocument=
                                                                       json.dumps(
                                                                           self.assume_role_policy_document_for_cloudhealth))
                self.attach_role_policy_routine(CLOUDHEALTH_ROLE_NAME,self.child_cloudhealth_policy_arn)
                print("Cloud health updated successfully!!!")
            elif role_name == ACCOUNT_INFLATION_ROLE_NAME:
                print("Role inflation trying to update")
                # While updating the AccountManagement product, trusted services removing in platform_service_inflation started
                final_assume_role_policy_document_for_account_inflation = self.update_assume_role_policy_from_child_account(
                    role_name)
                self.iam_childaccount_client.update_assume_role_policy(
                    RoleName=ACCOUNT_INFLATION_ROLE_NAME,
                    PolicyDocument=json.dumps(
                        final_assume_role_policy_document_for_account_inflation))
                # While updating the AccountManagement product, trusted services removing in CCS_Inflation Role ended
                self.attach_role_policy_routine(ACCOUNT_INFLATION_ROLE_NAME,self.child_inflation_policy_arn)
                self.attach_role_policy_routine(ACCOUNT_INFLATION_ROLE_NAME,self.child_inflation_policy_2_arn)
                self.attach_role_policy_routine(ACCOUNT_INFLATION_ROLE_NAME,self.readonly_policy_arn)
                print("Role inflation updated successfully!!!")
            elif role_name == INSTANCE_ROLE_NAME:
                self.iam_childaccount_client.update_assume_role_policy(RoleName=INSTANCE_ROLE_NAME,
                                                                       PolicyDocument=json.dumps(
                                                                           self.assume_role_policy_document_for_instance_role))
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.ssm_managed_arn)
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.cloudwatch_plicy_arn)
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.ssm_managed_arn_directory_Service)
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.child_iam_passrole_policy_arn)
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.readonly_policy_arn)
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.child_sts_fullaccess)
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.child_ec2instance)
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.back_up_arn)
                self.attach_role_policy_routine(INSTANCE_ROLE_NAME,self.ec2_fullaccess_policy_arn)
                print("Role Instance updated successfully!!!")

            elif role_name == READONLY_ROLE_NAME:
                print("Role ReadOnly trying to update")
                # Append Trusted services from both Automation Account and Child Account in CCS_ReadOnly Role started
                final_assume_role_policy_document_for_readonly = self.update_assume_role_policy_for_readonly(
                    role_name)
                self.iam_childaccount_client.update_assume_role_policy(
                    RoleName=READONLY_ROLE_NAME,
                    PolicyDocument=json.dumps(
                        final_assume_role_policy_document_for_readonly))
                # Append Trusted services from both Automation Account and Child Account in CCS_ReadOnly Role ended
                self.attach_role_policy_routine(READONLY_ROLE_NAME,self.readonly_policy_arn)
                print("Role Readonly updated successfully!!!")
            elif role_name == CUSTSERVICE_ROLE_NAME:
                print("Role custservice trying to remove")
                # Remove custservice role from child account
                self.delete_role(CUSTSERVICE_ROLE_NAME)
                print("Role custservice removed successfully!!!")
            elif role_name == CUSTSERVICE_READONLY_ROLE_NAME:
                print("Role cust_readonly trying to remove")
                # Remove cust_readonly role from child account
                self.delete_role(CUSTSERVICE_READONLY_ROLE_NAME)
                print("Role cust_readonly removed successfully!!!")
            elif role_name == PLATFORM_BACK_UP:
                print("Role backup trying to update")
                self.iam_childaccount_client.update_assume_role_policy(RoleName=PLATFORM_BACK_UP,
                                                                       PolicyDocument=
                                                                       json.dumps(
                                                                           self.assume_role_policy_back_up))
                self.attach_role_policy_routine(PLATFORM_BACK_UP,self.back_up_arn)
                self.attach_role_policy_routine(PLATFORM_BACK_UP,self.child_iam_passrole_policy_arn)
                self.attach_role_policy_routine(PLATFORM_BACK_UP,self.back_up_servicerole_arn)
                self.attach_role_policy_routine(PLATFORM_BACK_UP,self.restore_servicerole_arn)
                self.attach_role_policy_routine(PLATFORM_BACK_UP,self.sns_full_access)
                print("Platform back up Role updated successfully!!!")
            elif role_name == PLATFORM_ITOM_ROLE:
                print("Role ITOM trying to update")
                self.iam_childaccount_client.update_assume_role_policy(
                    RoleName=PLATFORM_ITOM_ROLE,
                    PolicyDocument=json.dumps(
                        self.assume_role_policy_itom_readonly))
                self.attach_role_policy_routine(PLATFORM_ITOM_ROLE,self.child_itom_policy_arn)
                print("Platform ITOM Role updated successfully!!!")
            elif role_name == IOT_SHELL_CDF_EXECUTION_ROLE:
                if self.IsIOTAccount == 'Yes':
                    print("Role IOT CDF role trying to update")
                    self.iam_childaccount_client.update_assume_role_policy(
                        RoleName=IOT_SHELL_CDF_EXECUTION_ROLE,
                        PolicyDocument=json.dumps(
                            self.assume_role_policy_iot_cdf))
                    self.attach_role_policy_routine(IOT_SHELL_CDF_EXECUTION_ROLE,self.child_iot_cdf_policy_arn)
                    print("Business CDF Execution Role updated successfully!!!")
            elif role_name == PLATFORM_ListEC2ForFNM_ROLE:
                if self.AccountType == 'private' or self.AccountType == 'hybrid':
                    print("Role ListEC2ForFNM role trying to update")
                    self.iam_childaccount_client.update_assume_role_policy(
                        RoleName=PLATFORM_ListEC2ForFNM_ROLE,
                        PolicyDocument=json.dumps(
                            self.assume_role_policy_FlexeraBeacon_pvt))
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.child_ListEC2ForFNMSpvt_policy_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.child_ec2instance)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.child_iam_passrole_policy_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.child_sts_fullaccess)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.readonly_policy_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.cloudwatch_plicy_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.ssm_managed_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.ssm_managed_arn_directory_Service)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.back_up_arn)
                    print("Business ListEC2ForFNM Execution Role created successfully!!!")
                else:
                    self.iam_childaccount_client.update_assume_role_policy(
                        RoleName=PLATFORM_ListEC2ForFNM_ROLE,
                        PolicyDocument=json.dumps(
                            self.assume_role_policy_FlexeraBeacon_pub))
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.child_ListEC2ForFNMSpub_policy_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.child_ec2instance)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.child_iam_passrole_policy_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.child_sts_fullaccess)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.readonly_policy_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.cloudwatch_plicy_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.ssm_managed_arn)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.ssm_managed_arn_directory_Service)
                    self.attach_role_policy_routine(PLATFORM_ListEC2ForFNM_ROLE,self.back_up_arn)
                    print("Business ListEC2ForFNM Execution Role created successfully!!!")
            elif role_name == PLATFORM_SNOW_SGC_ROLE:
                print("Role SNOW_SGC trying to update")
                self.iam_childaccount_client.update_assume_role_policy(
                    RoleName=PLATFORM_SNOW_SGC_ROLE,
                    PolicyDocument=json.dumps(
                        self.assume_role_policy_SNOW_SGC))
                self.attach_role_policy_routine(PLATFORM_SNOW_SGC_ROLE,self.child_snow_sgc_policy_arn)
                print("SNOW_SGC Role updated successfully!!!")
            role_creation_update_status = True
        except Exception as e:
            print("exception",str(e))
            role_creation_update_status = False
        return role_creation_update_status

    """ PBI-213216 - Enforcing CIS v1.2 password standards
    Author: Shanmukha <shanmukhaswamy.p@shell.com"""
    def set_password_policy(self):
        is_policy_set = 'FAILED'
        try:
            #updating password policy
            response = self.iam_childaccount_client.update_account_password_policy(
                MinimumPasswordLength=14,
                RequireSymbols=True,
                RequireNumbers=True,
                RequireUppercaseCharacters=True,
                RequireLowercaseCharacters=True,
                AllowUsersToChangePassword=True,
                MaxPasswordAge=90,
                PasswordReusePrevention=6,
                HardExpiry=False
            )
            is_policy_set = 'SUCCESS'
            LOGGER.info("The password policy is updated")
        except Exception as e:
            print("exception",str(e))
            role_creation_update_status = False
        return is_policy_set


    """Verify if a role is created before performing create or update"""
    def verify_role(self, role_name):
        print("Inside Verify Role")
        role_creation_update_status = False
        try:
            roles = self.list_iam_roles()
            if role_name not in roles:
                role_creation_update_status = self.create_role(role_name)
            else:
                role_creation_update_status = self.update_role(role_name)
        except Exception as e:
            print("exception",str(e))
            role_creation_update_status = False
        return  role_creation_update_status
        
        
    """Creation of custom role for Databricks account and creation S3 with custom name"""
    def databricks_resources(self):
        print("Inside Databricks Role")
        self.s3_childaccount_client = self.child_assume_role_session.client('s3')
        databricks_resources_status = False
        try:
            if self.IsDatabricksAccount == 'Yes':
                roles = self.list_iam_roles()
                for self.Databricks_role in self.databricks_role_name:
                    if self.Databricks_role not in roles:
                        """Creation of assume role policy"""
                        assume_role_policy_document = {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Action": "sts:AssumeRole",
                                    "Effect": "Allow",
                                    "Principal": {
                                        "AWS": [
                                            "arn:aws:iam::177707710168:role/aws-dpas-prd-oidc-trusted-role"
                                        ]
                                    }
                                }
                            ]
                        }
            
                        """Creating Databricks Role"""
                        print("Creating Databricks custom role")
                        response = self.iam_childaccount_client.create_role(
                            RoleName=self.Databricks_role,
                            AssumeRolePolicyDocument=json.dumps(assume_role_policy_document)
                        )
                        print(f"Role created: {response['Role']['Arn']}")
                        
            
                        """Creating Inline policy for Databricks role"""
                        inline_policy_document = {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Action": [
                                        "sts:DecodeAuthorizationMessage",
                                        "ec2:DescribeVpcs",
                                        "ec2:DescribeVpcAttribute",
                                        "ec2:DescribeSubnets",
                                        "ec2:DescribeSecurityGroups",
                                        "ec2:DescribeSecurityGroupRules",
                                        "ec2:DescribeRouteTables",
                                        "ec2:DescribeNetworkInterfaces",
                                        "ec2:DescribeImages"
                                    ],
                                    "Resource": [
                                        "*"
                                    ],
                                    "Effect": "Allow",
                                    "Sid": "NonResourceBasedPermissions"
                                },
                                {
                                    "Action": [
                                        "*"
                                    ],
                                    "Resource": [
                                        "arn:aws:iam::"+ self.account_number +":role/*"+ self.Databricks_projectID +"-"+ self.account_number +"-*-"+ self.DatabricksEnvironment +"-*",
                                        "arn:aws:iam::"+ self.account_number +":policy/*"+ self.Databricks_projectID +"-"+ self.account_number +"-*-"+ self.DatabricksEnvironment +"-*",
                                        "arn:aws:s3:::*"+ self.Databricks_projectID +"-"+ self.account_number +"-*-"+ self.DatabricksEnvironment +"-*"
                                    ],
                                    "Effect": "Allow",
                                    "Sid": "InstancePoolsSupport"
                                }
                            ]
                        }
            
                        # Put the inline policy to the role
                        response = self.iam_childaccount_client.put_role_policy(
                            RoleName=self.Databricks_role,
                            PolicyName=self.Databricks_policy_name,
                            PolicyDocument=json.dumps(inline_policy_document)
                        )
                        print(f"Inline policy attached: {self.Databricks_policy_name}")
                        
                        if self.DatabricksVolumeRequired == 'Yes':
                            volume_inline_ploicy = {
                                "Version": "2012-10-17",
                                    "Statement": [
                                        {
                                            "Action": [
                                                "*"
                                            ],
                                            "Resource": [
                                                "arn:aws:s3:::"+ self.Databricks_projectID + "-" + self.account_number + "-" + self.DatabricksS3Region + "-" + self.DatabricksEnvironment + "-volume-" +"/*"
                                            ],
                                            "Effect": "Allow",
                                            "Sid": "S3BucketPermissionsVolume"
                                        },
                                        {
                                            "Action": [
                                                "s3:ListBucket"
                                            ],
                                            "Resource": "arn:aws:s3:::*",
                                            "Effect": "Allow",
                                            "Sid": "S3ListBucketPermissions"
                                        }
                                    ]
                                }
                                
                        response = self.iam_childaccount_client.put_role_policy(
                            RoleName=self.Databricks_role,
                            PolicyName=self.Databricks_volume_policy_name,
                            PolicyDocument=json.dumps(volume_inline_ploicy)
                        )
                        print(f"Inline volume policy attached: {self.Databricks_policy_name}")
                    else:
                        print("Databricks Role "+ self.Databricks_role +"is already present hence skipping")
                        
                        
                    if self.DatabricksVolumeRequired == "Yes" and self.RequestType == 'Create':
                        try:
                            if self.DatabricksS3Region == 'us-east-1':
                                response = self.s3_childaccount_client.create_bucket(
                                Bucket=self.Databricks_s3_name)
                            else:
                                response = self.s3_childaccount_client.create_bucket(
                                Bucket=self.Databricks_s3_name,
                                CreateBucketConfiguration={
                                    'LocationConstraint': self.DatabricksS3Region,
                                },
                            )
                        except Exception as ex:
                            print("s3 bucket name already present! Please use the unique name for s3")
                    else:
                        print("Skipping Databricks s3 bucket creation for update request")
            else:
                print("Not a Dtabricks account, hence skipping")
            databricks_resources_status = True
        except Exception as e:
            logging.error(f"Unexpected error occurred: {str(e)}")
            databricks_resources_status = False
        return databricks_resources_status

def lambda_handler(event, context):
    LOGGER.info(event)
    platform_roles = {}
    try:
        platform_service_cloudhealth_status = False
        platform_service_inflation_status = False
        platform_service_instance_status = False
        platform_service_readonly_status = False
        business_service_admin_status = False
        business_service_readonly_status = False
        platform_service_back_up_status = False
        platform_itom_role_status = False
        business_iot_cdf_execution_role_status = False
        platform_ListEC2ForFNMSRole_status = False
        SnowOrganizationAccountAccessRole_status = False
        databricks_custom_role_status = False
        account_authorization_object = AccountAuthorization(event, context)
        """Create all the Role's trust Policies. i.e. who the role is going to trust"""
        policy_document_status = account_authorization_object.role_policy_document()
        if (policy_document_status == True):
            """Create all the policies required by the roles."""
            policy_cloud_health_status,policy_inflation_status,policy_2_inflation_status,policy_iam_pass_status,policy_sts_status,platform_ec2instance_status,policy_itom_status,policy_iot_status,platform_ListEC2ForFNMSPolicypubandpvt_status,policy_SNOWSGC_status = account_authorization_object.createPolicy()
            if (policy_cloud_health_status):
                platform_service_cloudhealth_status = account_authorization_object.verify_role("platform_service_cloudhealth")
                platform_service_inflation_status = account_authorization_object.verify_role("platform_service_inflation")
                platform_service_instance_status = account_authorization_object.verify_role("platform_service_instance")
                platform_service_readonly_status = account_authorization_object.verify_role("platform_service_readonly")
                business_service_admin_status = account_authorization_object.verify_role("business_service_admin")
                business_service_readonly_status = account_authorization_object.verify_role("business_service_readonly")
                platform_service_back_up_status = account_authorization_object.verify_role("platform_backup")
                platform_itom_role_status = account_authorization_object.verify_role("ServiceNow_ITOM_Discovery_Child_Role")
                business_iot_cdf_execution_role_status = account_authorization_object.verify_role("business_cdf-execution-role")
                platform_ListEC2ForFNMSRole_status = account_authorization_object.verify_role("Platform_Flexera_AwsConnect_Role")
                SnowOrganizationAccountAccessRole_status = account_authorization_object.verify_role("platform_SnowOrganizationAccountAccessRole")
                databricks_custom_role_status = account_authorization_object.databricks_resources()
        platform_roles['platform_service_cloudhealth_status'] = str(platform_service_cloudhealth_status)
        platform_roles['platform_service_inflation_status'] = str(platform_service_inflation_status)
        platform_roles['platform_service_instance_status'] = str(platform_service_instance_status)
        platform_roles['platform_service_readonly_status'] = str(platform_service_readonly_status)
        platform_roles['business_service_admin_status'] = str(business_service_admin_status)
        platform_roles['business_service_readonly_status'] = str(business_service_readonly_status)
        platform_roles['platform_service_back_up_status'] = str(platform_service_back_up_status)
        platform_roles['platform_itom_role_status'] = str(platform_itom_role_status)
        platform_roles['business_iot_cdf_execution_role_status'] = str(business_iot_cdf_execution_role_status)
        platform_roles['platform_ListEC2ForFNMSRole_status'] = str(platform_ListEC2ForFNMSRole_status)
        platform_roles['SnowOrganizationAccountAccessRole_status'] = str(SnowOrganizationAccountAccessRole_status)
        platform_roles['databricks_custom_role_status'] = str(databricks_custom_role_status)
        event['password_policy'] = account_authorization_object.set_password_policy()
        event.update(platform_roles)
        password_policy = account_authorization_object.set_password_policy()

    except Exception as e:
        print("Lambda Exception", str(e))
        event.update(platform_roles)

    return event
