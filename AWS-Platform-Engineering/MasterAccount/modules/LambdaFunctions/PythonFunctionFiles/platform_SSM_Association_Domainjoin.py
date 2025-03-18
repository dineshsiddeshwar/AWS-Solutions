'''
Create SSM Association for Domainjoin process
'''
import logging
import random
import json
import boto3
import time
from botocore.exceptions import ClientError
import base64

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

VALUE_DICT = {}               

class Domainjoin(object):
    """
    Class: Domainjoin
    Description: Prerequisite for Domainjoin proccess
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            self.path = '{"path": '
            self.linux_key = "tag:platform_domainjoin_linux"
            self.schedule = "rate(30 minutes)"
            self.domainjoin_schedule = "rate(60 minutes)"
            self.reason_data = ""
            session_client = boto3.Session()
            self.sts_client = session_client.client('sts')
            self.s3_client = session_client.client('s3')
            self.ssm_client = session_client.client('ssm')
            self.child_account_number = event['accountNumber']
            print("Child account number is : ", self.child_account_number)
            private_region = self.ssm_client.get_parameter(Name='Private_whitelisted_region')
            self.private_region = (private_region['Parameter']['Value']).split(',')
            print("Private Regions are ", self.private_region)
            self.child_account_arn = "arn:aws:iam::{}:role/AWSControlTowerExecution".\
                format(self.child_account_number)
            self.child_account_sessionname = "linkedAccountSession-" + \
                                             str(random.randint(1, 100000))
            child_account_role_creds = self.sts_client.assume_role\
                (RoleArn=self.child_account_arn, RoleSessionName=self.child_account_sessionname)
            child_credentials = child_account_role_creds.get('Credentials')
            child_access_keyid = child_credentials.get('AccessKeyId')
            child_secret_access_key = child_credentials.get('SecretAccessKey')
            child_session_token = child_credentials.get('SessionToken')
            self.child_assume_role_session = boto3.Session(child_access_keyid, child_secret_access_key,
                                                           child_session_token)
            self.association_id = ""

            ##Shared service role assume.
            shared_account_number = self.ssm_client.get_parameter(Name='shared_services_account_id')['Parameter']['Value']
            print("Platform Shared account number:", shared_account_number)
            secondary_rolearn = "arn:aws:iam::{}:role/AWSControlTowerExecution".format(shared_account_number)
            secondary_session_name = "SecondarySession-" + str(random.randint(1, 100000))
            secondaryRoleCreds = self.sts_client.assume_role(RoleArn=secondary_rolearn,
                                                        RoleSessionName=secondary_session_name)
            shared_credentials = secondaryRoleCreds.get('Credentials')
            self.ss_assumeRoleSession = boto3.session.Session(shared_credentials.get('AccessKeyId'),
                                                            shared_credentials.get('SecretAccessKey'),
                                                            shared_credentials.get('SessionToken'))
           ##audit account role assume.
            self.audit_account_number = self.ssm_client.get_parameter(Name='audit_account')['Parameter']['Value']
            print("Platform audit account number:", self.audit_account_number)
            audit_rolearn = "arn:aws:iam::{}:role/AWSControlTowerExecution".format(self.audit_account_number)
            audit_session_name = "SecondarySession-" + str(random.randint(1, 100000))
            auditRoleCreds = self.sts_client.assume_role(RoleArn=audit_rolearn,
                                                        RoleSessionName=audit_session_name)
            audit_credentials = auditRoleCreds.get('Credentials')
            self.audit_assumeRoleSession = boto3.session.Session(audit_credentials.get('AccessKeyId'),
                                                            audit_credentials.get('SecretAccessKey'),
                                                            audit_credentials.get('SessionToken'))
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)               

    def update_s3_bucket_policy(self):
        '''
        Update the S3 bucket policy to allow any Instance Role of the child account access
        to the script
        '''
        principal_str = "arn:aws:iam::{}:role/*".format(self.child_account_number)
        try:
            response = self.ssm_client.get_parameters(
                Names=["agent_bucket"],
                WithDecryption=True)
            for values in response['Parameters']:
                if values['Name'] == 'agent_bucket':
                    bucket_name = values['Value']
                    print(bucket_name)
            bucket_policy = json.loads(self.s3_client.get_bucket_policy(Bucket=bucket_name)['Policy'])
            print(bucket_policy)
            print(type(bucket_policy))
            principal_list = bucket_policy['Statement'][0]['Condition']['ArnLike']['aws:PrincipalArn']
            print(principal_list)
            print(type(principal_list))
            print(type(principal_str))
            if principal_str in principal_list:
                print('Childaccount roles already updated in s3 bucket policy')
                VALUE_DICT['update_s3_bucket_policy'] = "PASSED"
            else:
                if type(principal_list) == list:
                    principal_list.append(principal_str)
                else:
                    principal_list = [principal_list]
                    principal_list.append(principal_str)
                print(principal_list)
                bucket_policy['Statement'][0]['Condition']['ArnLike']['aws:PrincipalArn'] = principal_list
                print(bucket_policy)
                response = self.s3_client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(bucket_policy))
                print(response)
                print("Bucket policy insertion response {}".format(response))
                print("Bucket policy inserted successfully!!!")
                VALUE_DICT['update_s3_bucket_policy'] = "PASSED"
        except Exception as exception:
            print("Exception occurred while updating bucket policy {}".format(str(exception)))

    def update_dbcontrols_s3_bucket_policy(self):
        '''
        Update the S3 bucket policy to allow any Instance Role of the child account access
        to the script
        '''
        s3_auditaccount_client = self.audit_assumeRoleSession.client('s3')
        principal_str = "arn:aws:iam::{}:role/*".format(self.child_account_number)
        try:
            response = self.ssm_client.get_parameters(
                Names=["ScoreCardBucketName"],
                WithDecryption=True)
            for values in response['Parameters']:
                if values['Name'] == 'ScoreCardBucketName':
                    bucket_name = values['Value']
                    print(bucket_name)
            db_bucket_policy = {
                "Version": "2008-10-17",
                "Statement": [
                    {
                        "Sid": "BucketPolicyDoc",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": [
                            "s3:List*",
                            "s3:Get*",
                            "s3:Put*"
                        ],
                        "Resource": [
                            'arn:aws:s3:::'+bucket_name,
                            'arn:aws:s3:::'+bucket_name+'/*'
                        ],
                        "Condition": {
                            "ArnLike": {
                                "aws:PrincipalArn": [
                                    f'arn:aws:iam::{self.audit_account_number}:role/*'
                                ]
                            }
                        }
                    }
                ]
            }   
            try:
                db_bucket_policy = json.loads(s3_auditaccount_client.get_bucket_policy(Bucket=bucket_name)['Policy'])
            except:
                s3_auditaccount_client.put_bucket_policy(Bucket=bucket_name,Policy=json.dumps(db_bucket_policy))
                print(db_bucket_policy)
            bucket_policy = json.loads(s3_auditaccount_client.get_bucket_policy(Bucket=bucket_name)['Policy'])
            print(bucket_policy)                
            print(type(bucket_policy))
            principal_list = bucket_policy['Statement'][0]['Condition']['ArnLike']['aws:PrincipalArn']
            print(principal_list)
            print(type(principal_list))
            print(type(principal_str))
            if principal_str in principal_list:
                print('Childaccount roles already updated in s3 bucket policy')
                VALUE_DICT['update_dbcontrols_s3_bucket_policy'] = "PASSED"
            else:
                if type(principal_list) == list:
                    principal_list.append(principal_str)
                else:
                    principal_list = [principal_list]
                    principal_list.append(principal_str)
                print(principal_list)
                bucket_policy['Statement'][0]['Condition']['ArnLike']['aws:PrincipalArn'] = principal_list
                print(bucket_policy)
                response = s3_auditaccount_client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(bucket_policy))
                print(response)
                print("Bucket policy insertion response {}".format(response))
                print("Bucket policy inserted successfully!!!")
                VALUE_DICT['update_dbcontrols_s3_bucket_policy'] = "PASSED"
        except Exception as exception:
            print("Exception occurred while updating bucket policy {}".format(str(exception)))

    def create_association_linuxprerequisite(self):
        '''
        Create the SSM Association in the child account to Run remote script from S3 for linux domain join prerequisite steps
        '''
        try:
            response = self.ssm_client.get_parameters(
                Names=["domainjoin_linuxpreURL", "execution_timeout",
                       "domainjoin_linuxpath", "domainjoin_linux_prefilename"],
                WithDecryption=True)
            for values in response['Parameters']:
                if values['Name'] == 'domainjoin_linuxpath':
                    path = values['Value']
                elif values['Name'] == 'execution_timeout':
                    execution_time = values['Value']
                elif values['Name'] == 'domainjoin_linuxpreURL':
                    script_path = values['Value']
                elif values['Name'] == 'domainjoin_linux_prefilename':
                    file_name = values['Value']
            source_info = ['{"path": ' + script_path + '}']
            source_type = ['S3']
            command_line = [file_name]
            working_directory = [path]
            execution_timeout = [execution_time]
            for region in self.private_region:
                self.ssm_childaccount_client = self.child_assume_role_session.client('ssm',
                                                                                     region_name=region)
                if (not self.verify_association(self.ssm_childaccount_client, "platform-Domainjoinpre-Linux")):
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
                                'Key': self.linux_key,
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.schedule,
                        AssociationName='platform-Domainjoinpre-Linux'
                    )
                    print("SSM Association for Linux Domainjoin prerequisites created successfully!!!")
                    VALUE_DICT['create_association_linuxprerequisite'] = "PASSED"
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
                                'Key': self.linux_key,
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.schedule,
                        AssociationName='platform-Domainjoinpre-Linux'
                    )
                    print("SSM Association for Linux Domainjoin prerequisites updated successfully!!!")
                    VALUE_DICT['create_association_linuxprerequisite'] = "PASSED"
        except Exception as exception:
            print("Exception occurred while creating Linux Domainjoin prerequisites SSM Association {}".format(
                str(exception)))

    def delete_association_linuxprerequisite(self):
        '''
        Delete the SSM Association in the child account as it is replaced by SSSD based domain join script
        '''
        try:
            for region in self.private_region:
                self.ssm_childaccount_client = self.child_assume_role_session.client('ssm',
                                                                                     region_name=region)
                if (self.verify_association(self.ssm_childaccount_client, "platform-Domainjoinpre-Linux")):
                    response = self.ssm_childaccount_client.delete_association(
                        Name="AWS-RunRemoteScript",
                        AssociationId=self.association_id
                    )
                    print("SSM Association for Linux Domainjoin prerequisites deleted successfully!!!")
                else:
                    print("SSM Association for Linux Domainjoin prerequisites not found hence quitting!!!")
        except Exception as exception:
            print("Exception occurred while deleting Linux Domainjoin prerequisites SSM Association {}".format(str(exception)))

    def create_association_linuxadjoin(self):
        '''
        Create the SSM Association in the child account to Run remote script from S3 for linux main domain join steps
        '''
        try:
            response = self.ssm_client.get_parameters(
                Names=["domainjoin_linuxmainURL", "execution_timeout",
                       "domainjoin_linuxpath", "domainjoin_linux_mainfilename"],
                WithDecryption=True)
            for values in response['Parameters']:
                if values['Name'] == 'domainjoin_linuxpath':
                    path = values['Value']
                elif values['Name'] == 'execution_timeout':
                    execution_time = values['Value']
                elif values['Name'] == 'domainjoin_linuxmainURL':
                    script_path = values['Value']
                elif values['Name'] == 'domainjoin_linux_mainfilename':
                    file_name = values['Value']
            source_info = [self.path + script_path + '}']
            source_type = ['S3']
            command_line = [file_name]
            working_directory = [path]
            execution_timeout = [execution_time]
            for region in self.private_region:
                self.ssm_childaccount_client = self.child_assume_role_session.client('ssm',
                                                                                     region_name=region)
                if (not self.verify_association(self.ssm_childaccount_client, "platform-Domainjoinmain-Linux")):
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
                                'Key': self.linux_key,
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.domainjoin_schedule,
                        AssociationName='platform-Domainjoinmain-Linux'
                    )
                    print("SSM Association for Linux Domainjoin main created successfully!!!")
                    VALUE_DICT['create_association_linuxadjoin'] = "PASSED"
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
                                'Key': self.linux_key,
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.domainjoin_schedule,
                        AssociationName='platform-Domainjoinmain-Linux'
                    )
                    print("SSM Association for Linux Domainjoin main updated successfully!!!")
                    VALUE_DICT['create_association_linuxadjoin'] = "PASSED"
        except Exception as exception:
            print("Exception occurred while creating Linux domainjoin main SSM Association {}".format(str(exception)))

    def file_path(self, region):
        if region == "us-east-1":
            domainjoin_windows_url = "domainjoin_windowsURL_us"
            return domainjoin_windows_url
        elif region == "eu-west-1":
            domainjoin_windows_url = "domainjoin_windowsURL_eu"
            return domainjoin_windows_url
        elif region == "ap-southeast-1":
            domainjoin_windows_url = "domainjoin_windowsURL_sg"
            return domainjoin_windows_url
        
    def create_association_winadjoin(self):
        '''
        Create the SSM Association in the child account to Run remote script from S3 for windows domain join steps
        '''
        try:
            for region in self.private_region:
                domainjoin_windows_url = self.file_path(region)
                print(domainjoin_windows_url)

                response = self.ssm_client.get_parameters(
                    Names=[domainjoin_windows_url, "execution_timeout",
                           "domainjoin_windows_path", "domainjoin_windows_filename"],
                    WithDecryption=True)
                for values in response['Parameters']:
                    if values['Name'] == 'domainjoin_windows_path':
                        path = values['Value']
                    elif values['Name'] == 'execution_timeout':
                        execution_time = values['Value']
                    elif values['Name'] == domainjoin_windows_url:
                        script_path = values['Value']
                    elif values['Name'] == 'domainjoin_windows_filename':
                        file_name = values['Value']
                source_info = [self.path + script_path + '}']
                source_type = ['S3']
                command_line = [file_name]
                working_directory = [path]
                execution_timeout = [execution_time]
                self.ssm_childaccount_client = self.child_assume_role_session.client('ssm',
                                                                                     region_name=region)
                if (not self.verify_association(self.ssm_childaccount_client, "platform-Domainjoinmain-Windows")):
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
                                'Key': "tag:platform_domainjoin_windows",
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.schedule,
                        AssociationName='platform-Domainjoinmain-Windows'
                    )
                    print("SSM Association for Windows Domainjoin created successfully!!!")
                    VALUE_DICT['create_association_winadjoin'] = "PASSED"
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
                                'Key': "tag:platform_domainjoin_windows",
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.schedule,
                        AssociationName='platform-Domainjoinmain-Windows'
                    )
                    print("SSM Association for Windows Domainjoin updated successfully!!!")
                    VALUE_DICT['create_association_winadjoin'] = "PASSED"
        except Exception as exception:
            print("Exception occurred while creating Windows SSM Association {}".format(str(exception)))

    def share_sharedaccount_directory(self):
            try:
                SharedDirectoryList = []
                for region in self.private_region:
                    directoryId = "directoryId" + region.replace("-", "")
                    response = self.ssm_client.get_parameter(Name=directoryId)
                    directoryIdValue = response['Parameter']['Value']
                    print("Directory ID value is: ", directoryIdValue)
                    self.ca_ds_client = self.child_assume_role_session.client('ds', region_name=region)
                    dd_response = self.ca_ds_client.describe_directories()
                    flag = 0
                    region_directories = {}
                    if dd_response['ResponseMetadata']['HTTPStatusCode'] == 200 and len(dd_response['DirectoryDescriptions']) != 0 :
                         print("Serching Shared account directory if shared in child account")
                         for directory in dd_response['DirectoryDescriptions']:
                             if directory['OwnerDirectoryDescription']['DirectoryId'] == directoryIdValue:
                                flag +=1
                                region_directories.update({"region" : region, "shareddirectoryId" : directory['DirectoryId'] })
                                break

                    if flag == 0:
                        print("Domain service does not exist, create the Directory share now..")
                        self.ss_ds_client = self.ss_assumeRoleSession.client('ds', region_name=region)
                        sd_response = self.ss_ds_client.share_directory(
                                                                DirectoryId=directoryIdValue,
                                                                ShareNotes='RESPC Domain Join',
                                                                ShareTarget={
                                                                    'Id': self.child_account_number,
                                                                    'Type': 'ACCOUNT'
                                                                },
                                                                ShareMethod='HANDSHAKE' 
                                                            )
                        if sd_response['ResponseMetadata']['HTTPStatusCode'] == 200 :
                            print("Successfully shared hence now accepting it from child account...")
                            time.sleep(5)
                            ad_response = self.ca_ds_client.accept_shared_directory(SharedDirectoryId=sd_response['SharedDirectoryId'])
                            if ad_response['ResponseMetadata']['HTTPStatusCode'] == 200:
                                print("Successfully Shared AD is accepted in child account..")
                                region_directories.update({"region" : region, "shareddirectoryId" : ad_response['SharedDirectory']['SharedDirectoryId'] })
                    else:
                        print("Shared account AD is shared for region: ", region)
                    SharedDirectoryList.append(region_directories)
                return SharedDirectoryList
            except Exception as ex:
                print("An Exception occured while sharing the managed AD an error %s", str(ex))

    def create_association_aws_managed_ad_domainjoin(self, SharedDirectoryLists, OUName):
        '''
        Create the SSM Association for AWS Managed AD Domain join of RESPC EC2 and RDS EC2 instances.
        '''
        try:
            for region in self.private_region:
                directoryId = "directoryId" + region.replace("-", "")
                directoryName = "directoryName" + region.replace("-", "")
                dnsIpAddresses = "dnsIpAddresses" + region.replace("-", "")
                response = self.ssm_client.get_parameters( Names=[directoryId, directoryName, dnsIpAddresses], WithDecryption=True)
                for values in response['Parameters']:
                    if values['Name'] == directoryId :
                        directoryIdValue = values['Value']
                    elif values['Name'] == directoryName :
                        directoryNameValue = values['Value']
                    elif values['Name'] == dnsIpAddresses :
                        dnsIpAddressesValue = values['Value'].split(",")
                shared_directory_item = next(iter(item for item in SharedDirectoryLists if item['region'] == region), None)
                print("directory name is : ", directoryNameValue)
                print("Parent directory Id is : ", directoryIdValue)
                SplitedDirectoryNames = directoryNameValue.split('.')
                print("Splitted Directory names", SplitedDirectoryNames)
                finalStringLine = ''
                for SplitedDirectoryName in SplitedDirectoryNames:
                    finalString = "DC="+SplitedDirectoryName
                    finalStringLine = finalStringLine+","+finalString
                print("shared dirctory region of iteration", shared_directory_item)
                # example eu - OU - "OU=RESPC-SES,OU=RESPC,OU=rds-eu1-da2uat,DC=rds-eu1-da2uat,DC=aws,DC=shell-cloud,DC=com"
                # example us - OU - "OU=RESPC-SEUK,OU=RESPC,OU=rds-eu1-da2uat,DC=rds-eu1-da2uat,DC=aws,DC=shell-cloud,DC=com"
                FullOUName = "OU="+OUName+",OU=RESPC"+",OU="+SplitedDirectoryNames[0] + finalStringLine
                print("Shared directory Id : ", shared_directory_item['shareddirectoryId'])
                print("full OU name framed is : ", FullOUName)
                print("dns Ip Addresses Value : ", dnsIpAddressesValue)
                self.ssm_childaccount_client = self.child_assume_role_session.client('ssm', region_name=region)
                if (not self.verify_association(self.ssm_childaccount_client, "platform-AWS-managed-AD-domainjoin")):
                    response = self.ssm_childaccount_client.create_association(
                        Name="AWS-JoinDirectoryServiceDomain",
                        Parameters={
                            'directoryId': [shared_directory_item['shareddirectoryId']],
                            'directoryName': [directoryNameValue],
                            'directoryOU': [FullOUName],
                            'dnsIpAddresses': dnsIpAddressesValue
                        },
                        Targets=[
                            {
                                'Key': "tag:platform_aws_managed_ad_domainjoin",
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.schedule,
                        AssociationName='platform-AWS-managed-AD-domainjoin'
                    )
                    print("SSM Association for platform AWS Managed AD DomainJoin created successfully!!!")
                    response_sctmgr = self.create_secret(shared_directory_item['shareddirectoryId'], region)
                    if response_sctmgr['ResponseMetadata']['HTTPStatusCode'] == 200 :
                        print("Successfully create the sct manager resources...")
                    else:
                        print("Could not create the sct manager resources...!!!")
                    VALUE_DICT['create_association_awsmanagedadjoin'] = "PASSED"
                else:
                    response = self.ssm_childaccount_client.update_association(
                        AssociationId=self.association_id,
                        Name="AWS-JoinDirectoryServiceDomain",
                        Parameters={
                            'directoryId': [shared_directory_item['shareddirectoryId']],
                            'directoryName': [directoryNameValue],
                            'directoryOU': [FullOUName],
                            'dnsIpAddresses': dnsIpAddressesValue
                        },
                        Targets=[
                            {
                                'Key': "tag:platform_aws_managed_ad_domainjoin",
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.schedule,
                        AssociationName='platform-AWS-managed-AD-domainjoin'
                    )
                    print("SSM Association for platform AWS Managed AD DomainJoin updated successfully!!!")
                    response_sctmgr = self.update_secret(shared_directory_item['shareddirectoryId'], region)
                    if response_sctmgr['ResponseMetadata']['HTTPStatusCode'] == 200 :
                        print("Successfully updated the sct manager resources...")
                    else:
                        print("Could not update the sct manager resources...!!!")
                    VALUE_DICT['create_association_awsmanagedadjoin'] = "PASSED"
        except Exception as exception:
            print("Exception occurred while creating platform AWS Managed AD DomainJoin SSM Association {}".format(str(exception)))

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

    def get_secret(self, region):
        secret_name = "RESPCManagedADCreds"
        try:
            secretsmanager_client = boto3.client('secretsmanager', region_name=region)
            get_secret_value_response = secretsmanager_client.get_secret_value( SecretId=secret_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise e
        else:
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                return secret
            else:
                decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
                return decoded_binary_secret

    def create_secret(self, id, region):
            try:
                scts = json.loads(self.get_secret(region))
                child_secretsmanager_client = self.child_assume_role_session.client('secretsmanager', region_name=region)
                SectStrg = json.dumps({"awsSeamlessDomainUsername":scts['awsSeamlessDomainUsername'], "awsSeamlessDomainPassword":scts['awsSeamlessDomainPassword']})
                Name = "aws/directory-services/"+ id +"/seamless-domain-join"
                response = child_secretsmanager_client.create_secret(
                    Description='AWS Managed AD Linux Domain Join',
                    Name=Name,
                    SecretString= str(SectStrg),
                    Tags=[{
                        'Key': 'platform_donotdelete',
                        'Value': 'yes'
                        }
                        ]
                )
                print("Created secret %s.", Name)
            except ClientError:
                print("Couldn't get secret %s.", Name)
                return False
            else:
                return response

    def update_secret(self, id,region):
            try:
                scts = json.loads(self.get_secret(region))
                child_secretsmanager_client = self.child_assume_role_session.client('secretsmanager', region_name=region)
                SectStrg = json.dumps({"awsSeamlessDomainUsername":scts['awsSeamlessDomainUsername'], "awsSeamlessDomainPassword":scts['awsSeamlessDomainPassword']})
                Name = "aws/directory-services/"+ id +"/seamless-domain-join"
                response = child_secretsmanager_client.update_secret(
                    SecretId=Name,
                    SecretString= str(SectStrg)
                )
                print("updated secret %s.", Name)
            except ClientError:
                print("Couldn't update secret %s.", Name)
                return False
            else:
                return response

def lambda_handler(event, context):
    '''
    Main lambda handler takes event as dictionary
    and context as an object
    '''
    try:
        result_values = {}
        result_values.update(event)
        print("Event {}".format(event))
        domainjoin_obj = Domainjoin(event, context)
        #domainjoin_obj.update_s3_bucket_policy()
        #domainjoin_obj.update_dbcontrols_s3_bucket_policy()
        account_type = event['ResourceProperties']['AccountType']
        is_RESPCAccount = event['ResourceProperties']['IsRESPCAccount']
        if 'private' in account_type:
            print('account is private')
            domainjoin_obj.create_association_winadjoin()
            domainjoin_obj.delete_association_linuxprerequisite()
            ##domainjoin_obj.create_association_linuxprerequisite()
            domainjoin_obj.create_association_linuxadjoin()
            result_values.update(VALUE_DICT)                                            
            return result_values
        elif 'hybrid' in account_type:
            print('account is hybrid')
            if 'Yes' in is_RESPCAccount:
                print("Its RESPC type account, hence creating respective domain join resources")
                print("calling share directory...")
                SharedDirectoryLists = domainjoin_obj.share_sharedaccount_directory()
                if len(SharedDirectoryLists) > 0:
                    print("Shared account directory is shared..")
                    print("Creating the SSM association..")
                    print("OU name selected is : ", event['ResourceProperties']['HybridRESPCAccountDomainJoinOUName'])
                    domainjoin_obj.create_association_aws_managed_ad_domainjoin(SharedDirectoryLists,event['ResourceProperties']['HybridRESPCAccountDomainJoinOUName'])
                    print("Creation of SSM association completed....")
                else:
                    print("Share directory in child account did not retrun list of shared AD..")
            else: 
                print("Its not RESPC type account hence going ahead for normal domain join resources")
                domainjoin_obj.create_association_winadjoin()
                domainjoin_obj.delete_association_linuxprerequisite()
                ##domainjoin_obj.create_association_linuxprerequisite()
                domainjoin_obj.create_association_linuxadjoin()
            result_values.update(VALUE_DICT)                                            
            return result_values
        elif 'Managed_Services' in account_type:
            print('account is BeAgile')
            domainjoin_obj.create_association_winadjoin()
            domainjoin_obj.delete_association_linuxprerequisite()
            ##domainjoin_obj.create_association_linuxprerequisite()
            domainjoin_obj.create_association_linuxadjoin()
            result_values.update(VALUE_DICT)
            return result_values
        else:
            print('SSM domain join association will not happen for public environment')
            return result_values
    except Exception as exception:
        print("Exception in Lambda Handler", exception)
