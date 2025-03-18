"""
This module is used to Provision VPC in the child account
"""

import random
import boto3
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

child_account_role_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))


class CreateResource(object):
    """
    # Class: CreateResource
    # Description: Creates Resources needed for Tagging Automation
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        self.res_dict = {}
        try:
            session_client = boto3.session.Session()
            self.ssm_client = session_client.client('ssm')
            #acnts_table_response = self.ssm_client.get_parameter(Name="accountDetailTableName")
            #self.table_name = acnts_table_response['Parameter']['Value']
            self.table_name = event['SSMParametres']['accountDetailTableName']
            print("account details table name", self.table_name)
            # get relevant input params from event
            self.ResourceProperties = self.event['ResourceProperties']
            self.account_id = event['accountNumber']
            self.dd_client = boto3.client('dynamodb', region_name="us-east-1")
            self.platform_stc = ""
            self.platform_lob = ""
            self.platform_apexid = ""
            self.platform_requestNo = ""
            self.platform_custodian = ""
            self.platform_DL = ""
            self.platform_account_type = ""
            self.platform_whitelisted_regions = ""
            self.platform_backup = ""
            self.platform_RSPC_Account = ""

            self.account_type = event['ResourceProperties']['AccountType']
            self.platfrom_SOX = event['ResourceProperties']['SOXrelevant']
            self.platform_BIA = event['ResourceProperties']['ActiveBIAid']
            self.platfrom_DataClassification = event['ResourceProperties']['DataClassification']
            self.platform_tenancy = event['ResourceProperties']['AccountTenancy']
            self.IsDatabricksAccount = event['ResourceProperties']['IsDatabricksAccount']
            if self.IsDatabricksAccount == 'Yes':
                self.DatabricksEnvironment = event['ResourceProperties']['DatabricksEnvironment'].lower()
                self.Databricks_projectID = event['ResourceProperties']['DatabricksProjectID'].lower()

            # Get relevant regions according to account type
            if 'private' in event['ResourceProperties']['AccountType']:
                print("account is private")
                self.Regions = event['SSMParametres']['whitelisted_regions_private'].split(',')
                print("Private regions", self.Regions)
            elif 'hybrid' in event['ResourceProperties']['AccountType']:
                print("account is hybrid")
                self.Regions = event['SSMParametres']['whitelisted_regions_private'].split(',')
                print("Hybrid regions", self.Regions)
            elif 'public' in event['ResourceProperties']['AccountType']:
                self.Regions = event['SSMParametres']['whitelisted_regions_public'].split(',')
                print("Public region", self.Regions)
            elif 'Managed_Services' in event['ResourceProperties']['AccountType']:
                self.Regions = event['SSMParametres']['whitelisted_regions_public'].split(',')
                print("Be Agile region", self.Regions)
            elif 'Migration' in event['ResourceProperties']['AccountType']:
                self.Regions = event['SSMParametres']['whitelisted_regions_public'].split(',')
                print("Migration accounts region", self.Regions)
            elif 'Data-Management' in event['ResourceProperties']['AccountType']:
                self.Regions = event['SSMParametres']['whitelisted_regions_public'].split(',')
                print("Data Management region", self.Regions)

            print("Creating Session and AWS Service Clients")
            session = boto3.session.Session()
            sts_client = session.client('sts')
            child_account_role_arn = "arn:aws:iam::" + self.account_id + ":role/AWSControlTowerExecution"
            child_account_role_creds = sts_client.assume_role(RoleArn=child_account_role_arn,
                                                              RoleSessionName=child_account_role_session_name)
            credentials = child_account_role_creds.get('Credentials')
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)
            print(self.assumeRoleSession)
        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))
            self.reason_data = "Missing required property %s" % exception
            self.res_dict['TagAutomation_create_reasource'] = "FAILED"
            self.res_dict['reason_data'] = self.reason_data
            self.res_dict['log_stream_name'] = self.context.log_stream_name
            raise Exception(str(exception))

    def create_ssm_parameter(self,region):
        """Create ssm parameter for tag values in child account"""
        try:
            get_response = self.dd_client.get_item(
                TableName=self.table_name,
                Key={'AccountNumber': {'S': self.account_id}},
                ConsistentRead=True
            )
            self.platform_stc = get_response['Item']['SoldToCode']['S']
            self.platform_lob = get_response['Item']['LoB']['S']
            self.platform_RSPC_Account = get_response['Item']['IsRESPCAccount']['S']
            self.platform_apexid = get_response['Item']['ApexID']['S']
            self.platform_requestNo = get_response['Item']['RequestNo']['L'][0]['S']
            self.platform_custodian = get_response['Item']['CustodianUser']['S']
            self.platform_DL = get_response['Item']['SupportDL']['S']
            self.platform_account_type = self.account_type
            self.platform_whitelisted_regions = ",".join(self.Regions)
            self.platform_backup = 'Yes'

            self.tag_dict = {
                "platform_STC": self.platform_stc,
                "platform_LOB": self.platform_lob,
                "platform_IsRESPCAccount": self.platform_RSPC_Account,
                "platform_Apexid": self.platform_apexid,
                "platform_RequestNo": self.platform_requestNo,
                "platform_Custodian": self.platform_custodian,
                "platform_DL": self.platform_DL,
                "platform_AccountType": self.platform_account_type,
                "platform_WhitelistedRegions": self.platform_whitelisted_regions,
                "platform_IsDatabricksAccount": self.IsDatabricksAccount
            }

            self.Account_tag_dist = {
                "platform_SOX": self.platfrom_SOX,
                "platform_BIA": self.platform_BIA,
                "platform_DataClassification": self.platfrom_DataClassification,
                "platform_Tenancy": self.platform_tenancy
            }

            ssm_client = self.assumeRoleSession.client('ssm',region_name = region)
            for key,value in self.tag_dict.items():
                print(key,value)
                ssm_response = ssm_client.put_parameter(
                    Name= "/Platform-Tag/"+key,
                    Description='Business details Tag values',
                    Value=str(value),
                    Type='String',
                    Overwrite=True

                )
                response = ssm_client.add_tags_to_resource(
                    ResourceType='Parameter',
                    ResourceId="/Platform-Tag/"+key,
                    Tags=[
                        {
                            'Key': 'platform_donotdelete',
                            'Value': 'yes'
                        }
                    ]
                )
                print(ssm_response)

            #Account level Tags
            for key,value in self.Account_tag_dist.items():
                print("Inside Account tagging")
                print(key,value)
                ssm_response = ssm_client.put_parameter(
                    Name= "/Platform-Tag/"+key,
                    Description='Business details Tag values',
                    Value=str(value),
                    Type='String',
                    Overwrite=True

                )
                response1 = ssm_client.add_tags_to_resource(
                    ResourceType='Parameter',
                    ResourceId="/Platform-Tag/"+key,
                    Tags=[
                        {
                            'Key': 'platform_donotdelete',
                            'Value': 'yes'
                        }
                    ]
                )
                print(ssm_response)
            ssm_response1 = ssm_client.put_parameter(
                Name= "/Platform-Backup-Tag/platform_Backup",
                Description='Business details Tag values',
                Value=self.platform_backup,
                Type='String',
                Overwrite=True

            )
            response2 = ssm_client.add_tags_to_resource(
                ResourceType='Parameter',
                ResourceId="/Platform-Backup-Tag/platform_Backup",
                Tags=[
                    {
                        'Key': 'platform_donotdelete',
                        'Value': 'yes'
                    }
                ]
            )
            print(ssm_response1)

            if self.IsDatabricksAccount == 'Yes':
                self.Databricks_tag_dist = {
                "platform_DatabricksEnvironment": self.DatabricksEnvironment,
                "platform_Databricks_projectID": self.Databricks_projectID,
                }

                ssm_client = self.assumeRoleSession.client('ssm',region_name = region)
                for key,value in self.Databricks_tag_dist.items():
                    print(key,value)
                    ssm_response = ssm_client.put_parameter(
                        Name= "/Platform-Tag/"+key,
                        Description='Databricks details Tag values',
                        Value=str(value),
                        Type='String',
                        Overwrite=True

                    )
                    response = ssm_client.add_tags_to_resource(
                        ResourceType='Parameter',
                        ResourceId="/Platform-Tag/"+key,
                        Tags=[
                            {
                                'Key': 'platform_donotdelete',
                                'Value': 'yes'
                            }
                        ]
                    )
                    print(ssm_response)

            self.res_dict['create_ssm_parameter'] = "PASSED"
            return self.res_dict
        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))
            self.reason_data = "Error in creating ssm parameter %s" % exception
            self.res_dict['TagAutomation_create_reasource'] = "FAILED"
            self.res_dict['reason_data'] = self.reason_data
            self.res_dict['log_stream_name'] = self.context.log_stream_name
            return self.res_dict

    def delete_backup_tag_ssm_parameter(self,region):
        """deleting ssm parameter for backup tag in child account if it exists"""
        try:
            ssm_client = self.assumeRoleSession.client('ssm',region_name = region)
            tag = "/Platform-Tag/platform_Backup" 
            ssm_response = ssm_client.describe_parameters(
                ParameterFilters=[
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': [
                            '/Platform-Tag/platform_Backup',
                        ]
                    },
                ]
            )
            if len(ssm_response['Parameters']) != 0:
                print("The paramaters exists..!!")
                ssm_response1 = ssm_client.delete_parameter(Name = tag)
                print(ssm_response1)
            else:
                print("The paramaters does not exists..!!")
            self.res_dict['delete_backup_tag_ssm_parameter'] = "PASSED"
            return self.res_dict
        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))
            self.reason_data = "Error in deleting ssm parameter %s" % exception
            self.res_dict['TagAutomation_create_reasource'] = "FAILED"
            self.res_dict['reason_data'] = self.reason_data
            self.res_dict['log_stream_name'] = self.context.log_stream_name
            return self.res_dict

    def config_rule(self,region):
        """put config for auto tag in child account"""
        try:
            config_client = self.assumeRoleSession.client('config',region_name = region)
            tag_dict = {
                "tag1Key": "platform_STC",
                "tag1Value": self.platform_stc,
                "tag2Key": "platform_LOB",
                "tag2Value": self.platform_lob,
                "tag3Key": "platform_Apexid",
                "tag3Value": self.platform_apexid,
                "tag4Key": "platform_RequestNo",
                "tag4Value": self.platform_requestNo,
                "tag5Key": "platform_Custodian",
                "tag5Value": self.platform_custodian,
                "tag6Key": "platform_IsRESPCAccount",
                "tag6Value": self.platform_RSPC_Account, 
            }
            input_param = json.dumps(tag_dict)
            print(input_param)
            config_response = config_client.put_config_rule(
                ConfigRule={
                    'ConfigRuleName': 'platform_Auto-Tag',
                    'Description': 'Config rule for auto-tagging the business resource',
                    'Source': {
                        'Owner': 'AWS',
                        'SourceIdentifier': 'REQUIRED_TAGS',
                    },
                    'InputParameters': input_param,
                },
                Tags=[
                    {
                        'Key': 'platform_donotdelete:',
                        'Value': 'yes'
                    }
                ]
            )
            print(config_response)
            response = config_client.start_config_rules_evaluation(
                ConfigRuleNames=[
                    'platform_Auto-Tag'
                ]
            )
            self.res_dict['config_rule'] = "PASSED"
            return self.res_dict
        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))
            self.reason_data = "Error in putting config rule %s" % exception
            self.res_dict['TagAutomation_create_reasource'] = "FAILED"
            self.res_dict['reason_data'] = self.reason_data
            self.res_dict['log_stream_name'] = self.context.log_stream_name
            return self.res_dict

    def config_rule_platform_backup_tag(self,region):
        """put config for auto tag in child account"""
        try:
            config_client = self.assumeRoleSession.client('config',region_name = region)
            tag_dict = {
                "tag1Key": "platform_Backup"
                #"tag1Value": self.platform_backup
            }
            input_param = json.dumps(tag_dict)
            print(input_param)
            config_response = config_client.put_config_rule(
                ConfigRule={
                    'ConfigRuleName': 'platform_Auto-Backup-Tag',
                    'Description': 'Config rule for auto-tagging the business resource',
                    'Source': {
                        'Owner': 'AWS',
                        'SourceIdentifier': 'REQUIRED_TAGS',
                    },
                    'InputParameters': input_param,
                },
                Tags=[
                    {
                        'Key': 'platform_donotdelete:',
                        'Value': 'yes'
                    }
                ]
            )
            print(config_response)
            self.res_dict['config_rule_platform_backup_tag'] = "PASSED"
            return self.res_dict
        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))
            self.reason_data = "Error in putting config rule %s" % exception
            self.res_dict['TagAutomation_create_reasource'] = "FAILED"
            self.res_dict['reason_data'] = self.reason_data
            self.res_dict['log_stream_name'] = self.context.log_stream_name
            return self.res_dict

def lambda_handler(event, context):
    """
    Lambda handler calls the function that creates auto tag resources
    """

    try:
        create_resource_obj = CreateResource(event, context)

        for region in create_resource_obj.Regions:
            ssm_result = create_resource_obj.create_ssm_parameter(region)
            ssm_result1 = create_resource_obj.delete_backup_tag_ssm_parameter(region)
            config_result = create_resource_obj.config_rule(region)
            config_result1 = create_resource_obj.config_rule_platform_backup_tag(region)
        event.update(create_resource_obj.res_dict)        
        event['TagAutomation_create_reasource'] = "PASSED"
        return event
    except Exception as exception:
        logger.error(str(exception))
        res_dict = {}
        res_dict['TagAutomation_create_reasource'] = "FAILED"
        event.update(res_dict)
        return event
