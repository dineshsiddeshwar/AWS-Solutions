"""
This module is used as part of account inflation to enable enterprise support in member account
"""
import random
import logging
import boto3
import json

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

class EnableEnterpriseSupport(object):

    """
    This class is used to enable enterprise support for member account
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        self.exception = []
        try:
            session_client = boto3.session.Session()
            self.ssm_client = session_client.client('ssm')
            self.create_case_ccadress = event['SSMParametres']['create_case_ccadress']
            # get relevant input params from event
            self.account_number = event['accountNumber']
            self.account_name = event['ResourceProperties']['AccountName']
            self.request_type = event['RequestType']
            session_client = boto3.session.Session()
            sts_client = session_client.client('sts')
            self.supp_master_client = session_client.client('support')
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)
            self.exception.append(str(exception))
            raise Exception(str(exception))


    def create_case(self):
        """
        Raise a ticket in Master account to enable technical
        support(Enterprise Support) for child account.
        :return:
        """
        try:
            print("accountNumber", self.account_number)
            print("accountName", self.account_name)
            response_describe_cases = self.supp_master_client.describe_cases()
            print("response_describe_cases", response_describe_cases)
            response_describe_services = self.supp_master_client.describe_services()
            print("response_describe_services", response_describe_services)
            res_desc_sev_level = self.supp_master_client.describe_severity_levels()
            print("response_describe_severity_levels", res_desc_sev_level)
            print("RequestType>>>", self.request_type)
            if self.request_type == 'Create':
                # Todo:  Change severity code from low to high
                response = self.supp_master_client.create_case(
                    issueType="customer-service",
                    subject='Enabled Enterprise Support for account ' + self.account_number,
                    serviceCode='account-management',
                    categoryCode='billing',
                    severityCode='low',
                    communicationBody='Hi Team,' +
                    'Please enable Enterprise Support for newly created accounts mentioned : '
                    + self.account_number+" "+self.account_name,
                    ccEmailAddresses=[self.create_case_ccadress],
                    language='en'
                )
                print("Response>>>>", response)
                pass
            else:
                print('The request type is ' + self.request_type + ', so no request created')

            return True, self.exception
        except Exception as exception:
            print("Error while creating enterprise support case", exception)
            self.exception.append(str(exception))
            return True, self.exception


def lambda_handler(event, context):
    """
            This is the entry point of the module
            :param event:
            :param context:
            :return:
    """
    try:
        result_values = {}
        result_values.update(event)
        enable_support_object = EnableEnterpriseSupport(event, context)
        output_value,exception = enable_support_object.create_case()
        print("result_values ", result_values)
        result = {}
        if output_value == True:
            result['enableEnterpriseSupport'] = "PASSED"
            print("No output to pass to the next state")
        else:
            result['enableEnterpriseSupport'] = "FAILED"
        print(json.dumps(result))
        return result
    except Exception as exception:
        print("Error in lambda_handler", exception)
        result = {}
        result['enableEnterpriseSupport'] = False
        error_exception = []
        error_exception.append(exception)
        return result
