'''
Create SSM Association for InstallFlexera process
'''
import logging
import random
import json
import datetime
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

class InstallFlexeraAgent(object):
    """
    # Class: InstallFlexera agent
    # Description: Prerequisite for InstallFlexera agent proccess
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            self.reason_data = ""
            self.res_dict = {}
            session_client = boto3.Session()
            self.sts_client = session_client.client('sts')
            self.s3_client = session_client.client('s3')
            self.ssm_client = session_client.client('ssm')
            self.child_account_number = event['accountNumber']
            self.private_region = event['SSMParametres']['whitelisted_regions_private'].split(',')
            self.public_region =event['SSMParametres']['whitelisted_regions_public'].split(',')
            self.child_account_arn = "arn:aws:iam::{}:role/AWSControlTowerExecution". \
                format(self.child_account_number)
            self.child_account_sessionname = "linkedAccountSession-" + \
                                             str(random.randint(1, 100000))
            child_account_role_creds = self.sts_client.assume_role \
                (RoleArn=self.child_account_arn, RoleSessionName=self.child_account_sessionname)
            child_credentials = child_account_role_creds.get('Credentials')
            child_access_keyid = child_credentials.get('AccessKeyId')
            child_secret_access_key = child_credentials.get('SecretAccessKey')
            child_session_token = child_credentials.get('SessionToken')
            self.child_assume_role_session = boto3.Session(child_access_keyid, child_secret_access_key,
                                                           child_session_token)
            self.association_id = ""
            self.target_tag = "tag:platform_flexera_linux"
            self.rate_expression = "rate(240 minutes)"
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)
            raise Exception(str(exception))

    def update_s3_bucket_policy(self):
        '''
        Update the S3 bucket policy to allow any Instance Role of the child account access
        to the script
        '''
        principal_str = "arn:aws:iam::{}:role/*".format(self.child_account_number)
        try:
            bucket_name = self.event['SSMParametres']['platform_agent_bucket']
            bucket_policy = json.loads(self.s3_client.get_bucket_policy(Bucket=bucket_name)['Policy'])
            principal_list = bucket_policy['Statement'][0]['Condition']['ArnLike']['aws:PrincipalArn']
            if principal_str in principal_list:
                print('Childaccount roles already updated in s3 bucket policy')
                self.res_dict['update_s3_policy'] = "PASSED"
                return self.res_dict
            else:
                if (type(principal_list) == list):
                    principal_list.append(principal_str)
                else:
                    principal_list = [principal_list]
                    principal_list.append(principal_str)
                bucket_policy['Statement'][0]['Condition']['ArnLike']['aws:PrincipalArn'] = principal_list
                response = self.s3_client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(bucket_policy))
                print("Bucket policy inserted successfully!!!")
                self.res_dict['update_s3_policy'] = "PASSED"
                return self.res_dict
        except Exception as exception:
            print("Exception occurred while updating bucket policy {}".format(str(exception)))
            self.res_dict['update_s3_policy'] = "FAILED"
            return self.res_dict

    def create_ssm_association_public(self):
        '''
        Create the SSM Association in the child account to Run remote script from S3 for Flexera installation
        '''
        try:
            path = self.event['SSMParametres']['platform_linux_dirpath']
            execution_time = self.event['SSMParametres']['platform_execution_timeout']
            script_path = self.event['SSMParametres']['platform_pub_flexera_linuxpath']
            file_name = self.event['SSMParametres']['platform_flexera_linux_filename']
            source_info = ['{"path": ' + script_path + '}']
            source_type = ['S3']
            command_line = [file_name]
            working_directory = [path]
            execution_timeout = [execution_time]
            for region in self.public_region:
                self.ssm_childaccount_client = self.child_assume_role_session.client('ssm', region_name=region)
                if (not self.verify_association(self.ssm_childaccount_client, "platform_InstallFlexeraAgent-Linux")):
                    response = self.ssm_childaccount_client.create_association(
                        Name="AWS-RunRemoteScript",
                        Parameters={
                            'commandLine': command_line,
                            'executionTimeout': execution_timeout,
                            'sourceInfo': source_info,
                            'sourceType': source_type,
                            'workingDirectory': working_directory
                        },
                        Targets=[
                            {
                                'Key': self.target_tag,
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.rate_expression,
                        AssociationName='platform_InstallFlexeraAgent-Linux'
                    )
                    print("SSM Association created successfully!!!")
                    self.res_dict['flexera_association_creation_pub_linux'] = "PASSED"
                else:
                    response = self.ssm_childaccount_client.update_association(
                        AssociationId=self.association_id,
                        Name="AWS-RunRemoteScript",
                        Parameters={
                            'commandLine': command_line,
                            'executionTimeout': execution_timeout,
                            'sourceInfo': source_info,
                            'sourceType': source_type,
                            'workingDirectory': working_directory
                        },
                        Targets=[
                            {
                                'Key': self.target_tag,
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.rate_expression,
                        AssociationName='platform_InstallFlexeraAgent-Linux'
                    )
                    print("SSM Association is created successfully!!!")
                    self.res_dict['flexera_association_creation_pub_linux'] = "PASSED"
        except Exception as exception:
            print("Exception occurred while creating SSM Association for Flexera linux {}".format(str(exception)))
            self.res_dict['flexera_association_creation_pub_linux'] = "FAILED"
            return self.res_dict

    def file_path(self, region):
        if region == "us-east-1":
            flexera_linux_path = "platform_pvt_flexera_linuxpath_us"
            return flexera_linux_path
        elif region == "eu-west-1":
            flexera_linux_path = "platform_pvt_flexera_linuxpath_eu"
            return flexera_linux_path

    def create_ssm_association_private(self):
        '''
        Create the SSM Association in the child account to Run remote script from S3 for Flexera installation
        '''
        try:
            for region in self.private_region:
                flexera_linux_path = self.file_path(region)
                print(flexera_linux_path)
                path = self.event['SSMParametres']['platform_linux_dirpath']
                execution_time = self.event['SSMParametres']['platform_execution_timeout']
                script_path = self.event['SSMParametres'][flexera_linux_path]
                file_name = self.event['SSMParametres']['platform_flexera_linux_filename']
                source_info = ['{"path": ' + script_path + '}']
                source_type = ['S3']
                command_line = [file_name]
                working_directory = [path]
                execution_timeout = [execution_time]
                self.ssm_childaccount_client = self.child_assume_role_session.client('ssm',region_name=region)
                if (
                not self.verify_association(self.ssm_childaccount_client, "platform_InstallFlexeraAgent-Linux")):
                    response = self.ssm_childaccount_client.create_association(
                        Name="AWS-RunRemoteScript",
                        Parameters={
                            'commandLine': command_line,
                            'executionTimeout': execution_timeout,
                            'sourceInfo': source_info,
                            'sourceType': source_type,
                            'workingDirectory': working_directory
                        },
                        Targets=[
                            {
                                'Key': self.target_tag,
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.rate_expression,
                        AssociationName='platform_InstallFlexeraAgent-Linux'
                    )
                    print("SSM Association for Flexera installation for Linux has been created successfully!!!")
                    self.res_dict['flexera_association_creation_priv_linux'] = "PASSED"
                else:
                    response = self.ssm_childaccount_client.update_association(
                        AssociationId=self.association_id,
                        Name="AWS-RunRemoteScript",
                        Parameters={
                            'commandLine': command_line,
                            'executionTimeout': execution_timeout,
                            'sourceInfo': source_info,
                            'sourceType': source_type,
                            'workingDirectory': working_directory
                        },
                        Targets=[
                            {
                                'Key': self.target_tag,
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.rate_expression,
                        AssociationName='platform_InstallFlexeraAgent-Linux'
                    )
                    print("SSM Association for Flexera installation for Linux has been updated successfully!!!")
                    self.res_dict['flexera_association_creation_priv_linux'] = "PASSED"
        except Exception as exception:
            print("Exception occurred while creating SSM Association for Flexera linux {}".format(str(exception)))
            self.res_dict['flexera_association_creation_priv_linux'] = "FAILED"
            return self.res_dict

    def verify_association(self, ssm_childaccount_client, association_name):
        '''
            Verify if the associatation is already present or not
        '''
        try:
            response = ssm_childaccount_client.list_associations(
                AssociationFilterList=[
                    {
                        'key': 'AssociationName',
                        'value': association_name
                    },
                ]
            )
            print(response['Associations'].__len__())
            if (response['Associations'].__len__() > 0):
                self.association_id = response['Associations'][0]['AssociationId']
                return True
            else:
                return False
        except Exception as exception:
            print("Exception occurred while verifying SSM Association {}".format(str(exception)))
            self.res_dict['flexera_association_verification_linux'] = "FAILED"
            return self.res_dict


def lambda_handler(event, context):
    """"
    Lamda handler that calls the function to Creat SSM Association to Install Flexera Agent
    """
    try:
        result_values = {}
        result_values.update(event)
        print("Event {}".format(event))
        install_flexera_agent_object = InstallFlexeraAgent(event, context)
        #install_flexera_agent_object.update_s3_bucket_policy()
        account_type = event['ResourceProperties']['AccountType']
        if 'private' in account_type:
            print('account is private')
            install_flexera_agent_object.create_ssm_association_private()
            result_values.update(install_flexera_agent_object.res_dict)
            return result_values
        elif 'hybrid' in account_type:
            print('account is hybrid')
            install_flexera_agent_object.create_ssm_association_private()
            result_values.update(install_flexera_agent_object.res_dict)
            return result_values
        elif 'public' in account_type:
            print('its public account')
            install_flexera_agent_object.create_ssm_association_public()
            result_values.update(install_flexera_agent_object.res_dict)
        elif 'Data-Management' in account_type:
            print('its Data Management account')
            install_flexera_agent_object.create_ssm_association_public()
            result_values.update(install_flexera_agent_object.res_dict)
        elif 'Migration' in account_type:
            print('its Migration account')
            install_flexera_agent_object.create_ssm_association_public()
            result_values.update(install_flexera_agent_object.res_dict)
        else:
            print("SSM association creation failed for flexera linux or Account might be a platform account")
        return result_values
    except Exception as exception:
        print("Exception in Lambda Handler", exception)
        return event
