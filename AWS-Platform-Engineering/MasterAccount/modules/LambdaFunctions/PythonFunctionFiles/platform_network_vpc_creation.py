"""
This module is used to Provision VPC in the child account
"""
import json
import random
import boto3
import logging
import os
import time
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

child_account_role_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))
TRUE = "TRUE"
FALSE = "FALSE"

SUCCESS = "SUCCESS"
FAILED = "FAILED"


class VPCProvision(object):
    """
    # Class: VPCProvision
    # Description: Provisions VPC in the child account
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        self.result = {}
        try:

            self.resource_properties = self.event['ResourceProperties']
            # get relevant input params from event
            self.account_id = self.resource_properties['AccountNumber']
            self.regions = list(self.event['region_ip_dict'].keys())
            self.environment = self.resource_properties['Environment']
            self.account_name = event['response_data']['AccountName']

            print("Creating Session and AWS Service Clients")

            session = boto3.session.Session()
            sts_client = session.client('sts')
            ssm_client = session.client('ssm')
            self.dynamodb_client = session.client('dynamodb')

            self.cidr_table_name = ssm_client.get_parameter(Name='cidr_table_name')['Parameter']['Value']
            self.cidr_table_index = ssm_client.get_parameter(Name='cidr_table_index')['Parameter']['Value']
            self.vpc_flowlog_bucket = 'arn:aws:s3:::platform-da2-central-vpcflowlogs-' + os.environ['env']

            child_account_role_arn = "arn:aws:iam::" + self.account_id + ":role/AWSControlTowerExecution"
            child_account_role_creds = sts_client.assume_role(RoleArn=child_account_role_arn,
                                                              RoleSessionName=child_account_role_session_name)
            credentials = child_account_role_creds.get('Credentials')
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)

        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))
            raise Exception(str(exception))

    def create_vpc_in_child_account(self):
        try:
            cidr_list = self.event['CIDR_List']
            vpc_id = ""
            print(self.event)
            print(cidr_list)
            for cidr_row in cidr_list:
                cidr = cidr_row['cidr']
                child_account_ec2_client = self.assumeRoleSession.client('ec2',
                                                                         region_name=cidr_row['region'])

                vpc_response = child_account_ec2_client.describe_vpcs(
                    Filters=[
                        {
                            'Name': 'tag:Name',
                            'Values': ['platform-VPC']
                        }
                    ]
                )
                print(vpc_response)
                if len(vpc_response['Vpcs']) > 0:
                    vpc_id = vpc_response['Vpcs'][0]['VpcId']
                    cidr_row['cidr'] = vpc_response['Vpcs'][0]['CidrBlock']
                    # Enabling VPC flow log for existing VPC may required in migration
                    self.enable_vpc_flowlogs(child_account_ec2_client, vpc_id)
                    logger.info("VPC already present. Hence skipping VPC Provision...")
                else:
                    print(cidr)
                    vpc_response = child_account_ec2_client.create_vpc(
                        CidrBlock=cidr,
                        TagSpecifications=[
                            {
                                'ResourceType': 'vpc',
                                'Tags': [
                                    {
                                        'Key': 'Name',
                                        'Value': 'platform-VPC'
                                    },
                                    {
                                        'Key': 'platform_donotdelete',
                                        'Value': 'yes'
                                    }
                                ]
                            }])
                    vpc_id = vpc_response['Vpc']['VpcId']
                    print(vpc_id)
                    self.check_vpc_status(cidr, vpc_id, child_account_ec2_client, cidr_row)
                cidr_row['vpc_id'] = vpc_id
                self.event['vpc_status'] = TRUE
            print(self.event)
            return self.event['vpc_status']

        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))
            self.event['vpc_status'] = FALSE
            raise RuntimeError('VPC creation failed' + str(exception))

    def check_vpc_status(self, cidr, vpc_id, child_account_ec2_client, cidr_row):
        while True:
            time.sleep(5)
            try:
                vpc_response = child_account_ec2_client.describe_vpcs(
                    VpcIds=[vpc_id]
                )
                if vpc_response['Vpcs'][0]['State'] == 'available':
                    if vpc_response['Vpcs'][0]['CidrBlock'] == cidr:
                        print("Updating CIDR Table")
                        self.update_cidr_table(cidr_row, vpc_id)
                        self.enable_vpc_flowlogs(child_account_ec2_client, vpc_id)
                        cidr_row['is_allocated'] = TRUE
                        break
                    else:
                        self.enable_vpc_flowlogs(child_account_ec2_client, vpc_id)
                        break
            except Exception as exception:
                print(str(exception))

    def enable_vpc_flowlogs(self, ec2_client, vpc_id):
        try:
            print("Inside the enable VPC flow logs function!!!")
            print(vpc_id)
            vpc_fl_response = ec2_client.describe_flow_logs(
                Filters=[
                    {
                        'Name': 'resource-id',
                        'Values': [vpc_id]
                    },
                ],
            )
            if len(vpc_fl_response['FlowLogs']) > 0:
                print(vpc_fl_response)
                print("VPC Flow Logs already created. Hence skipping!!!")
                self.event['vpc_flowlog'] = TRUE
                return
            else:
                vpc_fl_create_response = ec2_client.create_flow_logs(
                    ResourceIds=[vpc_id],
                    ResourceType='VPC',
                    TrafficType='ALL',
                    LogDestinationType='s3',
                    LogDestination=self.vpc_flowlog_bucket
                )
                print("VPC Flow Logs created successfully with response: {}".format(vpc_fl_create_response))
            self.event['vpc_flowlog'] = TRUE
        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))

    def update_cidr_table(self, cidr_row, vpc_id):
        try:
            print("inside update")
            insert_response = self.dynamodb_client.put_item(
                TableName=self.cidr_table_name,
                Item={
                    'cidr': {"S": cidr_row['cidr']},
                    'available_ips': {"S": cidr_row['available_ips']},
                    'is_allocated': {"S": 'TRUE'},
                    'region': {"S": cidr_row['region']},
                    'consolidated_key': {"S": cidr_row['consolidated_key']},
                    'environment': {"S": cidr_row['environment']},
                    'account_name': {"S": self.account_name},
                    'account_number': {"S": self.account_id},
                    'vpc_id': {"S": vpc_id}
                })

            print(insert_response)
            print("CIDR Table updated successfully!!!")
            self.event['update_cidr_table'] = TRUE
            return self.event['update_cidr_table']
        except Exception as exception:
            print("DynamoDB Table updation failed!!!")
            print(str(exception))
            logger.error(str(exception))
            self.event['update_cidr_table'] = FALSE

    def update_provisioned_product(self):

        """Update the network provision product with vpc"""
        try:
            print("Inside update network provision")
            for cidr_row in self.event['CIDR_List']:
                if cidr_row['region'] == 'us-east-1':
                    self.event['response_data']['NVirginiaVPC'] = cidr_row['vpc_id']
                elif cidr_row['region'] == 'eu-west-1':
                    self.event['response_data']['IrelandVPC'] = cidr_row['vpc_id']
            self.send(self.event, self.context, SUCCESS, self.event['response_data'], "VPC Creation Completed")
            print("Provisioned Product updated successfully")
            self.event['update_provisioned_product'] = TRUE
        except Exception as exception:
            print("Provisioned Product update Failed!!!")
            print(str(exception))
            logger.error(str(exception))
            self.event['update_provisioned_product'] = FALSE
            raise RuntimeError('Provisioned Product update Failed!!!' + str(exception))

    def send(self, event, context, response_status, response_data, reason_data):
        """
        Send status to the cloudFormation
        Template.
        """
        print("Inside send method")
        response_url = event['ResponseURL']

        response_body = {}
        response_body['Status'] = response_status
        response_body['Reason'] = reason_data + ' See the details in CloudWatch Log Stream: ' + context.log_stream_name
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
    """
    Lambda handler calls the function that provisions the vpc in the child account
    """
    try:
        vpc_provision_obj = VPCProvision(event, context)
        vpc_provision_obj.create_vpc_in_child_account()
        vpc_provision_obj.update_provisioned_product()
        return event
    except Exception as exception:
        logger.error(str(exception))
        print(str(exception))
