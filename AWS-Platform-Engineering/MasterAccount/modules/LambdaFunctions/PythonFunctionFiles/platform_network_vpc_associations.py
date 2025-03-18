"""
This module is used to create and attach service endpoint associations in private environment
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


class VPCAssociations(object):
    """
    # Class: VPCAssociations
    # Description: creates and attaches endpoint associations
    """

    def __init__(self, event, context):
        self.event = event
        self.resource_properties = self.event['ResourceProperties']
        # get relevant input params from event
        self.account_id = self.resource_properties['AccountNumber']
        sts_client = boto3.client('sts')
        ssm_client = boto3.client('ssm')
        # ssm parameter values

        self.hosted_zone_list_us = (ssm_client.get_parameter(Name='hostedzone_id_us')['Parameter']['Value']).split(',')
        self.hosted_zone_list_eu = ssm_client.get_parameter(Name='hostedzone_id_eu')['Parameter']['Value'].split(',')
        self.hosted_zone_list_sg = ssm_client.get_parameter(Name='hostedzone_id_sg')['Parameter']['Value'].split(',')

        n_account_number = ssm_client.get_parameter(Name='shared_services_account_id')['Parameter']['Value']
        print(n_account_number)
        # Session for child Account
        child_account_role_arn = "arn:aws:iam::" + self.account_id + ":role/AWSControlTowerExecution"
        child_account_role_creds = sts_client.assume_role(RoleArn=child_account_role_arn,
                                                          RoleSessionName=child_account_role_session_name)
        credentials = child_account_role_creds.get('Credentials')

        self.assumeRoleSession = boto3.session.Session(credentials.get('AccessKeyId'),
                                        credentials.get('SecretAccessKey'), credentials.get('SessionToken'))

        # Session for Shared Services account
        secondary_rolearn = "arn:aws:iam::{}:role/AWSControlTowerExecution".format(n_account_number)
        secondary_session_name = "SecondarySession-" + str(random.randint(1, 100000))
        secondaryRoleCreds = sts_client.assume_role(RoleArn=secondary_rolearn,
                                                    RoleSessionName=secondary_session_name)
        n_credentials = secondaryRoleCreds.get('Credentials')
        self.ss_assumeRoleSession = boto3.session.Session(n_credentials.get('AccessKeyId'),
                                                          n_credentials.get('SecretAccessKey'),
                                                          n_credentials.get('SessionToken'))

    def enable_vpc_attributes(self, cidr_row):
        try:

            """
            The below section enabled vpc attributes-  DNS  
            """
            print("enable_vpc_attributes")
            client = self.assumeRoleSession.client('ec2', region_name=cidr_row['region'])
            support_response = client.modify_vpc_attribute(
                EnableDnsSupport={
                    'Value': True,
                },
                VpcId=cidr_row['vpc_id'],
            )
            response = client.modify_vpc_attribute(
                EnableDnsHostnames={
                    'Value': True,
                },
                VpcId=cidr_row['vpc_id'],
            )

            print("Enabled vpc attributes",response)
            self.event['vpc_attributes'] = "True"
        except Exception as exception:
            print("enable_vpc_attributes failed!!!")
            print(str(exception))
            logger.error(str(exception))
            return False

    def invoke_association(self):
        '''Invoke the vpc association for each vpc'''
        try:
            for cidr_row in self.event['CIDR_List']:

                self.enable_vpc_attributes(cidr_row)
                if cidr_row['region'] == 'us-east-1':
                    self.associate_hostedzones(cidr_row, self.hosted_zone_list_us)
                elif cidr_row['region'] == 'eu-west-1':
                    self.associate_hostedzones(cidr_row, self.hosted_zone_list_eu)
                elif cidr_row['region'] == 'ap-southeast-1':
                    self.associate_hostedzones(cidr_row, self.hosted_zone_list_sg)
                else:
                    print("Region not supported")
            self.event['invoke_associations'] = "True"
        except Exception as e:
            print("Failed to invoke association")

    def associate_hostedzones(self, cidr_row, hosted_zone_list):
        try:

            """
            The below section associate vpc with private hosted zones form Shared services  
            """
            print("Inside associate hostedzones")

            child_r53_client = self.assumeRoleSession.client('route53', region_name=cidr_row['region'])
            r53_client = self.ss_assumeRoleSession.client('route53', region_name=cidr_row['region'])
            for hosted_zone_id in hosted_zone_list:
                # loop through shared hosted zone and  create associations

                try:
                    # authorize child account to create associations in Shared Services account
                    response = r53_client.create_vpc_association_authorization(
                        HostedZoneId=hosted_zone_id,
                        VPC={
                            'VPCRegion': cidr_row['region'],
                            'VPCId': cidr_row['vpc_id']
                        }
                    )
                    print(response)

                    # Create hosted zone associations in child account
                    child_response = child_r53_client.associate_vpc_with_hosted_zone(
                        HostedZoneId=hosted_zone_id,
                        VPC={
                            'VPCRegion': cidr_row['region'],
                            'VPCId': cidr_row['vpc_id']
                        },
                    )
                    print(child_response)

                except Exception as exception:
                    print("vpc association failed in loop!!!",hosted_zone_id)
                    print(str(exception))
                    logger.error(str(exception))
                    continue
            self.event['associate_hostedzones'] = "True"
        except Exception as exception:
            print("enable_vpc_attributes failed!!!")
            print(str(exception))
            logger.error(str(exception))
            return False


def lambda_handler(event, context):
    """
    Lambda handler calls the function that provisions the vpc in the child account
    """
    try:
        association_obj = VPCAssociations(event, context)
        association_obj.invoke_association()
        return event
    except Exception as exception:
        logger.error(str(exception))
        print(str(exception))
        raise Exception(str(exception))

