"""
This module is used to update network Table
"""

import json
import boto3
import random
import sys

class UpdateNetworkDynamoDBTable(object):
    """
    # Class: UpdateTable
    # Description: Update VPC Table
    """

    def __init__(self, event):
        self.event = event
        try:
            self.account_id = self.event['ProvisionedProduct']['AccountNumber']
            self.account_name = self.event['ProvisionedProduct']['Name']
            self.environment = self.event['ProvisionedProduct']['OU']
            self.request_type = self.event['RequestType']
            session = boto3.session.Session()
            ssm_client = session.client('ssm')
            self.dynamodb_client = session.client('dynamodb')
            self.cidr_table_name = ssm_client.get_parameter(Name='cidr_table_name')['Parameter']['Value']
            self.cidr_table_index = ssm_client.get_parameter(Name='cidr_table_index')['Parameter']['Value']
            self.network_table_name = ssm_client.get_parameter(Name='platform_network_table_name')['Parameter']['Value']
            child_account_role_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))
            sts_client = boto3.client('sts')
            child_account_role_arn = "arn:aws:iam::" + self.account_id + ":role/AWSControlTowerExecution"
            child_account_role_creds = sts_client.assume_role(RoleArn=child_account_role_arn, RoleSessionName=child_account_role_session_name)
            credentials = child_account_role_creds.get('Credentials')
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)
            self.regions = [item for item in self.event['RegionIpDictionary'] if self.event['RegionIpDictionary'][item] != "No-VPC"]
        except Exception as exception:
            print(str(exception))
            raise Exception(str(exception))

    def update_table(self, region):
        try:
            if self.request_type == "Create" or self.request_type == "Update" :
                Account_Status_Value = "ACTIVE"
            elif self.request_type == "Delete" :
                Account_Status_Value = "SUSPENDED"
            else:
                Account_Status_Value = "NA"
            vpc_cidr_list = ','.join(self.vpc_cidr) 
            subnet_list = ','.join(self.subnet_cidr) 
            resolver_association = ','.join(self.resolver_association_list)
            insert_response = self.dynamodb_client.put_item(
                    TableName=self.network_table_name,
                    Item={
                        'CIDR_List': {"S": vpc_cidr_list},
                        'Region': {"S": region},
                        'Subnet_ID_List': {"S": subnet_list},
                        'Environment': {"S": self.environment},
                        'AccountName': {"S": self.account_name},
                        'AccountNumber': {"S": self.account_id},
                        'VPC_Id': {"S": self.vpc_id},
                        'Resolver_Association': {"S": resolver_association},
                        'Account_Status': {"S": Account_Status_Value}
                    })
            print(insert_response)
            return True
        except Exception as exception:
            print(str(exception))
            return False

    def update_cidr_flag(self, event):

        ''' Change FLAG to FALSE'''
        try:
            scan_query = self.dynamodb_client.scan(TableName=self.cidr_table_name,
                                                Select='ALL_ATTRIBUTES', ConsistentRead=False,
                                                FilterExpression="is_allocated = :ia",
                                                ExpressionAttributeValues={":ia": {"S": 'FLAG'}})
            print(scan_query)
            for item in scan_query['Items']:
                print(item)
                for region in self.regions:
                    regionkey =  "us" if region == "us-east-1" else ("eu" if region == "eu-west-1" else ("sg" if region == "ap-southeast-1" else "NA"))
                    RegionIpDictionary = "RegionIpDictionary_"+regionkey.upper()
                    if item['cidr']['S'].strip() in event[RegionIpDictionary][region].values():
                        insert_response = self.dynamodb_client.put_item(
                            TableName=self.cidr_table_name,
                            Item={
                                'cidr': {"S": item['cidr']['S']},
                                'available_ips': {"S": item['available_ips']['S']},
                                'is_allocated': {"S": 'TRUE'},
                                'region': {"S": item['region']['S']},
                                'consolidated_key': {"S": item['consolidated_key']['S']},
                                'environment': {"S": item['environment']['S']},
                                'account_name' :{"S": self.account_name},
                                'account_number' :{"S": self.account_id}
                            })
                        print("Update CIDR table successfully", insert_response)
            return True
        except Exception as exception:
            print(str(exception))
            return False

    def get_vpc_details(self):

        ''' Get VPC details for update'''
        try:
            for region in self.regions:
                Flag = 0
                child_account_ec2_client = self.assumeRoleSession.client('ec2', region_name=region)
                resolver_client = self.assumeRoleSession.client('route53resolver', region_name =region)
                vpc_response = child_account_ec2_client.describe_vpcs(
                    Filters=[
                        {
                            'Name': 'tag:Name',
                            'Values': ['platform-VPC']
                        }
                    ])
                print(vpc_response)
                if len(vpc_response['Vpcs']) > 0:
                    self.vpc_id = vpc_response['Vpcs'][0]['VpcId']
                    self.vpc_cidr = []
                    cidr_response = vpc_response['Vpcs'][0]['CidrBlockAssociationSet']
                    for item in cidr_response:
                        self.vpc_cidr.append(item['CidrBlock'])
                    print(self.vpc_cidr)
                    print("platform-VPC - {}".format(self.vpc_id))
                else:
                    print("No platform-VPC - {} available".format(self.vpc_id))
                    Flag +=1

                subnet_response = child_account_ec2_client.describe_subnets(
                    Filters=[
                        {
                            'Name': 'vpc-id',
                            'Values': [
                                self.vpc_id 
                            ]
                        }
                    ]
                )
                if len(subnet_response['Subnets']) > 0:
                    self.subnet_cidr = []
                    for item in subnet_response['Subnets']:
                       self.subnet_cidr.append(item['CidrBlock'])
                    print(self.subnet_cidr)
                else:
                    print("No platform-VPC Subnet - {} available".format(self.vpc_id))
                    Flag +=1

                list_associations = resolver_client.list_resolver_rule_associations(
                        Filters=[
                            {
                            'Name': 'Name',
                            'Values': [
                                'platform_ResolverRuleAssociation'
                            ]
                            }])
                if len(list_associations['ResolverRuleAssociations']) > 0:
                    self.resolver_association_list = []
                    for item in list_associations['ResolverRuleAssociations']:
                       self.resolver_association_list.append(item['Id'])
                    print(self.resolver_association_list)
                else:
                    print("No platform-VPC Subnet - {} available".format(self.vpc_id))
                    Flag +=1
                if Flag == 0:
                    self.update_table(region)
            return True
        except Exception as e:
            print("Exception occured in get VPC details", e)
            return False

try:
    local_file_path = str(sys.argv[1])+"parameters.json"
    print("Parameters local file path: ", local_file_path)
    with open(local_file_path) as json_data:
        parameters_data = json.load(json_data)
    print(parameters_data)
    if parameters_data : 
        print("parameters are loaded in json format, invokes UpdateNetworkDynamoDBTable function..")
        NWTable = UpdateNetworkDynamoDBTable(parameters_data)
        if NWTable.get_vpc_details():
            print("Network Details Table Updated is successfully ..!!")
        else:
            print("Network Details Table Updated is  fialed..!!")
        if NWTable.update_cidr_flag(parameters_data):
            print("Network CIDR Table Updated is successfully ..!!")
        else:
            print("Network CIDR Table Updated is  fialed..!!")
except Exception as ex:
    print("There is an error in UpdateNetworkDynamoDBTable %s", str(ex))
