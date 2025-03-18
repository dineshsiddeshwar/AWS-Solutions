"""
This module is used to Provision Subnet in the child account
"""

import boto3
import ipaddress
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


class SubnetProvision(object):
    """
    # Class: SubnetProvision
    # Description: Provisions Subnet in the child account in the specified VPC
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        self.CIDR = []
        try:

            self.resource_properties = self.event['ResourceProperties']
            # get relevant input params from event
            self.account_id = self.resource_properties['AccountNumber']
            self.regions = list(self.event['region_ip_dict'].keys())
            self.region_ip_dict = self.event['region_ip_dict']
            if self.regions == None:
                raise Exception("Region List cannot be none")
            print(self.regions)
            self.environment = self.resource_properties['Environment']

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

        ''' Get the vpc details for creating Subnets '''
        try:
            for cidr_row in self.event['CIDR_List']:
                cidr_row = self.create_subnets_and_update_table(cidr_row)
                print(self.event['CIDR_List'])
            for ext_row in self.event['Extension_data']:
                ext_row = self.create_subnets_and_update_table(ext_row)
            print(self.event['Extension_data'])
        except Exception as e:
            print("Subnet creation failed in while fetching VPC and Region")

    def create_subnets_and_update_table(self, cidr_row):
        try:
            cidr = cidr_row['cidr']
            subnet_id_list = []
            vpc_id = cidr_row['vpc_id']
            # Get availabilty zone for the region
            print(cidr_row['region'])
            child_account_ec2_client = self.assumeRoleSession.client('ec2', region_name=cidr_row['region'])
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
                if zone['ZoneName'].endswith('a') or zone['ZoneName'].endswith('b'):
                    zone_list.append(zone['ZoneName'])
                    print(zone['ZoneName'])
                    count += 1
                    if count > 2:
                        break
            
            # break the cidr into two for "Hybrid"
            #ipaddress.ip_network(cidr).subnets()
            if self.environment == 'Hybrid':

                subnet_list = list(ipaddress.ip_network(cidr).subnets(prefixlen_diff=2))
                count = 0
                print(subnet_list)
                for subnet in subnet_list:
                    try:
                        if count in [0,1]:
                            HybridSubnetNames = "platform-public-subnet-"+str(1+count)
                            zone = count
                        
                        if count in [2,3]:
                            HybridSubnetNames = "platform-private-subnet-"+str(count-1)
                            zone = count-2

                        print(zone_list[zone], str(subnet))
                        subnet_response = child_account_ec2_client.create_subnet(
                            AvailabilityZone=zone_list[zone],
                            CidrBlock=str(subnet),
                            VpcId=vpc_id,
                            TagSpecifications=[
                                {
                                    'ResourceType': 'subnet',
                                    'Tags': [
                                        {
                                            'Key': 'Name',
                                            'Value': HybridSubnetNames
                                        },
                                        {
                                            'Key': 'platform_donotdelete',
                                            'Value': 'yes'
                                        }
                                    ]
                                }]
                        )
                        print(subnet_response)
                        subnet_id_list.append(subnet_response['Subnet']['SubnetId'])
                        count += 1

                    except Exception as e:

                        print("Subnet already exists:", e)
                        fetch_subnet_id = child_account_ec2_client.describe_subnets(
                            Filters=[
                                {
                                    'Name': 'cidr-block',
                                    'Values': [str(subnet)]

                                }
                            ])
                        print(fetch_subnet_id)
                        subnet_id_list.append(fetch_subnet_id['Subnets'][0]['SubnetId'])
                cidr_row['Subnet_Id_List'] = subnet_id_list
                print(cidr_row)
                return cidr_row
                
            elif self.environment == 'Private':

                subnet_list = list(ipaddress.ip_network(cidr).subnets())
                count = 0
                print(subnet_list)
                for subnet in subnet_list:
                    try:
                        if count in [0,1]:
                            privatesubnetName = "platform-private-subnet-"+str(1+count)
                        print(zone_list[count], str(subnet))
                        subnet_response = child_account_ec2_client.create_subnet(
                            AvailabilityZone=zone_list[count],
                            CidrBlock=str(subnet),
                            VpcId=vpc_id,
                            TagSpecifications=[
                                {
                                    'ResourceType': 'subnet',
                                    'Tags': [
                                        {
                                            'Key': 'Name',
                                            'Value': privatesubnetName
                                        },
                                        {
                                            'Key': 'platform_donotdelete',
                                            'Value': 'yes'
                                        }
                                    ]
                                }]
                        )
                        print(subnet_response)
                        subnet_id_list.append(subnet_response['Subnet']['SubnetId'])
                        count += 1

                    except Exception as e:

                        print("Subnet already exists:", e)
                        fetch_subnet_id = child_account_ec2_client.describe_subnets(
                            Filters=[
                                {
                                    'Name': 'cidr-block',
                                    'Values': [str(subnet)]

                                }
                            ])
                        print(fetch_subnet_id)
                        subnet_id_list.append(fetch_subnet_id['Subnets'][0]['SubnetId'])
                cidr_row['Subnet_Id_List'] = subnet_id_list
                print(cidr_row)
                return cidr_row

            else:
                return False

        except Exception as exception:

            print("VPC subnets creation failed!!!")
            print(str(exception))
            logger.error(str(exception))
            return False


def lambda_handler(event, context):
    '''
    Lambda handler for subnet creation
    '''
    print('event ' + str(event))
    try:

        subnet_provision_object = SubnetProvision(event, context)
        subnet_provision_object.get_region_vpc()
        return event
    except Exception as exception:
        print(exception)
        return exception