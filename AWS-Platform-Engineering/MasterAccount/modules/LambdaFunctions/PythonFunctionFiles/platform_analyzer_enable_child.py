"""
This module is used to enable IAM Access Analyzer in the child account.
"""
import random
import logging
import boto3

LOGGER = logging.getLogger('logging')
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


class EnableAnalyzer:
    """
    # Class: Enable IAM Access Analyzer
    # Description: Includes method to enable IAM Access Analyzer in the child account
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            # get relevant input params from event
            self.reason_data = ""
            self.res_dict = {}
            session_client = boto3.Session()
            self.ssm_client = session_client.client('ssm')
            #regions_response = self.ssm_client.get_parameter(Name="whitelisted_regions")
            #self.whitelisted_regions_ssm = regions_response['Parameter']['Value']
            self.whitelisted_regions_ssm = event['SSMParametres']['whitelisted_regions']
            self.region = self.whitelisted_regions_ssm.split(',')
            self.resource_properties = event['ResourceProperties']
            #audit_response = self.ssm_client.get_parameter(Name="audit_account")
            audit_account = event['SSMParametres']['audit_account']
            self.account_number = event['accountNumber']
            if self.resource_properties['Migration'] == "Yes":
               self.res_dict = {'accountNumber': self.account_number,
                             'RequestType': event['RequestType'],
                             'dlForNewAccount': self.resource_properties['dlForNewAccount'],
                             'whitelisted_regions': self.region,
                             'SSMParametres': event['SSMParametres'],
                             'audit_account': audit_account}
            else:
                self.res_dict = {'accountNumber': self.account_number,
                             'RequestType': event['RequestType'],
                             'dlForNewAccount': event['dlForNewAccount'],
                             'whitelisted_regions': self.region,
                             'SSMParametres': event['SSMParametres'],
                             'audit_account': audit_account}
            self.sts_client = session_client.client('sts')
            if self.resource_properties['Migration'] == "Yes":
                self.dl_for_new_account = self.resource_properties['dlForNewAccount']
            else:
                self.dl_for_new_account = event['dlForNewAccount']
            self.account_number = event['accountNumber']
            self.child_account_role_arn = "arn:aws:iam::{}:role/AWSControlTowerExecution".\
                                          format(self.account_number)
            self.child_account_session_name = "childAccountSession-" + \
                                              str(random.randint(1, 100000))
            self.child_account_role = self.sts_client.assume_role(
                                            RoleArn=self.child_account_role_arn,
                                            RoleSessionName=self.child_account_session_name)
            self.child_credentials = self.child_account_role.get('Credentials')
            self.child_access_key = self.child_credentials.get('AccessKeyId')
            self.child_secret_access_key = self.child_credentials.get('SecretAccessKey')
            self.child_session_token = self.child_credentials.get('SessionToken')
            self.child_assume_role_session = boto3.Session(
                                             self.child_access_key,
                                             self.child_secret_access_key,
                                             self.child_session_token)
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)

    def status_analyzer(self):
        """
        Check IAM Access Analyzer status in the child account.
        """
        print("Inside Check Analyzer status Function")
        try:
            for region in self.region:
                print('Inside Region - {}'.format(region))
                analyzer_client = self.child_assume_role_session.client(
                                    'accessanalyzer', region_name=region)
                ls_analyzer = analyzer_client.list_analyzers(type='ACCOUNT')
                while ls_analyzer.get('NextToken'):
                    ls_analyzer = analyzer_client.list_detectors(NextToken=ls_analyzer['NextToken'])
                if len(ls_analyzer['analyzers']) != 0:
                    for analyzer in ls_analyzer['analyzers']:
                        if analyzer['name'] != 'platform_analyzer_' + region:
                            delete_analyzer = analyzer_client.delete_analyzer(
                                              analyzerName=ls_analyzer['analyzers'][0].get('name'))
                            print('Delete analyzer - {}'.format(delete_analyzer))
                        elif analyzer['name'] == 'platform_analyzer_' + region:
                            self.validate_analyzer(analyzer_client, region)
                else:
                    print('Calling Create Analyzer')
                    self.create_analyzer(analyzer_client, region)
                    self.validate_analyzer(analyzer_client, region)

        except Exception as exception:
            self.reason_data = "Checking for status of Analyzer %s" % exception
            LOGGER.error(self.reason_data)
            print("ERROR Checking Analyzer status", exception)
            self.res_dict['Enable Analyzer Child'] = 'FAILED'
            return self.res_dict

        return self.res_dict

    def create_analyzer(self, analyzer_client, region):
        """
        Create IAM Access Analyzer status in the child account.
        """
        print('Inside Enable Analyzer function in account - {}'.format(self.account_number))
        create_analyzer = analyzer_client.create_analyzer(analyzerName=('platform_analyzer_' + region), 
                                                          type='ACCOUNT',
                                                          tags={
                                                              'platform_donotdelete': 'yes'
                                                          }
                                                          )
        print('Create Analyzer  in Child - {}'.format(create_analyzer))

    def validate_analyzer(self, analyzer_client, region):
        """
        Validate IAM Access Analyzer status in the child account.
        """
        print('Inside Validate Analyzer')
        get_analyzer = analyzer_client.get_analyzer(analyzerName=('platform_analyzer_' + region))
        if 'DISABLED' or 'FAILED' not in get_analyzer['analyzer']['status']:
            self.res_dict['Enable Analyzer Child'] = 'PASSED'
        else:
            raise Exception('Enable Analyzer Exception')


def lambda_handler(event, context):
    """"
    Lambda handler that calls the function to create IAM Access Analyzer
    """
    result_value = {}
    try:
        # result_value.update(event)
        iam_analyzer_obj = EnableAnalyzer(event, context)
        output_value = iam_analyzer_obj.status_analyzer()
        print("Output of the function : "+str(output_value))
        result_value.update(output_value)
        return result_value

    except Exception as exception:
        print("Error in Lambda Handler", exception)
        result_value['Handler Exception'] = str(exception)
        return result_value
