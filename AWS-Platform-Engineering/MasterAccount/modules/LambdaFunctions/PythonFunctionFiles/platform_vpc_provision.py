"""
This module is used to Provision VPC in the child account
"""

import random
import boto3
import logging
import ipaddress
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

master_admin_role_session_name = "AuditAdminSession-" + str(random.randint(1, 100000))
child_account_role_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))

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
        self.CIDR = []
        try:

            self.ResourceProperties = self.event['ResourceProperties']
            # get relevant input params from event
            self.account_id = event['accountNumber']
            selected_regions = self.ResourceProperties['Region']

            print(selected_regions)
            if selected_regions != None:
                # list(map(lambda s: s.strip(), selected_regions.split(",")))
                self.regions = list(map(lambda s: s.strip(), selected_regions.split(",")))
            else:
                raise Exception("Region List cannot be none")

            print(self.regions)
            self.environment = self.ResourceProperties['AccountType']
            self.required_ips = self.ResourceProperties['IpSize']

            self.is_allocated = "FALSE"
            self.cidr_row = {}
            self.consolidated_keys = []
            for region in self.regions:
                consolidated_key = self.required_ips + "|" + region + "|" + self.environment
                print(consolidated_key)
                self.consolidated_keys.append(consolidated_key)

            print("Creating Session and AWS Service Clients")

            session = boto3.session.Session()
            sts_client = session.client('sts')
            ssm_client = session.client('ssm')
            self.master_admin_role_arn = ssm_client.get_parameter(Name='master_admin_role_arn')['Parameter']['Value']
            self.cidr_table_name = ssm_client.get_parameter(Name='cidr_table_name')['Parameter']['Value']
            self.cidr_table_index = ssm_client.get_parameter(Name='cidr_table_index')['Parameter']['Value']

            master_admin_role_creds = sts_client.assume_role(RoleArn=self.master_admin_role_arn,
                                                             RoleSessionName=master_admin_role_session_name)
            credentials = master_admin_role_creds.get('Credentials')
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)

            self.master_account_dynamodb_client = assumeRoleSession.client('dynamodb')
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
            raise Exception (str(exception))

    def fetch_cidr(self):
        try:
            cidr_list = []
            count = 0
            for key in self.consolidated_keys:
                queryResponse = \
                    self.master_account_dynamodb_client.query(TableName=self.cidr_table_name,
                      IndexName=self.cidr_table_index,
                      Select='ALL_PROJECTED_ATTRIBUTES', ConsistentRead=False,
                      KeyConditionExpression="consolidated_key = :ck AND is_allocated = :ia",
                      ExpressionAttributeValues={":ck": {"S": key},
                                                 ":ia": {"S": self.is_allocated}})

                if len(queryResponse['Items']) < 1:
                    print("No free CIDR ranges available to provision the VPC")
                    print("VPC creation process will fail")
                    return Exception
                cidr_row = {
                    'cidr': queryResponse['Items'][0]['cidr']['S'],
                    'available_ips': queryResponse['Items'][0]['available_ips']['S'],
                    'is_allocated': queryResponse['Items'][0]['is_allocated']['S'],
                    'region': queryResponse['Items'][0]['region']['S'],
                    'consolidated_key': queryResponse['Items'][0]['consolidated_key']['S'],
                    'environment': queryResponse['Items'][0]['environment']['S']
                }
                cidr_list.append(cidr_row)
            return cidr_list
        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))
            return exception

    def enable_igw_for_public(self,child_account_ec2_client,vpc_id):
        try:
            if self.environment == 'public':
                """
                The below section creates an IGW, attaches it to the VPC and then 
                creates a default route to IGW in the vpc subnet 
                """

                igw_response = child_account_ec2_client.describe_internet_gateways()
                if len(igw_response['InternetGateways']) > 0:
                    print("Internet Gateway already present. Hence skipping!!!")
                    return True
                else:
                    igw_id = child_account_ec2_client.create_internet_gateway()['InternetGateway']['InternetGatewayId']
                    print("Internet Gateway {} created successfully!!!".format(igw_id))

                igw_attach_response = child_account_ec2_client.attach_internet_gateway(
                    InternetGatewayId=igw_id,
                    VpcId=vpc_id)
                print("Internet Gateway Attachment Response: {}".format(igw_attach_response))

                rtb_response = child_account_ec2_client.describe_route_tables(
                    Filters=[
                        {
                            'Name': 'vpc-id',
                            'Values': [vpc_id]
                        },
                    ]
                )
                rtb_id = rtb_response['RouteTables'][0]['RouteTableId']
                rtb_update_response = child_account_ec2_client.create_route(
                    DestinationCidrBlock='0.0.0.0/0',
                    GatewayId=igw_id,
                    RouteTableId=rtb_id)
                print("Route Creation Response: {}".format(rtb_update_response))
                return True
            else:
                return False
        except Exception as exception:
            print("VPC configuration for public environment failed!!!")
            print(str(exception))
            logger.error(str(exception))
            return False

    def create_subnets_and_update_table(self,cidr_row,cidr,child_account_ec2_client,vpc_id):
        try:
            print("Starting to update CIDR DynamoDB Table...")
            self.update_cidr_table(cidr_row)

            print("Starting to enable VPC Flowlogs...")
            self.enable_vpc_flowlogs(child_account_ec2_client, vpc_id)

            az_response = child_account_ec2_client.describe_availability_zones(
                Filters=[
                    {
                        'Name': 'region-name',
                        'Values': [cidr_row['region']]
                    },
                ]
            )
            zone_list = []
            count = 1
            for zone in az_response['AvailabilityZones']:
                zone_list.append(zone['ZoneName'])
                print(zone['ZoneName'])
                count += 1
                if count > 2:
                    break

            ipaddress.ip_network(cidr).subnets()
            subnet_list = list(ipaddress.ip_network(cidr).subnets())
            count = 0
            for subnet in subnet_list:
                subnet_response = child_account_ec2_client.create_subnet(
                    AvailabilityZone=zone_list[count],
                    CidrBlock=str(subnet),
                    VpcId=vpc_id
                )
                print(subnet_response)
                count += 1
            return True
        except Exception as exception:
            print("VPC subnets creation failed!!!")
            print(str(exception))
            logger.error(str(exception))
            return False

    def create_vpc_in_child_account(self):
        try:
            cidr_list = self.fetch_cidr()
            igw_status_list = []
            subnets_status_list = []
            cidr_status_list = []

            # print (cidr_list)
            for cidr_row in cidr_list:
                try:
                    cidr = cidr_row['cidr']
                    child_account_ec2_client = self.assumeRoleSession.client('ec2',
                                                                             region_name=cidr_row['region'])

                    vpc_response = child_account_ec2_client.describe_vpcs()
                    # print (vpc_response)
                    if len(vpc_response['Vpcs']) > 0:
                        logger.info("VPC already present. Hence skipping VPC Provision...")
                        cidr_status_list.append(True)
                        subnets_status_list.append(True)
                        if (self.environment == "public"):
                            igw_status_list.append(True)
                        else:
                            igw_status_list.append(False)
                        continue

                    print(cidr)
                    vpc_response = child_account_ec2_client.create_vpc(
                        CidrBlock=cidr
                    )
                    vpc_id = vpc_response['Vpc']['VpcId']

                    while True:
                        vpc_response = child_account_ec2_client.describe_vpcs(
                            VpcIds=[vpc_id]
                        )
                        if vpc_response['Vpcs'][0]['State'] == 'available':
                            break
                        time.sleep(5)

                    print(vpc_response)

                    output = {
                        'cidr': cidr,
                        'region': cidr_row['region']
                    }
                    self.CIDR.append(output)
                    cidr_status_list.append(True)

                    subnets_status = self.create_subnets_and_update_table(cidr_row, cidr, child_account_ec2_client,
                                                                          vpc_id)
                    subnets_status_list.append(subnets_status)

                    igw_status = self.enable_igw_for_public(child_account_ec2_client, vpc_id)
                    igw_status_list.append(igw_status)

                except Exception as exception:
                    print("VPC creation failed!!!")
                    print(str(exception))
                    logger.error(str(exception))
                    cidr_status_list.append(True)

            vpc_provison_status = {}
            vpc_provison_status['vpc_status'] = cidr_status_list
            vpc_provison_status['subnets_status'] = subnets_status_list
            vpc_provison_status['igw_status'] = igw_status_list
            return vpc_provison_status
        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))

            vpc_provison_status = {}
            vpc_provison_status['vpc_status'] = [False]
            vpc_provison_status['subnets_status'] = [False]
            vpc_provison_status['igw_status'] = [False]
            return vpc_provison_status

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
                return
            else:
                vpc_fl_create_response = ec2_client.create_flow_logs(
                        ResourceIds=[vpc_id],
                        ResourceType='VPC',
                        TrafficType='ALL',
                        LogDestinationType='s3',
                        LogDestination='arn:aws:s3:::platform-da2-central-vpcflowlogs-dev/'
                    )
                print("VPC Flow Logs created successfully with response: {}".format(vpc_fl_create_response))
        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))
            return Exception("VPC Flow Logs creation failed!!!")

    def update_cidr_table(self, cidr_row):
        try:
            insert_response = self.master_account_dynamodb_client.put_item(
                TableName=self.cidr_table_name,
                Item={
                    'cidr': {"S": cidr_row['cidr']},
                    'available_ips': {"S": cidr_row['available_ips']},
                    'is_allocated': {"S": 'TRUE'},
                    'region': {"S": cidr_row['region']},
                    'consolidated_key': {"S": cidr_row['consolidated_key']},
                    'environment': {"S": cidr_row['environment']}
                })

            print(insert_response)
            print("CIDR Table updated successfully!!!")

        except Exception as exception:
            print("DynamoDB Table updation failed!!!")
            print(str(exception))
            logger.error(str(exception))
            return exception

def lambda_handler(event, context):
    """
    Lambda handler calls the function that provisions the vpc in the child account
    """
    try:
        vpc_provision_obj = VPCProvision(event, context)
        vpc_provison_status = vpc_provision_obj.create_vpc_in_child_account()
        event['CIDR'] = vpc_provision_obj.CIDR
        event['vpc_provison_status'] = vpc_provison_status
        return event
    except Exception as exception:
        logger.error(str(exception))
        event['CIDR'] = []
        vpc_provison_status = {}
        vpc_provison_status['vpc_status'] = [False]
        vpc_provison_status['subnets_status'] = [False]
        vpc_provison_status['igw_status'] = [False]
        event['vpc_provison_status'] = vpc_provison_status
        return event