# This lambda is created to enable the TRB approved images in the child account. This lambda will be triggered by the step function in the payer account.
import json
import logging
import os
import boto3
import datetime
import random
import time
import requests
import base64


#Cloudwatch logger variables
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

#Environment and global variables
dynamodb_resource = boto3.resource('dynamodb')
session_client = boto3.session.Session()
secretManager_client = session_client.client('secretsmanager', region_name="us-east-1")
database_payer = os.environ['platform_trb_details']
child_event_rule = os.environ['platform_child_event_rule_name']
target_fucntion_name = os.environ['target_function_name']
trb_parameter_ami_name = os.environ['trb_parameter_ami_name']
trb_parameter_owner_id = os.environ['trb_parameter_owner_id']
trb_parameter_image_id = os.environ['trb_parameter_image_id']

SUCCESS = "SUCCESS"
FAILED = "FAILED"
FAILED_RESPONSE = 400
SUCCESS_RESPONSE = 200



tags = [{
    'Key': 'platform_do_not_delete',
    'Value': 'yes'}]


def get_ssm_param(parametre_name):
    """
    param: parametre_name
    return: parameter value for the given param name
    """
    try:
        ssm_client = boto3.client("ssm")
        parameter = ssm_client.get_parameter(
        Name=parametre_name,
            WithDecryption=True
        )
        if parameter:
            return parameter['Parameter']['Value']
    except Exception as ex:
        LOGGER.error("Encountered error while getting parameters'{0}'".format(ex))
        return FAILED

def create_update_ssm_parameters(event, operation_type, parameter_name, param_value, child_ssm_client):
    """
    create/update given ssm parameter.
    :param operation_type: Type of operartion ( OwnerId/AMI_Name)
    :param event: lambda parameter
    :param child_ssm_client: ssm client
    :param param_value: value to be updated
    :return bool: SUCCESS/FAILED
    """
    try:
        description = " TRB approved images/Saas images list."
        parameter_to_update = event['RequestParameter']

        # remove whitespaces
        parameter_to_update = parameter_to_update.replace(" ", "")
        # split string by comma and remove empty strings
        parameter_to_update = list(filter(None, parameter_to_update.split(",")))


        if operation_type == 'Create':

            # join the list of ami ids with comma
            parameter_to_update = ','.join(parameter_to_update)
            create_response = child_ssm_client.put_parameter(
                Name = parameter_name,
                Description = description,
                Value = parameter_to_update,
                Type = 'StringList',
                Overwrite = False,
                Tags = tags)
        else:
            
            temp_value = param_value.split(",")
            temp_value.extend(parameter_to_update)
            temp_value = list(set(temp_value))
            value = ','.join(temp_value)
            update_response = child_ssm_client.put_parameter(
                Name = parameter_name,
                Description= description,
                Value= value,
                Type= 'StringList',
                Overwrite = True)
        return SUCCESS
    except Exception as e:
        LOGGER.error("Something went wrong during ssm parameter creation - '{0}'".format(e))
        return FAILED


def add_ssm_parameters(event, assume_role_session):
    """
    create/update SSM parameters in child account. These set of SSM Parameteres will used by a lambda to whitelist AMIs.
    :param event: lambda event
    :param assume_role_session: STS credentials to be used by the payer account to initiate a client.
    :return: SUCCESS/FAILURE
    """
    try:
        LOGGER.info("Creating SSM Parameters.")
        current_param = ""
        creation_response = FAILED
        child_ssm_client = assume_role_session.client('ssm', region_name= event['Region'])
        ssm_response = child_ssm_client.get_parameters(
            Names = [trb_parameter_ami_name, trb_parameter_owner_id, trb_parameter_image_id],
            WithDecryption = False)
        if event['RequestType'] == 'Owner Account ID': 
            LOGGER.info("Owner ID based whitelisting")
            for param in ssm_response['Parameters']:
                if param['Name'] == trb_parameter_owner_id:
                    current_param = param['Value']
            if current_param:
                LOGGER.info("Parameter does exist.  appending new ami name to the existing parameter list.")
                creation_response = create_update_ssm_parameters(event, 'Update', trb_parameter_owner_id, current_param, child_ssm_client)
            else:
                LOGGER.info("Parameter does not exist. creating new parameter list.")
                creation_response = create_update_ssm_parameters(event, 'Create', trb_parameter_owner_id, current_param, child_ssm_client)
        elif event['RequestType'] == 'Image ID': 
            LOGGER.info("Image Id based whitelisting")
            for param in ssm_response['Parameters']:
                if param['Name'] == trb_parameter_image_id:
                    current_param = param['Value']
            if current_param:
                LOGGER.info("Parameter does exist. Appending new ami name to the existing parameter list.")
                creation_response = create_update_ssm_parameters(event, 'Update', trb_parameter_image_id, current_param, child_ssm_client)
            else:
                LOGGER.info("Parameter does not exist. creating new parameter list.")
                creation_response = create_update_ssm_parameters(event, 'Create', trb_parameter_image_id, current_param, child_ssm_client)
        else:
            LOGGER.info("Image name based whitelisting")
            for param in ssm_response['Parameters']:
                if param['Name'] == trb_parameter_ami_name:
                    current_param = param['Value']
            if current_param:
                LOGGER.info("Parameter does exist. appending new ami name to the existing parameter list.")
                creation_response = create_update_ssm_parameters(event, 'Update', trb_parameter_ami_name, current_param, child_ssm_client)   
            else:
                LOGGER.info("Parameter does not exist. creating new parameter list.")
                creation_response = create_update_ssm_parameters(event, 'Create', trb_parameter_ami_name, current_param,child_ssm_client)
        # If there are parameter present then it's a second run so no need to create an event rule but reuse.
        # get_parameters() returns non-existing parameters in ['InvalidParameters]
        if len(ssm_response['InvalidParameters']) <= 2:
            creation_response = "PRESENT"
        return creation_response
    except Exception as e:
        LOGGER.error("Something went wrong in add_ssm_parameters - '{0}'".format(e))
        return FAILED


def verify_boto_response(response):
    """
    function: validate dynamo response object
    param: response object/dict
    return: SUCCESS/FAILED
    """
    try:
        status_code = response.get('ResponseMetadata', FAILED_RESPONSE).get('HTTPStatusCode')
        if status_code != SUCCESS_RESPONSE:
            LOGGER.error("Invalid parameter passed in request payload.")
            return FAILED
        return SUCCESS
    except Exception as e:
        LOGGER.error("Something went wrong while verifying the AWS response:'{0}'".format(e))
        return FAILED


def put_child_eventbridge_rule(event, child_assume_role_session):
    """
    function: Creates an eventbridge rule in child account's default event bus.
    param: Lambda event
    param: IAM session
    return: SUCCESS/FAILED
    """
    try:
        LOGGER.info("Creating an event bridge rule.")
        eventbridge_childaccount_client = child_assume_role_session.client('events', region_name= event['Region'])
        time.sleep(1)
        put_rule_response = eventbridge_childaccount_client.put_rule(
            Name= child_event_rule,
            ScheduleExpression="rate(1 hour)",
            State='ENABLED',
            Description='Rule to trigger a platform compliance lambda periodically to enable TRB allowed images.',
            Tags=[
                {'Key': 'platform_do_not_delete',
                'Value': 'yes'}
                ])
        lambda_client = child_assume_role_session.client('lambda', region_name= event['Region'])
        put_permission = lambda_client.add_permission(
            FunctionName = target_fucntion_name,
            StatementId= f'{target_fucntion_name}_invoke',
            Action = 'lambda:InvokeFunction',
            Principal = 'events.amazonaws.com',
            SourceArn = put_rule_response['RuleArn'])
        if(verify_boto_response(put_rule_response)) == FAILED:
            return FAILED
        time.sleep(1)
        put_rule_response = (put_rule_response.get('RuleArn',"")).split("/")
        add_target_response = eventbridge_childaccount_client.put_targets(
            Rule= put_rule_response[1],
            Targets=[{
                "Id": "MyTargetId",
                "Arn": "arn:aws:lambda:"+ event['Region'] + ":" + event['BusinessAccountNumber'] +":function:" + target_fucntion_name}])
        return SUCCESS
    except Exception as e:
        LOGGER.error("Something went wrong inside event rule enabler:'{0}'".format(e))
        return FAILED

def validate_paylaod_in_child_account(event, child_assume_role_session, child_account_region):
    """
    Function: Validates if the AMI ID/ List of AMI with owner ID/ AMI with the provided name is present in the child account
    Param: event, child_access_key_id, child_secret_access_key, child_session_token, child_account_region
    returns: SUCCESS/FAILURE
    """
    try:
        print("Inside validate_paylaod_in_child_account")
        ec2_client = child_assume_role_session.client('ec2', region_name=child_account_region)
        
        if event["RequestType"] == "Image ID":
            ami_id = event["RequestParameter"]
            # remove whitespaces from ami_id list
            ami_id = ami_id.replace(" ", "")
            # split the ami_id list by comma and remove empty strings
            ami_id_list = list(filter(None, ami_id.split(",")))
            ami_details = ec2_client.describe_images(ImageIds=ami_id_list)
            
            if 'Images' in ami_details and ami_details['Images']:
                image_info = ami_details['Images'][0]
                LOGGER.info("Found the AMI details in child Account: '{0}'".format(image_info))
                return SUCCESS
            else:
                print("No ami found with AMI ID '{0}'".format(event["RequestParameter"]))
            return FAILED
            
        elif event["RequestType"] == "Owner Account ID":
            owner_id = event["RequestParameter"]

            # remove whitespaces
            owner_id = owner_id.replace(" ", "")
            # split string by comma and remove empty strings
            owner_id = list(filter(None, owner_id.split(",")))

            ami_details = ec2_client.describe_images(Owners=owner_id)
            if 'Images' in ami_details and ami_details['Images']:
                image_info = ami_details['Images']
                LOGGER.info("Found the '{0}'AMI details in child Account: '{0}'".format(len(image_info)))
                return SUCCESS
            else:
                print("No ami found with AMI Owner ID '{0}'".format(event["RequestParameter"]))
            return FAILED
            
        else:
            ami_name = event["RequestParameter"]
            # remove whitespaces
            # only remove whitespaces where after and before comma

            ami_name = ami_name.replace(", ", ",")
            ami_name = ami_name.replace(" ,", ",")
            # split string by comma and remove empty strings
            ami_name = list(filter(None, ami_name.split(",")))
            ami_details = ec2_client.describe_images(Filters=[{'Name':'name', 'Values':ami_name}])
            if len(ami_details['Images']) > 0:
                image_info = ami_details['Images'][0]
                print(ami_details['Images'][0])
                LOGGER.info("Found the '{0}'AMI details in child Account: '{0}'".format(image_info))
                return SUCCESS
            else:
                print("No ami found with AMI Name '{0}'".format(event["RequestParameter"]))
            return FAILED
    except Exception as ex:
        LOGGER.error("Something went wrong validating paylaod in child account'{0}'".format(ex))
        return FAILED


def enable_child_account(event, context):
    """
    function: Assume a role in child account and enables the required infra inside the provided account.
    param: lambda event
    returns: SUCCESS/FAILURE
    """
    try:
        LOGGER.info("Assuming a role in child account:'{0}'".format(event['BusinessAccountNumber']))
        session_client = boto3.session.Session()
        sts_master_client = session_client.client('sts')
        iam_arn_string_prefix = "arn:aws:iam::"
        str_sts_assume_role = "sts:AssumeRole"
        str_lambda_arn = "lambda.amazonaws.com"
        target_account_number = event['BusinessAccountNumber']
        master_account_number = context.invoked_function_arn.split(":")[4]
        child_account_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))
        master_account_session_name = "MasterAccountSession-" + str(random.randint(1, 100000))
        child_account_role_arn = iam_arn_string_prefix + str(target_account_number) + ":role/AWSControlTowerExecution"

        """Assume Role into the child account"""    
        child_account_role_creds = sts_master_client.assume_role(RoleArn=child_account_role_arn,RoleSessionName=child_account_session_name)
        child_credentials = child_account_role_creds.get('Credentials')
        child_access_key_id = child_credentials.get('AccessKeyId')
        child_secret_access_key = child_credentials.get('SecretAccessKey')
        child_session_token = child_credentials.get('SessionToken')
        # start a session in child account
        child_assume_role_session = boto3.Session(child_access_key_id, child_secret_access_key,child_session_token)
        # validating payload info in the child account for IMAGE existence
        validate_paylaod_response = validate_paylaod_in_child_account(event, child_assume_role_session, event["Region"])
        if validate_paylaod_response != SUCCESS:
            LOGGER.info("No AMI found in the child account with the provided payload")
            return FAILED, "No AMI found in the child account with the provided payload"
        # add SSM parameters in the child account
        ssm_response = add_ssm_parameters(event, child_assume_role_session)
        
        # enable the cloudwatch rule in child only for first timers.
        if ssm_response != "PRESENT":
            event_bridge_response = put_child_eventbridge_rule(event, child_assume_role_session)
            if event_bridge_response != SUCCESS:
                return FAILED, "Failed to create event bridge rule in the child account."
        else:
            LOGGER.info("Event bridge rule is already present in the account. Skipping the eventbridge setup.")
            return SUCCESS, "Event bridge rule is already present in the account. Skipping the eventbridge setup."
        return SUCCESS, "enabled the child account."    
    except Exception as ex:
        LOGGER.error("An issue occure inside the  child account. Attention required.'{0}'".format(ex))
        return FAILED, ex

def get_custodian(accountid):
    """this module will return custodian email id"""
    try:
        LOGGER.info("Getting custodian Email id from DB")
        db_client = boto3.client('dynamodb')
        db_response = db_client.get_item(
                                    TableName='Account_Details',
                                    Key={
                                        'AccountNumber': {
                                            'S': accountid
                                        }
                                    },
                                    AttributesToGet=['CustodianUser']
                                )
        custodian_id = db_response['Item']['CustodianUser']['S']
        return custodian_id
    except Exception as ex:
        LOGGER.error("Encountered error while getting custoain Email ID".format(ex))    
        return False

def lambda_handler(event, context):
    """
    function: Lambda handler
    param: event from the lambda fucntion(API gateway).
        {
            "BusinessAccountNumber": "AccountNumber",
            "Region": "Region",
            "RequestType": "owner_id|image_name|image_id",
            "RequestParameter": "<ami owner account id>|<ami_name>"
    }
    param: lambda context/runtime
    returns: json response
    """
    try:
        LOGGER.info("Inside the Lambda handler with the event - '{0}'".format(json.dumps(event)))
        #Enable changes in the child account
        event['CustodianMailId'] = get_custodian(event['BusinessAccountNumber'])
        child_response,response = enable_child_account(event, context)
        if child_response == FAILED:
            # status = "FAILED"
            return {
            'statusCode': 400,
            'AccountNumber': event['BusinessAccountNumber'],
            'Region': event['Region'],
            'RequestType': event['RequestType'],
            'RequestParameter': event['RequestParameter'],
            'CustodianMailId': event['CustodianMailId'],
            'message': "Request Failed : {0}".format(response)
            }
        
        return {
        'statusCode': 200,
        'AccountNumber': event['BusinessAccountNumber'],
        'Region': event['Region'],
        'RequestType': event['RequestType'],
        'RequestParameter': event['RequestParameter'],
        'CustodianMailId':event['CustodianMailId'],
        'message': "Request Successful"
        }
    except Exception as ex:
        LOGGER.error("Something went wrong inside the Lambda handler'{0}'".format(ex))
        # notify_operations(event, ex)
        return {
        'statusCode': 400,
        'AccountNumber': event['BusinessAccountNumber'],
        'Region': event['Region'],
        'RequestType': event['RequestType'],
        'RequestParameter': event['RequestParameter'],
        'CustodianMailId':event['CustodianMailId'],
        'message': "Request Failed:  Error in platform_TRB_management_payer_child_account_trigger"
        }
