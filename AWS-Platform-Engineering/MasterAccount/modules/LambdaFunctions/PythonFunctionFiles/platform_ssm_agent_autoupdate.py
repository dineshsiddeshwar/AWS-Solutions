'''
Create SSM Association for SSM Agent Auto-Updated as per document
https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-state-cli.html
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


class SSMAgentAutoUpdate(object):
    """
    # Create SSM Association for SSM Agent Auto-Updated as per document
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
            self.ssm_client = session_client.client('ssm')
            self.child_account_number = event['accountNumber']
            print(self.child_account_number)
            self.private_region = event['SSMParametres']['whitelisted_regions_private'].split(',')
            print("Private Regions are ", self.private_region)
            self.public_region = event['SSMParametres']['SSMParametres'].split(',')
            print("Public Regions are ", self.public_region)
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
            self.target_tag = "tag:platform_ssminstall"
            self.rate_expression = "cron(0 2 ? * SUN *)"
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)
            raise Exception(str(exception))

    def create_ssm_agentau_association_public(self):
        '''
        Create SSM Association for SSM Agent Auto-Updated as per document - Public
        '''
        try:
            for region in self.public_region:
                print(region)
                self.ssm_childaccount_client = self.child_assume_role_session.client('ssm', region_name=region)
                if (not self.verify_association(self.ssm_childaccount_client, "platform_update_ssm_agent")):
                    response = self.ssm_childaccount_client.create_association(
                        Name="AWS-UpdateSSMAgent",
                        Targets=[
                            {
                                'Key': self.target_tag,
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.rate_expression,
                        AssociationName='platform_update_ssm_agent'
                    )
                    print("SSM association for platform auto update ssm agent has been created successfully!!!")
                    self.res_dict['ssm_agent_autoupdate_association_verification'] = "PASSED"
                else:
                    response = self.ssm_childaccount_client.update_association(
                        AssociationId=self.association_id,
                        Name="AWS-UpdateSSMAgent",
                        Targets=[
                            {
                                'Key': self.target_tag,
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.rate_expression,
                        AssociationName='platform_update_ssm_agent'
                    )
                    print("SSM association for platform auto update ssm agent has been been updated successfully!!!")
                    self.res_dict['ssm_agent_autoupdate_association_verification'] = "PASSED"
        except Exception as exception:
            print("Exception occurred while creating platform auto update ssm agent {}".format(str(exception)))
            self.res_dict['ssm_agent_autoupdate_association_verification'] = "FAILED"
            return self.res_dict

    def create_ssm_agentau_association_private(self):
        '''
        Create SSM Association for SSM Agent Auto-Updated as per document - Private
        '''
        try:
            for region in self.private_region:
                self.ssm_childaccount_client = self.child_assume_role_session.client('ssm', region_name=region)
                if (not self.verify_association(self.ssm_childaccount_client, "platform_update_ssm_agent")):
                    response = self.ssm_childaccount_client.create_association(
                        Name="AWS-UpdateSSMAgent",
                        Targets=[
                            {
                                'Key': self.target_tag,
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.rate_expression,
                        AssociationName='platform_update_ssm_agent'
                    )
                    print("SSM association for platform auto update ssm agent has been created successfully!!!")
                    self.res_dict['ssm_agent_autoupdate_association_verification'] = "PASSED"
                else:
                    response = self.ssm_childaccount_client.update_association(
                        AssociationId=self.association_id,
                        Name="AWS-UpdateSSMAgent",
                        Targets=[
                            {
                                'Key': self.target_tag,
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.rate_expression,
                        AssociationName='platform_update_ssm_agent'
                    )
                    print("SSM association for platform auto update ssm agent has been been updated successfully!!!")
                    self.res_dict['ssm_agent_autoupdate_association_verification'] = "PASSED"
        except Exception as exception:
            print("Exception occurred while creating platform auto update ssm agent {}".format(str(exception)))
            self.res_dict['ssm_agent_autoupdate_association_verification'] = "FAILED"
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
                self.res_dict['ssm_agent_autoupdate_association_verification'] = "PASSED"
                return True

            else:
                self.res_dict['ssm_agent_autoupdate_association_verification'] = "PASSED"
                return False
        except Exception as exception:
            print("Exception occurred while verifying SSM Association {}".format(str(exception)))
            self.res_dict['ssm_agent_autoupdate_association_verification'] = "FAILED"
            return self.res_dict

def lambda_handler(event, context):
    """"
    Create SSM Association for SSM Agent Auto-Updated as per document
    """
    try:
        result_values = {}
        result_values.update(event)
        print("Event {}".format(event))
        create_ssm_obj = SSMAgentAutoUpdate(event, context)
        account_type = event['ResourceProperties']['AccountType']
        if 'private' in account_type:
            print('account is private')
            create_ssm_obj.create_ssm_agentau_association_private()
            result_values.update(create_ssm_obj.res_dict)
            return result_values
        elif 'hybrid' in account_type:
            print('account is private')
            create_ssm_obj.create_ssm_agentau_association_private()
            result_values.update(create_ssm_obj.res_dict)
            return result_values
        elif 'public' in account_type or 'Migration' in account_type or 'Data-Managemen' in account_type or 'Managed_Services' in account_type:
            print('its public type account')
            create_ssm_obj.create_ssm_agentau_association_public()
            result_values.update(create_ssm_obj.res_dict)
            return result_values
        else:
            print("SSM agent auto update creation not reuired")
            return result_values
    except Exception as exception:
        print("Exception in Lambda Handler", exception)
        return event
