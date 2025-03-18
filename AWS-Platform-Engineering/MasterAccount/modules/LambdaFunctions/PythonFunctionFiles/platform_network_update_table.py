"""
This module is used to update network Table
"""

import json
import boto3
import logging
import random
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

SUCCESS = "SUCCESS"
FAILED = "FAILED"
FALSE = "False"
TRUE = "True"


class UpdateTable(object):
    """
    # Class: UpdateTable
    # Description: Update VPC Table
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)

        self.res_dict = {}
        try:

            self.resource_properties = self.event['ResourceProperties']
            # get relevant input params from event
            self.account_id = self.resource_properties['AccountNumber']
            self.account_name = self.event['response_data']['AccountName']
            self.environment = self.resource_properties['Environment']
            self.response_data = self.event['response_data']
            session = boto3.session.Session()
            ssm_client = session.client('ssm')
            self.dynamodb_client = session.client('dynamodb')
            self.response_data = self.event['response_data']
            self.cidr_table_name = ssm_client.get_parameter(Name='cidr_table_name')['Parameter']['Value']
            self.cidr_table_index = ssm_client.get_parameter(Name='cidr_table_index')['Parameter']['Value']
            self.network_table_name = ssm_client.get_parameter(Name='platform_network_table_name')['Parameter']['Value']

        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))
            raise Exception(str(exception))

    def update_table(self):
        try:

            for cidr_row in self.event['CIDR_List']:
                print(cidr_row)
                subnet_list = ','.join(cidr_row['Subnet_Id_List'])
                query_response = \
                    self.dynamodb_client.query(TableName=self.network_table_name,
                                               Select='ALL_ATTRIBUTES', ConsistentRead=False,
                                               KeyConditionExpression="VPC_Id = :vi",
                                               ExpressionAttributeValues={":vi": {"S": cidr_row['vpc_id']}
                                                                          })
                print(query_response)
                if len(query_response['Items']) == 1:
                    print("It is vpc update")
                    self.get_vpc_details(cidr_row)
                    subnet_list = ','.join(cidr_row['Subnet_Id_List'])
                    cidr_row['cidr'] = ','.join(cidr_row['cidr'])
                    cidr_row['association_list'] = ','.join(cidr_row['association_list'])
                    print(cidr_row)

                else:
                    print("vpc not available")
                if cidr_row['environment'] == 'Public':
                    insert_response = self.dynamodb_client.put_item(
                        TableName=self.network_table_name,
                        Item={
                            'CIDR_List': {"S": cidr_row['cidr']},
                            'Region': {"S": cidr_row['region']},
                            'Subnet_ID_List': {"S": subnet_list},
                            'Environment': {"S": cidr_row['environment']},
                            'AccountName': {"S": self.account_name},
                            'AccountNumber': {"S": self.account_id},
                            'VPC_Id': {"S": cidr_row['vpc_id']},
                            'IGW_Id': {"S": cidr_row['igw_id']}
                        })

                else:
                    insert_response = self.dynamodb_client.put_item(
                        TableName=self.network_table_name,
                        Item={
                            'CIDR_List': {"S": cidr_row['cidr']},
                            'Region': {"S": cidr_row['region']},
                            'Subnet_ID_List': {"S": subnet_list},
                            'Environment': {"S": cidr_row['environment']},
                            'AccountName': {"S": self.account_name},
                            'AccountNumber': {"S": self.account_id},
                            'VPC_Id': {"S": cidr_row['vpc_id']},
                            'Resolver_Association': {"S": cidr_row['association_id']}
                        })
                print(insert_response)
                self.event['Update_Table'] = "True"
        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))
            return exception

    def update_cidr_flag(self):

        ''' Change FLAG to FALSE'''
        try:
            scan_query = self.dynamodb_client.scan(TableName=self.cidr_table_name,
                                                   Select='ALL_ATTRIBUTES', ConsistentRead=False,
                                                   FilterExpression="is_allocated = :ia",
                                                   ExpressionAttributeValues={":ia": {"S": 'FLAG'}})
            print(scan_query)
            for item in scan_query['Items']:
                print(item)
                insert_response = self.dynamodb_client.put_item(
                    TableName=self.cidr_table_name,
                    Item={
                        'cidr': {"S": item['cidr']['S']},
                        'available_ips': {"S": item['available_ips']['S']},
                        'is_allocated': {"S": 'FALSE'},
                        'region': {"S": item['region']['S']},
                        'consolidated_key': {"S": item['consolidated_key']['S']},
                        'environment': {"S": item['environment']['S']}
                    })
            self.event['update_cidr_flag'] = TRUE
        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))
            return exception

    def get_vpc_details(self, cidr_row):

        ''' Get VPC details for update'''
        try:
            vpc_id = cidr_row['vpc_id']
            region = cidr_row['region']
            child_account_role_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))
            sts_client = boto3.client('sts')

            child_account_role_arn = "arn:aws:iam::" + self.account_id + ":role/AWSControlTowerExecution"
            child_account_role_creds = sts_client.assume_role(RoleArn=child_account_role_arn,
                                                              RoleSessionName=child_account_role_session_name)
            credentials = child_account_role_creds.get('Credentials')
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)
            child_account_ec2_client = self.assumeRoleSession.client('ec2', region_name=region)

            # get cidr details
            vpc_response = child_account_ec2_client.describe_vpcs(
                VpcIds=[
                    vpc_id
                ])

            cidr_row['cidr'] = []
            cidr_row['association_list'] = []
            for cidr in vpc_response['Vpcs'][0]['CidrBlockAssociationSet']:
                cidr_row['cidr'].append(cidr['CidrBlock'])
                cidr_row['association_list'].append(cidr['AssociationId'])

            # get subnet details
            subnet_response = child_account_ec2_client.describe_subnets(
                Filters=[
                    {
                        'Name': 'vpc-id',
                        'Values': [
                            vpc_id
                        ]
                    }
                ]
            )
            cidr_row['Subnet_Id_List'] = []
            for subnet in subnet_response['Subnets']:
                cidr_row['Subnet_Id_List'].append(subnet['SubnetId'])
            print("Latest details", cidr_row)
            self.event['vpc_details'] = TRUE
        except Exception as e:
            print(e)

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
    Lambda handler calls the function that updates Network Table
    """
    try:
        update_table_obj = UpdateTable(event, context)
        update_table_obj.update_table()
        update_table_obj.update_cidr_flag()
        print(event)
        update_table_obj.send(event, context, SUCCESS, event['response_data'], "VPC Update Completed")
        return event
    except Exception as exception:
        logger.error(str(exception))
