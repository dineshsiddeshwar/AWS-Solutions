"""
This module is used to associate DNS Resolver and VPC gateway Endpoints in Child Account
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


class AssociateResolverRule(object):
    """
    # Class: AssociateResolverRule
    # Description: creates and attaches Route53 resolver
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

    def associate_resolver(self, cidr_row):
        try:

            vpc_id =cidr_row['vpc_id']
            child_account_ec2_client = self.assumeRoleSession.client('ec2', region_name=cidr_row['region'])
            resolver_client = self.assumeRoleSession.client('route53resolver', region_name =cidr_row['region'])

            list_rules = resolver_client.list_resolver_rules(
                Filters=[
                    {
                        'Name': 'Name',
                        'Values': [
                            'platform_Shell_Domain_Forwarder_Outbound_Rule','platform_Shell_io_Domain_Forwarder_Outbound_Rule','platform_Shell_shell_Domain_Forwarder_Outbound_Rule'
                        ]
                    }
                ]
            )
            association_list=[]
            rule_list=[]
            for iterator in range(0,len(list_rules['ResolverRules'])):
                cidr_row['rule_id'] = list_rules['ResolverRules'][iterator]['Id']
                rule_list.append(list_rules['ResolverRules'][iterator]['Id'])

                try:
                    association_response = resolver_client.associate_resolver_rule(
                    ResolverRuleId= cidr_row['rule_id'],
                    Name='platform_ResolverRuleAssociation',
                    VPCId=vpc_id
                    )
                    print(association_response['ResolverRuleAssociation']['Id'])
                    association_list.append(association_response['ResolverRuleAssociation']['Id'])
                except Exception as e:
                    print(e)
                    list_associations = resolver_client.list_resolver_rule_associations(
                        Filters=[
                            {
                            'Name': 'Name',
                            'Values': [
                                'platform_ResolverRuleAssociation'
                            ]
                            }])
                    association_list.append(list_associations['ResolverRuleAssociations'][iterator]['Id'])
                    print("Association ID",list_associations['ResolverRuleAssociations'][iterator]['Id'])

                except Exception as e:
                    print(e)
            association_id_list=",".join(association_list)
            rule_id_list=",".join(rule_list)
            cidr_row['association_id']=association_id_list
            cidr_row['rule_id']=rule_id_list
            self.event['resolver'] = "TRUE"  #For unit testing and to validate in step function
            return cidr_row
        except Exception as exception:
            print("Association private environment failed!!!")
            print(str(exception))
            self.event['resolver'] = "FALSE"
            logger.error(str(exception))
            return cidr_row

    def create_vpc_gateway_endpoints(self, cidr_row):
        try:

            """
            The below section enabled gateway endpoint for S3 and DDB
            """
            print("enable gateway Endpoints")
            vpc_id = cidr_row['vpc_id']
            region = cidr_row['region']
            s3_service_name = "com.amazonaws."+ region + ".s3"
            ddb_service_name = "com.amazonaws."+ region + ".dynamodb"
            child_account_ec2_client = self.assumeRoleSession.client('ec2', region_name=region)
            rtb_response = child_account_ec2_client.describe_route_tables(
                Filters=[
                    {
                        'Name': 'vpc-id',
                        'Values': [vpc_id]
                    },
                ]
            )
            rtb_id = rtb_response['RouteTables'][0]['RouteTableId']
            endpoint_response = child_account_ec2_client.describe_vpc_endpoints(
                Filters=[
                    {
                        'Name': 'service-name',
                        'Values': [
                            s3_service_name
                        ]
                    }
                ]
            )
            print(endpoint_response)
            if len(endpoint_response['VpcEndpoints'])<1:

                S3_response = child_account_ec2_client.create_vpc_endpoint(
                    VpcEndpointType='Gateway',
                    VpcId=vpc_id,
                    ServiceName=s3_service_name,
                    RouteTableIds=[
                        rtb_id
                    ],
                    TagSpecifications=[
                        {
                            'ResourceType': 'vpc-endpoint',
                            'Tags': [
                                {
                                    'Key': 'platform_donotdelete',
                                    'Value': 'yes'
                                },
                                {
                                    'Key': 'Name',
                                    'Value': 'platform-S3-Endpoint'
                                },
                            ]
                        },
                    ]
                )
                print(S3_response)
            endpoint_response = child_account_ec2_client.describe_vpc_endpoints(
                Filters=[
                    {
                        'Name': 'service-name',
                        'Values': [
                            ddb_service_name
                        ]
                    }
                ]
            )
            print(endpoint_response)
            if len(endpoint_response['VpcEndpoints'])<1:
                ddb_response = child_account_ec2_client.create_vpc_endpoint(
                    VpcEndpointType='Gateway',
                    VpcId=vpc_id,
                    ServiceName= ddb_service_name,
                    RouteTableIds=[
                        rtb_id
                    ],
                    TagSpecifications=[
                        {
                            'ResourceType': 'vpc-endpoint',
                            'Tags': [
                                {
                                    'Key': 'platform_donotdelete',
                                    'Value': 'yes'
                                },
                                {
                                    'Key': 'Name',
                                    'Value': 'platform-DynamoDB-Endpoint'
                                },
                            ]
                        },
                    ]
                )
                print(ddb_response)
            self.event['vpc_endpoint_gateways'] = "True"
        except Exception as exception:
            print("vpc endpoint creation failed!!")
            print(str(exception))
            logger.error(str(exception))


def lambda_handler(event, context):
    """
    Lambda handler calls the function that provisions the vpc in the child account
    """
    try:
        resolver_obj = AssociateResolverRule(event, context)
        for cidr_row in event['CIDR_List']:
            cidr_row = resolver_obj.associate_resolver(cidr_row)
            cidr_row = resolver_obj.create_vpc_gateway_endpoints(cidr_row)
        return event
    except Exception as exception:
        logger.error(str(exception))
        print(str(exception))