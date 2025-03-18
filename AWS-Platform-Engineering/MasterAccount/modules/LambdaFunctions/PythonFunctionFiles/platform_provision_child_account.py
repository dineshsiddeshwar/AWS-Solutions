'''
Provision Account Factory product
'''

import random
import time
import datetime
import json
import logging
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
"""
# INPROGRESS = "INPROGRESS"
# FAILED = "FAILED"
"""

SESSION = boto3.Session()
STS_CLIENT = SESSION.client('sts')
sc_client = SESSION.client('servicecatalog')


class CreateAccount(object):
    '''
    Class: CreateAccount
    Description: Includes all the properties and methods to create a new child
    account from Control Tower Account Factory
    '''

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            self.reason_data = ""
            self.response_data = {}
            self.completed_timestamp = ""
            self.completedTimeStamp = ""
            self.account_number = ""
            # get relevant input params from event
            self.resource_properties = event['ResourceProperties']
            print(self.resource_properties)
            self.account_name = self.resource_properties['AccountName']
            if self.resource_properties['Migration'] == "Yes":
                self.dl_for_new_account = self.resource_properties['dlForNewAccount']
            else:
                self.dl_for_new_account = event['dlForNewAccount']
            self.request_type = event['RequestType']
            session_client = boto3.Session()
            self.af_productid = event['SSMParametres']['AFproductid']
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)
            print("Failed in except block of __init__")


    def create_the_account(self):
        '''
            The following function creates a new child account and returns the value
            to lamda handler
        '''
        res = {}
        try:
            provision_artifact = " "
            provision_response = ""

            pa_res = sc_client.list_provisioning_artifacts(
                ProductId=self.af_productid
            )
            for pa in pa_res['ProvisioningArtifactDetails']:
                if pa['Active'] == True:
                    provision_artifact = pa['Id']
                    print(pa['Id'])
            try:

                provision_response = sc_client.provision_product(
                    ProductId=self.af_productid,
                    ProvisioningArtifactId=provision_artifact,
                    ProvisionedProductName="AFPP-" + self.account_name,
                    ProvisioningParameters=[
                        {
                            "Key": "AccountName",
                            "Value": self.account_name
                        },
                        {
                            "Key": "AccountEmail",
                            "Value": self.dl_for_new_account
                        },
                        {
                            "Key": "SSOUserFirstName",
                            "Value": self.resource_properties['CustodianUserFirstName']
                        },
                        {
                            "Key": "SSOUserLastName",
                            "Value": self.resource_properties['CustodianUserLastName']
                        },
                        {
                            "Key": "SSOUserEmail",
                            "Value": self.resource_properties['CustodianUser']
                        },
                        {
                            "Key": "ManagedOrganizationalUnit",
                            "Value": self.resource_properties['Environment']
                        }
                    ]

                )

                print(provision_response)
            except Exception as exception:
                print(exception)
                failure_reason = exception
                self.reason_data = failure_reason
                result_account_creation = 'Fail'
                print("New account {} creation failed because of {}".format(
                    self.account_name, failure_reason))
                res.update({'emailParameter': ['accountFailure'],
                            'ResultAccountCreation': result_account_creation
                            }
                           )

            status = provision_response['RecordDetail']['Status']
            if status == "FAILED":
                failure_reason = provision_response['RecordDetail']['RecordErrors']
                self.reason_data = failure_reason
                result_account_creation = 'Fail'
                print("New account {} creation failed because of {}".format(
                    self.account_name, failure_reason))
                res.update({'emailParameter': ['accountFailure'],
                            'ResultAccountCreation': result_account_creation
                            }
                           )
                
            else:
                result_account_creation = 'Success'
                ppid = provision_response['RecordDetail']['ProvisionedProductId']
                self.completedTimeStamp = (provision_response['RecordDetail']['CreatedTime'])\
                    .strftime("%d-%m-%Y")
                print(ppid)
                #Response to stepfuncion
                res.update({
                    'ResultAccountCreation': result_account_creation,
                    'emailParameter': ['accountSuccess'],
                    'ppid': ppid
                })
            return res
        except Exception as exception:
            print(exception)
            self.reason_data = "Account creation failed %s" % exception
            LOGGER.error(self.reason_data)
            res.update({'emailParameter': ['accountFailure'],
                        'ResultAccountCreation': 'Fail',
                        'reason_data': self.reason_data})
            return res

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

    def updateprovisionproduct(self, ppid):

        print("Inside updateProvisionProduct")

        print (ppid)
        res = {}
        try:
            provision_artifact = " "
            pa_res = sc_client.list_provisioning_artifacts(
                ProductId=self.af_productid
            )
            for pa in pa_res['ProvisioningArtifactDetails']:
                if pa['Active']:
                    provision_artifact = pa['Id']
                    print("Product Artifact ID:", pa['Id'])

            update_response = sc_client.update_provisioned_product(
                ProvisionedProductId=ppid,
                ProductId=self.af_productid,
                ProvisioningArtifactId=provision_artifact,
                ProvisioningParameters=[
                    {
                        "Key": "AccountName",
                        "Value": self.account_name
                    },
                    {
                        "Key": "AccountEmail",
                        "Value": self.dl_for_new_account
                    },
                    {
                        "Key": "SSOUserFirstName",
                        "Value": self.resource_properties['CustodianUserFirstName']
                    },
                    {
                        "Key": "SSOUserLastName",
                        "Value": self.resource_properties['CustodianUserLastName']
                    },
                    {
                        "Key": "SSOUserEmail",
                        "Value": self.resource_properties['CustodianUser']
                    },
                    {
                        "Key": "ManagedOrganizationalUnit",
                        "Value": self.resource_properties['Environment']
                    }
                ]
            )

            print("Update Product Response: ", update_response)

            status = update_response['RecordDetail']['Status']
            if status == "FAILED":
                failure_reason = update_response['RecordDetail']['RecordErrors']
                self.reason_data = failure_reason
                result_account_creation = 'Fail'
                print("Update account {}  failed because of {}".format(
                    self.account_name, failure_reason))
                res.update({'emailParameter': ['accountFailure'],
                            'ResultAccountCreation': result_account_creation
                            }
                           )
                self.send_status(status)
            else:
                result_account_creation = 'Success'
                ppid = update_response['RecordDetail']['ProvisionedProductId']
                self.completedTimeStamp = (update_response['RecordDetail']['CreatedTime'])\
                    .strftime("%d-%m-%Y")
                print(ppid)
                res.update({
                    'ResultAccountCreation': result_account_creation,
                    'emailParameter': ['accountSuccess'],
                    'ppid': ppid
                })

            return res
        except Exception as exception:
            print(exception)
            self.reason_data = "Account update failed %s" % exception
            LOGGER.error(self.reason_data)
            res.update({'emailParameter': ['accountFailure'],
                        'ResultAccountCreation': 'Fail',
                        'reason_data': self.reason_data})
            self.send_status('FAILED')
            return res

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
    """ Start of the function this function will
     handle create and update Account Factory product"""
    result = {}
    print('event ' + str(event))
    result.update(event)
    try:
        print("Received a {} Request".format(event['RequestType']))
        account = CreateAccount(event, context)
        if event['RequestType'] == 'Update' and event['ppid']:
            output = account.updateprovisionproduct(event['ppid'])
            result.update(output)
            result.update({"request_product_count": 1})

            return result
        output = account.create_the_account()
        print("Output of the function : " + str(output))
        result.update(output)
        result.update({"request_product_count":1})

        return result
    except Exception as exception:
        print(exception)
        return exception

