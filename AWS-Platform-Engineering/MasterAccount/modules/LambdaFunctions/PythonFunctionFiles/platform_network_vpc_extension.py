"""
This module is used to extend vpc in the child account
"""

import boto3
import logging
import random

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


class ExtendVPC(object):
    """
    # Class: ExtendVPC
    # Description: Extends VPC with given CIDR range
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        self.CIDR = []
        try:
            self.network_table_name = 'Network_Table'
            self.resource_properties = self.event['ResourceProperties']
            # get relevant input params from event
            self.account_id = self.resource_properties['AccountNumber']
            self.environment = self.resource_properties['Environment']
            self.account_name = event['response_data']['AccountName']

            print("Creating Session and AWS Service Clients")

            session = boto3.session.Session()
            sts_client = session.client('sts')
            ssm_client = session.client('ssm')
            self.dynamodb_client = session.client('dynamodb')

            self.cidr_table_name = ssm_client.get_parameter(Name='cidr_table_name')['Parameter']['Value']
            self.cidr_table_index = ssm_client.get_parameter(Name='cidr_table_index')['Parameter']['Value']

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

    def get_region_vpc(self):

        ''' Get the vpc details for extending the vpc '''
        try:
            for cidr_row in self.event['Extension_data']:
                self.extend_vpc(cidr_row)
                self.update_cidr_table(cidr_row)
                cidr_row['environment'] = self.environment

            print(self.event['Extension_data'])
            self.event['ExtendVPC'] = 'True'
        except Exception as e:
            print("Failed  while fetching VPC and Region or updating extended CIDR range in DynamoDB")

    def extend_vpc(self, cidr_row):
        try:
            child_account_ec2_client = self.assumeRoleSession.client('ec2', region_name=cidr_row['region'])
            cidr_row['association_id_list'] = []
            cidr = cidr_row['cidr']
            vpc_id = cidr_row['vpc_id']
            # Describe vpc to check existing extension
            vpc_response = child_account_ec2_client.describe_vpcs(
                VpcIds=[
                    vpc_id
                ])
            print("VPC response", vpc_response)
            cidr_set = vpc_response['Vpcs'][0]['CidrBlockAssociationSet']
            for association in cidr_set:
                cidr_row['association_id_list'].append(association['AssociationId'])

            cidr_count = len(cidr_set)
            # checks if the number of existing associations for vpc is same as existing extension request
            if cidr_count == list(self.event['ResourceProperties'].values()).count(vpc_id):
                try:
                    response = child_account_ec2_client.associate_vpc_cidr_block(
                        CidrBlock=cidr,
                        VpcId=vpc_id
                    )
                    print(response)
                    cidr_row['association_id'] = response['CidrBlockAssociation']['AssociationId']
                except Exception as e:
                    print("CIDR block associated")
                    fetch_association_id = child_account_ec2_client.describe_vpcs(
                        Filters=[
                            {
                                'Name': 'cidr-block-association.cidr-block ',
                                'Values': [cidr]

                            }
                        ])
                    print(fetch_association_id)
                    cidr_row['association_id'] = fetch_association_id['Vpcs'][0]['CidrBlockAssociationSet'][
                        'AssociationId']
                while True:
                    status_response = child_account_ec2_client.describe_vpcs(
                        Filters=[
                            {
                                'Name': 'cidr-block-association.association-id',
                                'Values': [cidr_row['association_id']]

                            }
                        ])
                    if status_response['Vpcs'][0]['CidrBlockAssociationSet'][0]['CidrBlockState'][
                        'State'] == 'associated':
                        cidr = status_response['Vpcs'][0]['CidrBlockAssociationSet'][0]['CidrBlock']
                        cidr_row['association_id_list'].append(association['AssociationId'])
                        break
                return True
            else:
                print("Association already exists")
                cidr = cidr_set[1]['CidrBlock']
        except Exception as exception:
            print("Association creation failed!!!")
            print(str(exception))
            logger.error(str(exception))
            return False

    def update_cidr_table(self, cidr_row):
        try:
            print("inside cidr update for vpc extension")
            Items = {
                'cidr': {"S": cidr_row['cidr']},
                'available_ips': {"S": cidr_row['available_ips']},
                'is_allocated': {"S": 'TRUE'},
                'region': {"S": cidr_row['region']},
                'consolidated_key': {"S": cidr_row['consolidated_key']},
                'environment': {"S": cidr_row['environment']},
                'account_name': {"S": self.account_name},
                'account_number': {"S": self.account_id},
                'vpc_id': {"S": cidr_row['vpc_id']}
            }
            insert_response = self.dynamodb_client.put_item(
                TableName=self.cidr_table_name,
                Item=Items)
            print("DynamoDB table ", self.cidr_table_name, "updated with Items ", Items)
            print(insert_response)
            print("CIDR Table updated successfully for VPC extension!!!")
            self.event['extension_update_cidr_table'] = TRUE
            return self.event['extension_update_cidr_table']
        except Exception as exception:
            print("DynamoDB Table updation failed!!!")
            print(str(exception))
            logger.error(str(exception))
            self.event['extension_update_cidr_table'] = FALSE


def lambda_handler(event, context):
    '''
    Lambda handler for subnet creation
    '''
    print('event ' + str(event))
    try:
        vpc_extend_object = ExtendVPC(event, context)
        vpc_extend_object.get_region_vpc()
        return event
    except Exception as exception:
        print(exception)
        return exception
