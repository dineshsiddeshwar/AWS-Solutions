'''
Check Provision ProductStat
'''

import random
import time
import json
import logging
import requests
import boto3
import datetime

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

SESSION = boto3.Session()
STS_CLIENT = SESSION.client('sts')
sc_client = SESSION.client('servicecatalog')

"""
This Lambda function is used to check the status of the Control tower Account creation product
"""

class AccountNumber(object):
    '''
    Class: Check_PPStatus
    Description: Checks whether provision Product is available
    '''

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            self.AccountId = "No-AccountID"
            self.reason_data = ""
            self.completedTimeStamp = "No time"
            self.response_data = {}
            # get relevant input params from event
            self.resource_properties = event['ResourceProperties']
            self.RequestType = event['RequestType']
            self.ppid = event['ppid']
            self.account_name = self.resource_properties['AccountName']
            if self.resource_properties['Migration'] == "Yes":
                self.dl_for_new_account = self.resource_properties['dlForNewAccount']
            else:
                self.dl_for_new_account = event['dlForNewAccount']
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)
            print("Failed in except block of __init__")

    """Send Early response to the Service Catalog if the Account creation is taking more the 1 hour to avoide time out
    the avm step function waits for 4 min between each call to this lambda function.
    """
    def send_response_to_service_catalog_to_avoide_timeout(self):
        try:
            if (self.event['request_product_count'] >= 14):
                print ("Send Response To Service Catalog to avoid Time Out Exception if the Account Creation or Update will take "
                       "more then 60 Minutes.")
                if self.AccountId == "No-AccountID":
                    self.AccountId = "No Account Number Generated"

                # Response for Cloudformation
                self.response_data = {
                    'AccountName': self.account_name,
                    'AccountNumber': self.AccountId,
                    'DistributionID': self.dl_for_new_account,
                    'CompletedTimestamp': self.completedTimeStamp,
                    'Ppid': self.ppid
                }
                self.send_status(SUCCESS)
        except Exception as e:
            raise Exception (str(e))
        

    def get_responce_provision_product(self, filter, search_filter):
        """
        Method: To get get responce from provision product
        """
        sleep_time = 30
        try:
            while True :
                LOGGER.info("Inside get_responce_provision_product")
                search_response = sc_client.search_provisioned_products(
                            AccessLevelFilter=filter,
                            Filters={"SearchQuery": [search_filter]}
                        )
                print(search_response)
                if search_response['ProvisionedProducts'] == []:
                    print("API was unable to fetch ppid details....Re-trying")
                    time.sleep(sleep_time)
                else:
                    print("API was able to fetch ppid details")
                    status = search_response['ProvisionedProducts'][0]['Status']
                    print(status)
                    return search_response, status
        except RuntimeError as error:
            status = 'ERROR'
            response = {'ProvisionedProducts' : [{'Status' : 'ERROR'}]}
            LOGGER.error("There was no respone from provision product. Error {0}.".format(error))
            return response, status


    def get_accountnumber(self):
        '''
        get Account number from provisioned product
        '''
        try:
            failed_state = ["TAINTED", "ERROR"]
            res = {}
            filter = {'Key': 'Account', 'Value': 'self'}
            search_filter = "id:" + self.ppid

            search_response, status = self.get_responce_provision_product(filter, search_filter)
            
            if status == 'AVAILABLE':
                if 'PhysicalId' in search_response['ProvisionedProducts'][0]:
                    self.AccountId = search_response['ProvisionedProducts'][0]['PhysicalId']
                    print(self.AccountId)
                if 'CreatedTime' in search_response['ProvisionedProducts'][0]:
                    self.completedTimeStamp = (search_response['ProvisionedProducts'][0]['CreatedTime'])\
                    .strftime("%d-%m-%Y %H:%M:%S")
            '''
            Send Response To Service Catalog to avoid Time Out Exception if the Account Creation or Update will take 
            more then 60 Minutes. 
            '''
            self.send_response_to_service_catalog_to_avoide_timeout()


            if status == 'AVAILABLE':
                # Fetch AccountId from PPID
                print ("AVAILABLE")
                print("Account Id is :", self.AccountId)
                # Response for stepfunction
                res.update({
                    'AccountCreationStatus': status,
                    'emailParameter': ['accountSuccess'],
                    'accountNumber': self.AccountId,
                    'completedTimeStamp': self.completedTimeStamp

                })
                # Response for Cloudformation
                self.response_data = {
                    'AccountName': self.account_name,
                    'AccountNumber': self.AccountId,
                    'DistributionID': self.dl_for_new_account,
                    'CompletedTimestamp': self.completedTimeStamp,
                    'Ppid': self.ppid
                }
                self.send_status(SUCCESS)
                return res

            elif status in failed_state:
                print("FAILED")
                failure_reason = "Status is :" + status + " " + search_response['ProvisionedProducts'][0][
                    'StatusMessage']

                self.reason_data = failure_reason
                print("New account {} creation failed because of {}".format(
                    self.account_name, failure_reason))
                res.update({'emailParameter': ['accountFailure'],
                            'AccountCreationStatus': 'FAILED',
                            'failure_reason': failure_reason
                            }
                           )
                self.response_data = {
                    'AccountName': self.account_name,
                    'AccountNumber': self.AccountId,
                    'DistributionID': self.dl_for_new_account,
                    'CompletedTimestamp': self.completedTimeStamp,
                    'Ppid': self.ppid
                }
                self.send_status(SUCCESS)
                return res
            else:
                print("AVAILABLE")
                res.update({
                    'AccountCreationStatus': 'UNDER CHANGE',
                    'emailParameter': ['accountSuccess'],
                    'accountNumber': self.AccountId,
                    'completedTimeStamp': self.completedTimeStamp
                })
                """
                self.response_data = {
                     'AccountName': self.account_name,
                     'AccountNumber': self.AccountId,
                     'DistributionID': self.dl_for_new_account,
                     'CompletedTimestamp': self.completedTimeStamp,
                     'Ppid': self.ppid
                }
                self.send_status(SUCCESS)
                """
                return res
        except Exception as exception:
            print("send(..) failed executing GET account number:{} ".format(
                str(exception)))

    def send_status(self, pass_or_fail):
        '''
        Send the status of the Child Account Creation to  Cloudformation Template.
        '''
        self.send(
            event=self.event,
            context=self.context,
            response_status=pass_or_fail,
            response_data=self.response_data,
            reason_data=self.reason_data
        )

    def send(self, event, context, response_status, response_data, reason_data):
        '''
        Called by send status to send the status
        '''
        print("Inside send method")
        response_url = event['ResponseURL']

        response_body = {}
        response_body['Status'] = response_status
        response_body['Reason'] = reason_data + \
                                  ' See the details in CloudWatch Log Stream: ' + context.log_stream_name
        response_body['PhysicalResourceId'] = context.log_stream_name
        response_body['StackId'] = event['StackId']
        response_body['RequestId'] = event['RequestId']
        response_body['LogicalResourceId'] = event['LogicalResourceId']
        response_body['Data'] = response_data

        json_response_body = json.dumps(response_body)

        print("Response body:{}".format(json_response_body))

        headers = {
            'content-type': '',
            'content-length': str(len(json_response_body))
        }

        try:
            response = requests.put(response_url,
                                    data=json_response_body,
                                    headers=headers)
            print("Status code:{} ".format(response.reason))
        except Exception as exception:
            print("send(..) failed executing requests.put(..):{} ".format(
                str(exception)))


def lambda_handler(event, context):
    """Starting Point of the Function .Checks the status of provision product and returns the Account details"""
    result = {}
    # print('event ' + str(event))
    result.update(event)
    try:
        print("Received a {} Request".format(event['RequestType']))
        account = AccountNumber(event, context)
        output = account.get_accountnumber()
        print("Output of the function : " + str(output))
        result.update(output)
        result.update({"request_product_count":result['request_product_count']+1})
        return result
    except Exception as exception:
        print(exception)
        return exception
