import random
import json
import datetime
import requests
import boto3

SUCCESS = "SUCCESS"
FAILED = "FAILED"
NO_VPC = "No-VPC"
FALSE = "false"
TRUE = "true"


class NetworkRequest(object):
    '''
    Receive the request from the service catalog'''

    def __init__(self, event, context):
        print("Inside init")
        session_client = boto3.session.Session()
        self.ssm_client = session_client.client('ssm')
        self.event = event
        self.context = context
        self.reason_data = " "
        self.resource_properties = event['ResourceProperties']
        self.account_no = self.resource_properties['AccountNumber']
        self.nonroutable_subnets = self.resource_properties['IsNonroutableSubnets']
        print(self.account_no)
        self.account_name = " "
        self.res_dict = {}
        self.event['Extension_data'] = []
        reason_data = " "
        n_virginia_vpc = NO_VPC
        ireland_vpc = NO_VPC
        singapore_vpc = NO_VPC
        self.completedTimeStamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.response_data = {
            'AccountNumber': self.account_no,
            'AccountName': "NA",
            'NVirginiaVPC': n_virginia_vpc,
            'IrelandVPC': ireland_vpc,
            'SingaporeVPC': singapore_vpc,
            'IsNonroutableSubnets': self.nonroutable_subnets
        }

    def get_region_ip(self):
        '''
        Method to get the region and ip, add regions here in case of more region to be updated
        '''
        try:
            region_ip_dict = {}
            for region_name in self.resource_properties.keys():
                if region_name == 'NVirginia' and self.resource_properties[region_name] != "No-VPC":
                    region_ip_dict.update({"us-east-1": self.resource_properties[region_name]})
                if region_name == 'Ireland' and self.resource_properties[region_name] != "No-VPC":
                    region_ip_dict.update({"eu-west-1": self.resource_properties[region_name]})
                if region_name == 'Singapore' and self.resource_properties[region_name] != "No-VPC":
                    region_ip_dict.update({"ap-southeast-1": self.resource_properties[region_name]})
            print(region_ip_dict)
            self.event['region_ip_dict'] = region_ip_dict
            return region_ip_dict
        except Exception as e:
            print("Error occurred in fetching region", str(e))

    def get_extension_data(self, parameter):

        '''Get vpc extension data if there is a vpc extension request'''
        try:
            extension_id = str(parameter)[-1]
            vpc_parameter = "VPCID" + extension_id
            ip = self.resource_properties[parameter]
            vpc_id = self.resource_properties[vpc_parameter]
            print(extension_id, vpc_parameter, vpc_id)
            ext_row = {
                'vpc_id': vpc_id,
                'ip': ip}

            # if extension data has same vpc id for update fail the update request
            for row in self.event['Extension_data']:
                if row['vpc_id'] == ext_row['vpc_id']:
                    self.res_dict['param_valid'] = FAILED

            self.event['Extension_data'].append(ext_row)
            # If extension_data is NULL
            if not self.event['Extension_data']:
                self.res_dict['param_valid'] = FAILED

        except Exception as e:
            print("Error occurred in getting extension data", str(e))

    def invoke_stepfunction(self, regions):
        ''' method to invoke network request stepfunction '''
        try:
            # GET stepfunction name
            self.event.update(self.res_dict)
            self.event['response_data'] = self.response_data
            print(self.event)
            step_function_name = 'AWS@Shell-NW-SF-Account-No-' + \
                                 self.account_no + '-' + \
                                 str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + \
                                 str(random.randint(1, 100000)) + \
                                 self.event['ResourceProperties']['RequestNo']
            print("Step Function Name:", step_function_name)
            client = boto3.client('stepfunctions')
            response = client.start_execution(
                stateMachineArn='arn:aws:states:us-east-1:{}:stateMachine:platform_Network_Statemachine'. \
                    format(self.resource_properties['AWSAccountId']),
                name=step_function_name,
                input=json.dumps(self.event)
            )
            print(response)
            self.res_dict['invoke_stepfunction'] = SUCCESS
        except Exception as exception:
            print("Error occurred in stepfunction invocation", exception)
            return exception

    def get_business_account(self):
        ''' get business account details from Account_details table'''
        try:
            print("Inside get_business_account")
            response = self.ssm_client.get_parameter(Name="accountDetailTableName")
            account_table = response['Parameter']['Value']
            print(account_table)
            client = boto3.client('dynamodb')
            response = client.get_item(
                TableName=account_table,
                Key={
                    'AccountNumber': {
                        'S': self.account_no}})
            print("Account_Details", response)
            if 'Item' in response:
                self.account_name = response['Item']['AccountName']['S']
                print(self.account_name)
                self.res_dict['business_account'] = self.account_name
                self.response_data['AccountName'] = self.account_name

            else:
                print("Account Number is not valid")
                self.res_dict['business_account'] = FAILED
                self.send(self.event, self.context, FAILED, self.response_data, "Account Number is not valid")
            return self.res_dict['business_account']
        except Exception as exception:
            print("Error occurred in fetching business account", exception)
            return exception

    def verify_update(self):
        '''
        Verfiy if updated parameters are valid
        '''
        try:

            self.res_dict['param_valid'] = "True"
            print("inside verify_update")
            self.res_dict['new_region'] = FALSE
            self.res_dict['vpc_extension'] = FALSE
            old_param = self.event['OldResourceProperties']
            for param in old_param.keys():
                # Checking for parameter update
                if old_param[param] != self.resource_properties[param]:
                    # if request asks for new region set the new_region flag true
                    if old_param[param] == "No-VPC":
                        print(old_param[param])
                        self.res_dict['new_region'] = TRUE
                        continue
                    # if the there is vpc extension request, capture the data
                    elif old_param[param] == "0":
                        self.res_dict['vpc_extension'] = TRUE
                        print(param)
                        self.get_extension_data(param)
                    elif old_param[param] == "":
                        continue
                    # catch unsupported update
                    elif param not in ["RequestNo", "ServiceToken", "UpdateIndex","IsNonroutableSubnets"]:
                        reason_data = "Update not supported.Invalid " + param
                        print(reason_data, old_param[param], self.resource_properties[param])
                        self.res_dict['param_valid'] = FAILED
                        self.send(self.event, self.context, FAILED, self.response_data, reason_data)
            print(self.res_dict)
            return self.res_dict['param_valid']
        except Exception as e:
            print("Error Occurred while validating the parameter update", e)

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
        response_body['PhysicalResourceId'] = event['StackId'] + event['RequestId']
        response_body['StackId'] = event['StackId']
        response_body['RequestId'] = event['RequestId']
        response_body['LogicalResourceId'] = event['LogicalResourceId']
        if response_status == FAILED:
            json_responsebody = json.dumps(response_body)
        else:
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
    Lambda handler that calls the Step functions for the network creation
    '''
    print('event ' + str(event))
    try:
        print("Received a {} Request".format(event['RequestType']))
        if event['RequestType'] == "Create":
            event['new_region'] = TRUE
        network_request_object = NetworkRequest(event, context)
        if network_request_object.get_business_account() == FAILED:
            print("Business account not Valid")
            return network_request_object.res_dict
        if event['RequestType'] == "Update" and network_request_object.verify_update() == FAILED:
            print("Update parameter not Valid")
            network_request_object.send(event, context, FAILED, network_request_object.response_data,
                                        "Update parameter not Valid")
            return network_request_object.res_dict
        if event['RequestType'] == "Delete":
            network_request_object.send(event, context, SUCCESS, network_request_object.response_data, "Deleting")
            return False
        regions = network_request_object.get_region_ip()
        network_request_object.invoke_stepfunction(regions)
        return event
    except Exception as exception:
        print(exception)
