import boto3
import logging
import json
import os
from datetime import datetime, timezone

#CLouwatch logger variables
logger = logging.getLogger()
logger.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
logger.addHandler(CH)

DYNAMODB_CLIENT = boto3.client('dynamodb', region_name='us-east-1')
SUCCESS = "SUCCESS"
FAILED = "FAILED"
# arn:aws:dynamodb:us-east-1:XXXX:table/EC2_ISLOLATION_TRACKER

def check_if_approved_already(instanceid):
    """
    This function checks if the request is alredy approved or not. Item will be there if already approved
    """
    try:
        print("Inside check if already approved function")
        db_rsponse = DYNAMODB_CLIENT.get_item(
                                            Key={
                                                'InstanceID': {
                                                    'S': instanceid
                                                }
                                            },
                                            AttributesToGet=['InstanceID'],
                                            TableName='EC2_ISOLATION_TRACKER',
                                        )
        if 'Item' in db_rsponse.keys():
            logger.info("Instance item found in db.")
            return True
        else:
            return False
    except Exception as ex:
        logger.error("something went wrong in checking if already approved {}".format(ex))
        raise ex


def create_security_group(client, vpcid):
    """
    This function create s security group and return blank security group
    """
    try:
        print("Inside check creating sec group")
        try:
            sec_response = client.create_security_group(
                                Description='This is a blank sec group to isolate ec2 instance',
                                GroupName='Ec2_Isolation_security_group',
                                TagSpecifications=[
                                            {
                                                'ResourceType': 'security-group',
                                                'Tags': [
                                                    {
                                                        'Key': 'Name',
                                                        'Value': 'Ec2_Isolation_security_group'
                                                    },
                                                ]
                                            },
                                        ],
                                VpcId=vpcid)
            if sec_response:
                logger.info("blank security group created {}".format(sec_response['GroupId']))
                revoke_response = client.revoke_security_group_egress(
                                            GroupId=sec_response['GroupId'],
                                            IpPermissions=[{
                                                'FromPort': -1,
                                                'IpProtocol': 'All',
                                                'ToPort': -1,
                                                'IpRanges': [
                                                    {
                                                        'CidrIp': '0.0.0.0/0'
                                                    }
                                                ]
                                            
                                            }])
                if revoke_response['Return']:
                    return sec_response['GroupId']
                else:
                    raise("Something went wrong while revoking the sec group outbout rule")
        except Exception as ex:
            logger.info("inside sec group exception")
            if 'InvalidGroup.Duplicate' in str(ex):
                desc_res = client.describe_security_groups(
                                    Filters=[
                                        {
                                            'Name': 'tag:Name',
                                            'Values': [
                                                'Ec2_Isolation_security_group'
                                            ]
                                        },
                                        {
                                            'Name': 'vpc-id',
                                            'Values': [
                                                vpcid
                                            ]
                                        }
                                    ])
                if len(desc_res['SecurityGroups']) > 0:
                    sec_id = desc_res['SecurityGroups'][0]['GroupId']
                    return sec_id
                else:
                    sec_response = client.create_security_group(
                                Description='This is a blank sec group to isolate ec2 instance',
                                GroupName='Ec2_Isolation_security_group',
                                VpcId=vpcid)
                    if sec_response:
                        logger.info("blank security group created {}".format(sec_response['GroupId']))
                        revoke_response = client.revoke_security_group_egress(
                                            GroupId=sec_response['GroupId'],
                                            IpPermissions=[{
                                                'FromPort': -1,
                                                'IpProtocol': 'All',
                                                'ToPort': -1,
                                                'IpRanges': [
                                                    {
                                                        'CidrIp': '0.0.0.0/0'
                                                    }
                                                ]
                                            
                                            }])
                        if revoke_response['Return']:
                            return sec_response['GroupId']
                        else:
                            raise("Something went wrong while revoking the sec group outbout rule")
            else:
                logger.error(ex)
                raise ex
        
    except Exception as ex:
        logger.error("something went wrong in creating sec group {}".format(ex))
        raise ex


def modify_instance_attribute(blank_sec_id,instanceid,ec2_session_client):
    """
    This function will modify the security group
    """
    try:
        print("Inside check modifying the instance attribute")
        sec_res = ec2_session_client.modify_instance_attribute(InstanceId=instanceid,Groups=[blank_sec_id])
        if sec_res['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False
    except Exception as ex:
        logger.error("something went wrong in modifying the instance attribute {}".format(ex))
        raise ex

def isolate_ec2_instnace(instanceid, accounid, region):
    """
    This function isolates the ec2 instance. That is removing the sg group and attaches the blank security group
    """
    try:
        print("Inside check isolate ec2 instance")
        ec2_role_arn = "arn:aws:iam::"+accounid+":role/HIS-419-qualys-lambda-isolate-EC2-assumedrole"
        sts_client = boto3.client('sts')
        
        assumed_role_object = sts_client.assume_role(
                            RoleArn=ec2_role_arn,
                            RoleSessionName="236_ec2_role")
        credentials = assumed_role_object['Credentials']
        ec2_session = boto3.session.Session(
                                        aws_access_key_id=credentials['AccessKeyId'],
                                        aws_secret_access_key=credentials['SecretAccessKey'],
                                        aws_session_token=credentials['SessionToken']
                                    )
        ec2_session_client = ec2_session.client('ec2', region_name=region)
        describe_response = ec2_session_client.describe_instances(InstanceIds=[instanceid])
        vpcid = describe_response['Reservations'][0]['Instances'][0]['VpcId']
        sec_id_dict = describe_response['Reservations'][0]['Instances'][0]['SecurityGroups']
        sec_id_list = []
        for item in sec_id_dict:
            sec_id_list.append(item['GroupId'])
        blank_sec_id = create_security_group(ec2_session_client, vpcid)
        modify_attribute = modify_instance_attribute(blank_sec_id,instanceid,ec2_session_client)
        if modify_attribute:
            return sec_id_dict
        else:
            return False
    except Exception as ex:
        logger.error("something went wrong in isolating ec2 instance {}".format(ex))
        raise ex



def update_dynamoDB_table(instanceid, accounid, email, region, decision, sec_id_list):
    """
    This function updates the dynamodb table after isolation
    """
    try:
        print("Inside Update dynamoDB table")
        utc_now = datetime.now(timezone.utc)
        utc_now_str = utc_now.strftime('%Y-%m-%d %H:%M UTC')
        db_update_res = DYNAMODB_CLIENT.put_item(
                            TableName='EC2_ISOLATION_TRACKER',
                            Item={
                                'InstanceID': {
                                    'S': instanceid
                                },
                                'AccountNumber': {
                                    'S': accounid
                                },
                                'Approver': {
                                    'S': email
                                },
                                'Decision': {
                                    'S': decision
                                },
                                'Region': {
                                    'S': region
                                },
                                'ExistingSecGroups': {
                                    'S': str(sec_id_list)
                                },
                                'TimeApproved_UTC': {
                                    'S': utc_now_str
                                }
                            }
                        )
        if db_update_res:
            logger.info("Dynamo DB updated for the key {}".format(instanceid))
            return True
        else:
            return False
    except Exception as ex:
        logger.error("something went wrong in updating the dynamodb table {}".format(ex))
        raise ex

def lambda_handler(event, context):
    """
    This lambda will assume a role in account and performs the isolation
    """
    try:
        logger.info("Recieved the event:- {}".format(event))
        instanceid = event['instanceId']
        region = event['region']
        email = event['email']
        accounid = event['accountId']
        decision = event['decision']
        if decision == 'approve':
            is_exists = check_if_approved_already(instanceid)
            if is_exists:
                logger.info("Request was already processed and Updated the DynamoDB table. Hence skipping")
                return True
            else:
                security_grou_id_list = isolate_ec2_instnace(instanceid, accounid, region)
                if security_grou_id_list:
                    logger.info("Isolated the ec2 instanc. Now updating the DynamoDB table")
                    update_db = update_dynamoDB_table(instanceid, accounid, email, region, decision, security_grou_id_list)
                    if update_db:
                        logger.info("Request succesfully completed")
                        return True
                    else:
                        logger.error("Something went wrong in updating db")
                        return False
                else:
                    logger.error("Something went wrong in instance isolation")
                    return False

        elif decision == 'reject':
            logger.info("Request is rejected hence Not doing anything. Skipping...")
            return True
    except Exception as ex:
        logger.error("something went wrong in lambda handler {}".format(ex))
        raise ex