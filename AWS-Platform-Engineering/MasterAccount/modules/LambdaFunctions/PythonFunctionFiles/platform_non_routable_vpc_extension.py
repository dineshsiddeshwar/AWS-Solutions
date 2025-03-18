"""
This module is used to add Nonroutable CIDR to existing VPC
"""

import boto3
import logging
import random
import time

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
FAILED = "FAILED"
SUCCESS = "SUCCESS"


class ExtendVPC(object):
    """
    # Class: ExtendVPC
    # Description: Add the Nonroutable CIDR to the existing VPC
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        self.cidr_nonroutable = {}
        self.resource_properties = self.event['ResourceProperties']
        self.environment = self.resource_properties['Environment']
        self.IsNonroutableSubnets = event['ResourceProperties']['IsNonroutableSubnets']
        print(self.IsNonroutableSubnets)
        self.region = list(event["region_ip_dict"].keys())
        try:
            self.account_id = self.resource_properties['AccountNumber']
            self.account_name = event['response_data']['AccountName']
            self.CIDR_List = self.event['CIDR_List']
            self.vpc_status = self.event['vpc_status']
            print(self.vpc_status)
            self.subnetidlist = self.CIDR_List[0]['Subnet_Id_List']
            print(self.subnetidlist)
            self.vpc_id = self.CIDR_List[0]['vpc_id']
            print(self.vpc_id)

            print("Creating Session and AWS Service Clients")

            session = boto3.session.Session()
            sts_client = session.client('sts')
            ssm_client = session.client('ssm')
            


            child_account_role_arn = "arn:aws:iam::" + self.account_id + ":role/AWSControlTowerExecution"
            child_account_role_creds = sts_client.assume_role(RoleArn=child_account_role_arn,
                                                              RoleSessionName=child_account_role_session_name)
            credentials = child_account_role_creds.get('Credentials')
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)
            self.NonRoutableCIDR = ssm_client.get_parameter(Name='NonRoutableCIDR')['Parameter']['Value']
            print(self.NonRoutableCIDR)
            self.NonRoutableSubnetaz1 = ssm_client.get_parameter(Name='NonRoutableSubnetAZ1')['Parameter']['Value']
            print(self.NonRoutableSubnetaz1)
            self.NonRoutableSubnetaz2 = ssm_client.get_parameter(Name='NonRoutableSubnetAZ2')['Parameter']['Value']
            print(self.NonRoutableSubnetaz2)   
        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))
            raise Exception(str(exception))
        
    def extend_vpc(self):
        try:
            result_dict = {}
            failed_list = ['disassociating','disassociated','failing','failed']
            for cidr_list in self.CIDR_List:
                self.child_account_ec2_client = self.assumeRoleSession.client('ec2',region_name=cidr_list['region'])
                if self.vpc_status == TRUE:
                    response = self.child_account_ec2_client.associate_vpc_cidr_block(CidrBlock=self.NonRoutableCIDR,VpcId=cidr_list['vpc_id'])
                    time.sleep(20)
                    print(response)
                    print(response['CidrBlockAssociation']['CidrBlockState'])
                    if response['CidrBlockAssociation']['CidrBlockState']['State'] not in failed_list:
                        logger.info("Association of CIDR to VPC {0} in region {1} is completed".format(cidr_list['vpc_id'],cidr_list['region']))
                        result_dict.update({cidr_list['region'] : "SUCCESS"})
                    else:
                        logger.error("Association of CIDR to VPC {0} in region {1} is Failed".format(cidr_list['vpc_id'],cidr_list['region']))
                        result_dict.update({cidr_list['region'] : "FAILED"})
                else:
                    print("cidr not present or vpc unavailable")
            print(response)
            print(response['CidrBlockAssociation']['AssociationId'])
            return result_dict
        except Exception as exception:
            print("Cannot create 2 nonroutable CIDR")
            print(str(exception))
            logger.error(str(exception))
            return result_dict

            

def lambda_handler(event, context):
    '''
    Lambda handler for subnet creation
    '''
    print('event ' + str(event))
    modified_event = {}
    modified_event = event
    count = 0
    IsNonroutableSubnets = event['ResourceProperties']['IsNonroutableSubnets']
    Environment = event['ResourceProperties']['Environment']
    modified_event = event
    if ( "Yes" in IsNonroutableSubnets ) and ( "Private" in Environment or "Hybrid" in Environment ):
        vpc_extend_object = ExtendVPC(event, context)
        outp = vpc_extend_object.extend_vpc()
        if outp != {}:
            for item in outp.values():
                if item == SUCCESS:
                    count +=1
        if count >= len(outp):
            modified_event.update({"CIDRAssociated": "yes"})
        else:
            modified_event.update({"CIDRAssociated": "no"})
        try:
            vpc_extend_object = ExtendVPC(event, context)
            return modified_event
        except Exception as exception:
            print(exception)
            return exception
    else:
        IsNonroutableSubnets == "No"
        print("Non-routable is not opted..")
        return modified_event