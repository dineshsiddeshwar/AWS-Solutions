'''
This class calls the Stepfunction for
the Account Creation, Updation and
Deletion test
'''
import random
import json
import logging
import datetime
import botocore
from dateutil.tz import tzlocal
import requests
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

SUCCESS = "SUCCESS"
FAILED = "FAILED"

"""
This Lambda Function will be called form service catalog when the account creation/update/delete is called.
this lambda will call the step function
"""
class AccountRequest(object):
    '''
    Recieve the request from the service catalog
    '''

    def __init__(self, event, context):
        self.event = event
        self.context = context
        self.servicecatalog_client = boto3.client('servicecatalog')
        self.stack_id = event['StackId']
        self.completedTimeStamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.account_number = ""
        self.dl_for_new_account = " "
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            # get relevant input params from event
            self.resource_properties = self.event['ResourceProperties']
            self.account_name = self.resource_properties['AccountName']
            session_client = boto3.session.Session()
            self.ssm_client = session_client.client('ssm')

            print("resource_properties", self.resource_properties)
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)
            print("Failed in except block of __init__")

    """Fecth the account details during update/delete"""
    def get_update_delete_account_details(self,response):
        try:
            for val in response['Stacks'][0]['Outputs']:
                if val['OutputKey'] == 'CTManagedAccountPPID':
                    self.event['ppid'] = val['OutputValue']
                if val['OutputKey'] == 'CompletedTimestamp':
                    self.event['completedTimeStamp'] = val['OutputValue']
                if val['OutputKey'] == 'DistributionID':
                    self.event['dlForNewAccount'] = val['OutputValue']
                if val['OutputKey'] == 'AccountNumber':
                    self.event['accountNumber'] = val['OutputValue']
                else:
                    self.event['accountNumber'] = "No-AccountNumber"
                self.event['emailParameter'] = []
        except Exception as exception:
            print("Exception Block of account details...", exception)
        # Sending status to the Cloud Formation so that it's status changes to success
        # in the begining itself and Rollbacks can be avoided
    def create_update_delete_account(self):
        '''
        This function is called by lambda_function for calling
        the step function.
        '''
        try:

            response_data = {}
            reason_data = ""
            step_function_name = self.account_name + '-' + \
                                 str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + \
                                 str(random.randint(1, 1000)) + self.event['ResourceProperties']['RequestNo']
            print("Step Function Name:", step_function_name)
            print('event' + str(self.event))
            print('context' + str(self.context))

            # Read parameters from SSM Parameter Store
            # result_value = self.get_ssm_parameters_as_dict()
            subscription_name = self.get_subscription_name()
            print("Subscription name returned is ", subscription_name)
            response = self.ssm_client.get_parameter(Name="admin_account")
            admin_account = response['Parameter']['Value']

            self.event.update({'subscription_name': subscription_name})
            print("Values after updating the event", self.event)
            print("Received a {} Request".format(self.event['RequestType']))

            """
            if the account is updated/deleted the fetch teh account details before calling the AVM step function 
            """
            if self.event['RequestType'] in ['Update', 'Delete']:
                cft_client = boto3.client('cloudformation')
                response = cft_client.describe_stacks(StackName=self.event['StackId'])
                print("Response>>>", response)
                if 'Outputs' in response['Stacks'][0].keys():
                    print("Response>>>", response['Stacks'][0]['Outputs'])

                    self.get_update_delete_account_details(response)

                    response_data = {
                        'AccountName': self.event['ResourceProperties']['AccountName'],
                        'Ppid': self.event['ppid'],
                        'DistributionID': self.event['dlForNewAccount'],
                        "AccountNumber": self.event['accountNumber'],
                        'CompletedTimestamp': self.event['completedTimeStamp']
                    }
                    print("Response Data SUCCESS>>", response_data)
                    # Send Success status to CFT
                    if self.event['RequestType'] in ['Delete']:
                        self.send(
                            event=self.event,
                            context=self.context,
                            response_status=SUCCESS,
                            response_data=response_data,
                            reason_data=reason_data
                        )
                else:
                    print("The event does not contains output values")
                    # If due to some unknown technical issues CFT does
                    # not sends out OUTPUT values a SUCCESS status is
                    # sent to the Cloud Formation so that it's
                    # status changes to success in the begining itself
                    # and Rollbacks can be avoided(THIS IS A RARE CASE)
                    response_data = {}
                    response_data = {
                        'AccountName': self.account_name,
                        'Ppid': '1234',
                        'DistributionID': self.dl_for_new_account,
                        "AccountNumber": 'No-AccountNumber',
                        'CompletedTimestamp': self.completedTimeStamp
                    }
                    print("Response Data SUCCESS>>", response_data)
                    # Send Success status to CFT
                    self.send(
                        event=self.event,
                        context=self.context,
                        response_status=SUCCESS,
                        response_data=response_data,
                        reason_data=reason_data
                    )

            print("event after account id updation  ", self.event)
            client = boto3.client('stepfunctions')
            response = client.start_execution(
                stateMachineArn='arn:aws:states:us-east-1:{}:stateMachine:platform_AVMStatemachine'.format(admin_account),
                name=step_function_name,
                input=json.dumps(self.event)
            )

            print(response)
                # LOGGER.info("Received event:{} ".format(response))
        except Exception as exception:
            print("Exception Block of lambda_handler...", exception)
            return exception

    def get_subscription_name(self):
        """Get the Provisioned Product name which will be used as Subscription Name """
        subscription_name = ""
        try:
            provision_product_id = 'pp-' + self.stack_id.split("/")[1].split("-")[3]
            response = self.servicecatalog_client.describe_provisioned_product(
                AcceptLanguage='en',
                Id=provision_product_id
            )
            subscription_name = response['ProvisionedProductDetail']['Name']
            print("Subscription value in get_subscription_name", subscription_name)

        except Exception as exception:
            print("Error occurred in get_provisioned_product_name ", str(exception))

        return subscription_name

    def send(self, event, context, response_status, response_data, reason_data):
        '''
        Send status to the cloudFormation
        Template.
        '''
        print("Inside send method")
        response_url = event['ResponseURL']

        response_body = {}
        response_body['Status'] = response_status
        response_body['Reason'] = reason_data + ' See the details in CloudWatch Log Stream: ' + \
                                  context.log_stream_name
        response_body['PhysicalResourceId'] = event['PhysicalResourceId']
        response_body['StackId'] = event['StackId']
        response_body['RequestId'] = event['RequestId']
        response_body['LogicalResourceId'] = event['LogicalResourceId']
        response_body['Data'] = response_data

        json_responsebody = json.dumps(response_body)

        print("Response body:{}".format(json_responsebody))

        headers = {
            'content-type': '',
            'content-length': str(len(json_responsebody))
        }

        try:
            response = requests.put(response_url,
                                    data=json_responsebody,
                                    headers=headers)
            print("Status code:{} ".format(response.reason))
        except Exception as exception:
            print("send(..) failed executing requests.put(..):{} ".format(str(exception)))


def lambda_handler(event, context):
    '''
    Lamda handler that calls the Step functions for the dedicated Account
    '''
    print('event ' + str(event))
    print('type of event ' + str(type(event)))
    try:
        print("Received a {} Request".format(event['RequestType']))
        acccountrequest = AccountRequest(event, context)
        output = acccountrequest.create_update_delete_account()
        print("Output of the function : " + str(output))
    except Exception as exception:
        print(exception)
        return exception
