"""
This module is used to create NAT,RouteTables and Nonroutable subnet creation
"""

import boto3
import logging
import time
import json
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
print(child_account_role_session_name)
TRUE = "TRUE"
FALSE = "FALSE"
FAILED = "FAILED"
SUCCESS = "SUCCESS"

class NATGateway_nonroutable(object):
    """
    # Class: NATGateway_nonroutable
    # Description: Creates nonroutables subnets, nat gateway, route tables, associate the route table with subnets, create a default route
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        logger.info("Getting relevant input params from event")
        self.account_id = self.event['ResourceProperties']['AccountNumber']
        print(self.account_id)
        self.IsNonroutableSubnets = event['ResourceProperties']['IsNonroutableSubnets']
        print(self.IsNonroutableSubnets)
        try:
            self.resource_properties = self.event['ResourceProperties']
            print("Creating Session and AWS Service Clients")
            session = boto3.session.Session()
            sts_client = session.client('sts')
            ssm_client = session.client('ssm')
            self.environment = self.event['ResourceProperties']['Environment']
            self.regions = list(self.event['region_ip_dict'].keys())
            if self.regions == None:
                raise Exception("Region List cannot be none")
            print(self.regions)
            child_account_role_arn = "arn:aws:iam::" + self.account_id + ":role/AWSControlTowerExecution"
            print(child_account_role_arn)
            child_account_role_creds = sts_client.assume_role(RoleArn=child_account_role_arn,
                                                              RoleSessionName=child_account_role_session_name)
            print(child_account_role_creds)
            credentials = child_account_role_creds.get('Credentials')
            print(credentials)
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)
            print(self.assumeRoleSession)
            self.NonRoutableCIDR = ssm_client.get_parameter(Name='NonRoutableCIDR')['Parameter']['Value']
            self.NonRoutableSubnetaz1 = ssm_client.get_parameter(Name='NonRoutableSubnetAZ1')['Parameter']['Value']
            self.NonRoutableSubnetaz2 = ssm_client.get_parameter(Name='NonRoutableSubnetAZ2')['Parameter']['Value']
        except Exception as exception:
            print(str(exception))
            logger.error(str(exception)) 
            raise Exception(str(exception))
            
    def create_non_routable_resources(self):
        """Fetch parameters for multiple region selected by the user"""
        try:
            for cidr_row in self.event['CIDR_List']:
                cidr_row1 = self.create_subnet(cidr_row)
                cidr_row2 = self.create_nat(cidr_row)
                cidr_row3 = self.routing(cidr_row)    
            print(self.event)
        except Exception as exception:
            print("Subnet creation/nat/routing failed")
            print(str(exception))
            logger.error(str(exception))
            return False
            
    def create_subnet(self,cidr_row):
        """Create subnet of Nonroutable cidr blocks"""
        try:
            #create subnet
            vpc_id = cidr_row['vpc_id']
            self.nrsubnet_id = []
            self.nrsublist = []
            print(cidr_row['region'])
            CidrBlocks = [self.NonRoutableSubnetaz1,self.NonRoutableSubnetaz2]
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
            print(vpc_id)
            count = 0
            for cidr in CidrBlocks:
                subnet_resp = child_account_ec2_client.create_subnet(TagSpecifications=[{ 'ResourceType': 'subnet','Tags': [{'Key': 'Name','Value': 'platform-vpc-subnet-non-routable'},{'Key': 'platform-vpc-subnet-non-routable','Value': 'Yes'},{'Key': 'platform_donotdelete','Value': 'yes'}]}],AvailabilityZone=zone_list[count],CidrBlock=str(cidr),VpcId=vpc_id)
                print(subnet_resp)
                self.nrsubnet_id = subnet_resp['Subnet']['SubnetId']
                self.nrsublist.append(self.nrsubnet_id)
                count+=1
            print(self.nrsublist)
            return self.nrsublist
        except Exception as exception:
            print("Create subnet cannot be done")
            print(str(exception))
            logger.error(str(exception))
            return False
            
    def create_nat(self,cidr_row):
        """Create nat for private ips"""
        try:
            print(cidr_row)
            #create subnet
            self.list_natid = []
            self.privateipblock = []
            rt = []
            vpc_id = cidr_row['vpc_id']
            subnet_id_list = cidr_row['Subnet_Id_List']
            CidrBlocks = [self.NonRoutableSubnetaz1,self.NonRoutableSubnetaz2]
            self.subnet_dict_name = {'PRIVATE': []}
            self.subnet_dict_cidr = {'PRIVATE': []}
            self.child_account_ec2_client = self.assumeRoleSession.client('ec2', region_name=cidr_row['region'])
            print("asuume role not working")
            for item in subnet_id_list:
                subnet_response = self.child_account_ec2_client.describe_subnets(SubnetIds=[item])
                print(subnet_response['Subnets'][0]['Tags'])
                if len(subnet_response['Subnets']) > 0:                    
                    for index in subnet_response['Subnets']:
                        for tag in index['Tags']:
                            if tag['Key'] == 'Name':
                                temp = tag['Value']
                                if 'private' in temp:
                                    self.subnet_dict_name['PRIVATE'].append(index['SubnetId'])
            self.privateipblock = list(self.subnet_dict_name.values())[0]
            print(self.privateipblock)
            for privateip in self.privateipblock:
                nat_response = self.child_account_ec2_client.create_nat_gateway(SubnetId= privateip,ConnectivityType='private',TagSpecifications=[{'ResourceType':'natgateway','Tags': [{'Key': 'Name','Value': 'nat-gateway-nonroutable'},{'Key': 'platform_donotdelete','Value': 'yes'}]}])
                time.sleep(10)
                self.nat_gateway_id = nat_response['NatGateway']['NatGatewayId']
                self.list_natid.append(self.nat_gateway_id)
            print(self.list_natid)
        except Exception as exception:
            print("Nat not available")
            print(str(exception))
            logger.error(str(exception))
            return False
                
                                   
    def routing(self,cidr_row):    
        """Create route-table, associate with Nonroutable subnets and create one default route via NAT Gateway"""
        try:
            #create route table
            rt = []
            vpc_id = cidr_row['vpc_id']
            for index in range(0,2):
                rt_response = self.child_account_ec2_client.create_route_table(TagSpecifications=[{ 'ResourceType': 'route-table','Tags': [{'Key': 'Name','Value': 'platform-route-table-nonroutablesubnet'},{'Key': 'platform_donotdelete','Value': 'yes'}]}],VpcId=vpc_id)
                route_table_id = rt_response['RouteTable']['RouteTableId']
                rt.append(route_table_id)
            print(rt)
                
            for index1 in range(0,2):
                route = self.child_account_ec2_client.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=self.list_natid[index1],RouteTableId=rt[index1])
                response_associate = self.child_account_ec2_client.associate_route_table(RouteTableId=rt[index1],SubnetId=self.nrsublist[index1])
            print(self.nrpriv)
                    
        except Exception as exception:
            print("Routing failing")
            print(str(exception))
            logger.error(str(exception))
            return False
        

def lambda_handler(event, context):
    '''
    Lambda handler for creation of Nonroutable subnets, nat gateway, route tables and linking the route tables to nonroutable subnets
    '''
    IsNonroutableSubnets = event['response_data']['IsNonroutableSubnets']
    Environment = event['ResourceProperties']['Environment']
    if "Yes" in IsNonroutableSubnets and ("Hybrid" in Environment or "Private" in Environment ):
        print("true")
        try:
            if event['CIDRAssociated'] == "yes":
                NatGateway_nonroutable = NATGateway_nonroutable(event,context)
                NatGateway_nonroutable.create_non_routable_resources()
                print(event)
            else:
                print(event)
            return event
        except Exception as exception:
            print("exception")
            logger.debug(str(exception))
    else:
        print("Non-routable option is not opted..!!")
        return event