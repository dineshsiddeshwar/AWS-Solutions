"""
This module is used to create and attach IGW in the child account
"""

import random
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

child_account_role_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))


class EnableIGW(object):
    """
    # Class: EnableIGW
    # Description: creates and attaches
    """

    def __init__(self, event, context):
        self.event = event
        self.resource_properties = self.event['ResourceProperties']
        # get relevant input params from event
        self.account_id = self.resource_properties['AccountNumber']
        sts_client = boto3.client('sts')
        child_account_role_arn = "arn:aws:iam::" + self.account_id + ":role/AWSControlTowerExecution"
        child_account_role_creds = sts_client.assume_role(RoleArn=child_account_role_arn,
                                                          RoleSessionName=child_account_role_session_name)
        credentials = child_account_role_creds.get('Credentials')
        accessKeyID = credentials.get('AccessKeyId')
        secretAccessKey = credentials.get('SecretAccessKey')
        sessionToken = credentials.get('SessionToken')
        self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)

    def enable_igw_for_public(self, cidr_row):
        try:

            """
            The below section creates an IGW, attaches it to the VPC and then 
            creates a default route to IGW in the vpc subnet 
            """
            child_account_ec2_client = self.assumeRoleSession.client('ec2', region_name=cidr_row['region'])
            igw_response = child_account_ec2_client.describe_internet_gateways()
            print(igw_response)
            if len(igw_response['InternetGateways']) > 0:
                print("Internet Gateway already present. Hence skipping!!!")
                cidr_row['igw_id'] = igw_response['InternetGateways'][0]['InternetGatewayId']
                attachment_status = igw_response['InternetGateways'][0]['Attachments'][0]['State']
                if attachment_status == 'attached':
                    return True
            else:
                cidr_row['igw_id'] = child_account_ec2_client.create_internet_gateway(
                    TagSpecifications=[
                        {
                            'ResourceType': 'internet-gateway',
                            'Tags': [
                                {
                                    'Key': 'Name',
                                    'Value': 'platform-IGW'
                                },
                                {
                                    'Key': 'platform_donotdelete',
                                    'Value': 'yes'
                                }
                            ]
                        }])['InternetGateway']['InternetGatewayId']
                print("Internet Gateway {} created successfully!!!".format(cidr_row['igw_id']))

                igw_attach_response = child_account_ec2_client.attach_internet_gateway(
                    InternetGatewayId=cidr_row['igw_id'],
                    VpcId=cidr_row['vpc_id'])
                print("Internet Gateway Attachment Response: {}".format(igw_attach_response))

                rtb_response = child_account_ec2_client.describe_route_tables(
                    Filters=[
                        {
                            'Name': 'vpc-id',
                            'Values': [cidr_row['vpc_id']]
                        },
                    ]
                )

                rtb_id = rtb_response['RouteTables'][0]['RouteTableId']
                rtb_update_response = child_account_ec2_client.create_route(
                    DestinationCidrBlock='0.0.0.0/0',
                    GatewayId=cidr_row['igw_id'],
                    RouteTableId=rtb_id)
                print("Route Creation Response: {}".format(rtb_update_response))

        except Exception as exception:
            print("IGW  for public environment failed!!!")
            print(str(exception))
            logger.error(str(exception))


def lambda_handler(event, context):
    """
    Lambda handler calls the function that provisions the vpc in the child account
    """
    try:
        igw_obj = EnableIGW(event, context)
        for cidr_row in event['CIDR_List']:
            igw_obj.enable_igw_for_public(cidr_row)
        return event
    except Exception as exception:
        logger.error(str(exception))
        print(str(exception))

