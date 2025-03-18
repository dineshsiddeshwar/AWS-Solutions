'''
Create SSM Association to Install and Configure CloudWatch Agent
'''
import logging
import random
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

class InstallCloudwatchagent(object):
    """
    # Class: InstallFalconagent
    # Description: Prerequisite for InstallFalconagent proccess
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
            print(self.child_account_number)
            self.private_region = event['SSMParametres']['whitelisted_regions_private'].split(',')
            print("Private Regions are ", self.private_region)
            self.public_region = event['SSMParametres']['whitelisted_regions_public'].split(',')
            print("Public Regions are ", self.public_region)
            account_type = event['ResourceProperties']['AccountType']
            if 'private' in account_type:
                self.regions = self.private_region
                print(self.regions)
            elif 'hybrid' in account_type:
                self.regions = self.private_region
                print(self.regions)
            elif 'public' in account_type:
                self.regions = self.public_region
                print(self.regions)
            elif 'Data-Management' in account_type:
                self.regions = self.public_region
                print(self.regions)
            elif 'Migration' in account_type:
                self.regions = self.public_region
                print(self.regions)                
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
            self.rate_expression = "rate(240 minutes)"
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)
            raise Exception(str(exception))

    def install_agent(self):
        '''
        Create the SSM Association in the child account to Install CloudWatch Agent
        '''
        try:
            for region in self.regions:

                self.ssm_childaccount_client = self.child_assume_role_session.client('ssm',
                                                                                     region_name=region)
                if (not self.verify_association(self.ssm_childaccount_client, "platform_InstallCloudWatchAgent")):
                    response = \
                        self.ssm_childaccount_client.create_association(Name="AWS-ConfigureAWSPackage",
                                                                        Parameters={
                                                                            'action': ["Install"],
                                                                            'version': ["latest"],
                                                                            'name': ["AmazonCloudWatchAgent"]
                                                                        },
                                                                        Targets=[
                                                                            {
                                                                                'Key': "tag:platform_cloudwatch",
                                                                                'Values': ['yes']
                                                                            },
                                                                        ],
                                                                        ScheduleExpression=self.rate_expression,
                                                                        AssociationName='platform_InstallCloudWatchAgent'
                                                                        )
                    print("SSM Association to install CloudWatch Agent created successfully "
                          "in region {}".format(region))
                    self.res_dict['Cloudwatch_association_creation'] = "PASSED"
                else:
                    print("Association already present!!!")
                    self.res_dict['Cloudwatch_association_creation'] = "PASSED"
                    """
                    # return self.res_dict
                    """
            self.configure_agent_windows()
            self.configure_agent_linux()
        except Exception as exception:
            print("Exception occurred while creating SSM Association to install CloudWatch"
                  " Agent {}".format(str(exception)))
            self.res_dict['Cloudwatch_association_creation'] = "FAILED"
            raise Exception(str(exception))

    def configure_agent_windows(self):
        '''
        Create the SSM Association in the child account to Configure CloudWatch Agent
        '''
        ssm_parameter_name_win = ["platform_AmazonCloudWatch-windows"]
        for region in self.regions:
            try:
                self.ssm_childaccount_client = self.child_assume_role_session.client('ssm',
                                                                                     region_name=region)
                if (not self.verify_association(self.ssm_childaccount_client, "platform_AmazonCloudWatch-Windows")):
                    response = \
                        self.ssm_childaccount_client.create_association(Name="AmazonCloudWatch-ManageAgent",
                                                                        Parameters={
                                                                            'action': ["configure"],
                                                                            'optionalConfigurationSource': ["ssm"],
                                                                            'optionalConfigurationLocation': ssm_parameter_name_win,
                                                                            'optionalRestart': ["yes"],
                                                                            'mode': ["ec2"]
                                                                        },
                                                                        Targets=[
                                                                            {
                                                                                'Key': "tag:platform_cloudwatch_windows",
                                                                                'Values': ['yes']
                                                                            },
                                                                        ],
                                                                        ScheduleExpression=self.rate_expression,
                                                                        AssociationName='platform_AmazonCloudWatch-Windows')
                    print("SSM Association to configure CloudWatch Agent for windows created"
                          " successfully in region {}".format(region))
                    self.res_dict['Cloudwatch_association_creation_config_win'] = "PASSED"
                else:
                    response = self.ssm_childaccount_client.update_association(
                        AssociationId=self.association_id,
                        Name="AmazonCloudWatch-ManageAgent",
                        Parameters={
                            'action': ["configure"],
                            'optionalConfigurationSource': ["ssm"],
                            'optionalConfigurationLocation': ssm_parameter_name_win,
                            'optionalRestart': ["yes"],
                            'mode': ["ec2"]
                        },
                        Targets=[
                            {
                                'Key': "tag:platform_cloudwatch_windows",
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.rate_expression,
                        AssociationName='platform_AmazonCloudWatch-Windows')
                    print("SSM Association to configure CloudWatch Agent for windows updated"
                          " successfully in region {}".format(region))
                    self.res_dict['Cloudwatch_association_creation_config_win'] = "PASSED"
            except Exception as exception:
                print("Exception occurred while creating SSM Association to configure Windows"
                      " Agent {}".format(str(exception)))
                self.res_dict['Cloudwatch_association_creation_config_win'] = "FAILED"
                raise Exception(str(exception))

    def configure_agent_linux(self):
        '''
        Create the SSM Association in the child account to Configure CloudWatch Agent
        '''
        ssm_parameter_name = ["platform_AmazonCloudWatch-Linux"]
        for region in self.regions:
            print(region)
            try:
                self.ssm_childaccount_client = self.child_assume_role_session.client('ssm',
                                                                                     region_name=region)
                if (not self.verify_association(self.ssm_childaccount_client,\
                                                "platform_AmazonCloudWatch-Linux")):
                    response = \
                        self.ssm_childaccount_client.create_association(\
                            Name="AmazonCloudWatch-ManageAgent",
                            Parameters={
                                'action': ["configure"],
                                'optionalConfigurationSource': ["ssm"],
                                'optionalConfigurationLocation': ssm_parameter_name,
                                'optionalRestart': ["yes"],
                                'mode': ["ec2"]
                            },
                            Targets=[
                                {
                                    'Key': "tag:platform_cloudwatch_linux",
                                    'Values': ['yes']
                                },
                            ],
                            ScheduleExpression=self.rate_expression,
                            AssociationName='platform_AmazonCloudWatch-Linux'
                        )
                    print("SSM Association to configure CloudWatch Agent for windows created"
                          " successfully in region {}".format(region))
                    self.res_dict['Cloudwatch_association_creation_config_linux'] = "PASSED"
                else:
                    response = self.ssm_childaccount_client.update_association(
                        AssociationId=self.association_id,
                        Name="AmazonCloudWatch-ManageAgent",
                        Parameters={
                            'action': ["configure"],
                            'optionalConfigurationSource': ["ssm"],
                            'optionalConfigurationLocation': ssm_parameter_name,
                            'optionalRestart': ["yes"],
                            'mode': ["ec2"]
                        },
                        Targets=[
                            {
                                'Key': "tag:platform_cloudwatch_linux",
                                'Values': ['yes']
                            },
                        ],
                        ScheduleExpression=self.rate_expression,
                        AssociationName='platform_AmazonCloudWatch-Linux')
                    print("SSM Association to configure CloudWatch Agent for linux updated"
                          " successfully in region {}".format(region))
                    self.res_dict['Cloudwatch_association_creation_config_linux'] = "PASSED"
            except Exception as exception:
                print("Exception occurred while creating SSM Association to configure Linux"
                      " Agent {}".format(str(exception)))
                self.res_dict['Cloudwatch_association_creation_config_linux'] = "FAILED"
                raise Exception(str(exception))

    def verify_association(self, ssm_childaccount_client, association_name):
        print("Inside Verify")
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

            print(response)
            if (response['Associations'].__len__() > 0):
                self.association_id = response['Associations'][0]['AssociationId']
                return True
            else:
                return False

        except Exception as exception:
            print("Exception occurred while verifying SSM Association {}".format(str(exception)))
            return False
def lambda_handler(event, context):
    '''
    Main lambda handler takes event as dictionary
    and context as an object
    '''
    try:
        result_values = {}
        result_values.update(event)
        print("Event {}".format(event))
        install_cloudwatch_agent_object = InstallCloudwatchagent(event, context)
        install_cloudwatch_agent_object.install_agent()
        result_values.update(install_cloudwatch_agent_object.res_dict)
        return result_values
    except Exception as exception:
        print("Exception in Lambda Handler", exception)
        event['Cloudwatch_association_creation'] = "FAILED"
        return event