import json
import logging
import os
import boto3
import datetime
import random
import time
#import requests


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

#UAM tableName
database_payer = "NonInteractiveUser_Management"

SUCCESS = "SUCCESS"
FAILED = "FAILED"
FAILED_RESPONSE = 400
SUCCESS_RESPONSE = 200


RETURN_SUCCESS = {
        'statusCode': 200,
        'message': "Request Successful"
    }
RETURN_FAILURE = {
        'statusCode': 400,
        'message': "Request Failed"
    }

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


def notify_operations_automation_failure(event,e):
    """
    Alerts the team in case of failures.
    :param event: lambda event
    """
    try:
        ses_client = boto3.client('ses')
        titan_dl_str = get_ssm_param("tital_dl")
        sender_id = get_ssm_param("sender_id")

        body_text = """Hello Team\n An error occured in Non Interactive User - Payer Lambda""" \
                    + """\nBest Regards,\n AWS Platform Engineering team"""

            # The HTML body of the email.
        body_html = """<html>
                <body>
                <p style="font-family:'Arial Nova'">Hello Team,<p>
                <p></p>
                <p style="font-family:'Arial Nova'">An error occured during noninteractive user processing, automation needs a manual intevention.</p>
                <ul>
                <li style="font-family:'Arial Nova'">Business Account Number: """ + str(event['AccountNumber']) + """</li>
                <li style="font-family:'Arial Nova'">Request Number: """ + str(event['RequestNumber']) + """</li>
                <li style="font-family:'Arial Nova'">SCTASKNumber: """ + str(event['SCTaskNumber']) + """</li>
                <li style="font-family:'Arial Nova'">Payer Account Lambda Name: """ + "platform_noninteractive_user_payer" + """</li>
                <li style="font-family:'Arial Nova'">Error / Exception: """ + str(e) + """</li>
                <p style="font-family:'Arial Nova'"></p>
                <p style="font-family:'Arial Nova'">Thanks,</p>
                <p style="font-family:'Arial Nova'"> AWS Platform Engineering Team.</p>
                </body>
                </html>
            """.format(event['RequestNumber'])

        send_mail_response = ses_client.send_email(
            Source= sender_id,
            Destination={
                'ToAddresses': [titan_dl_str]
            },
            Message={
                'Subject': {
                    'Data':' ALERT: Non Interactive User Automation Failed'
                },
                'Body': {
                    'Text': {
                        'Data': body_text
                    },
                    'Html': {
                        'Data': body_html
                    }
                }
            }
        )
        return SUCCESS
    except Exception as e:
        LOGGER.error("An error occured while sending an alert to the TITAN team - '{0}".format(e))
        return FAILED



def dynamo_write(event, table_item, dynamo_table):
    """
    Add an item containing UAM details to the dynamodb
    param table_item: item to add to table
    param dynamo_table: dynamodb table name
    return: SUCCESS or FAILED
    """
    try:
        LOGGER.info("Making an entry to the dynamodb table")
        LOGGER.info("Writing to Dynamo DB:'{0}'".format(table_item))
        dynamo_response = dynamo_table.put_item(
            Item=table_item
            )
        status_code = dynamo_response.get('ResponseMetadata', FAILED_RESPONSE).get('HTTPStatusCode')   
        if status_code != SUCCESS_RESPONSE:
            LOGGER.error("unable to add the item to the dynamodb.'{0}'".format(table_item))
            msg = "unable to add the item to the dynamodb.'{0}'".format(table_item)
            notify_operations_automation_failure(event, msg)
            return FAILED 
    except Exception as ex:
        LOGGER.error("An error occured during dynamo record creation.'{0}'".format(ex))
        notify_operations_automation_failure(event, ex)
        return FAILED

def create_user(event, assume_role_session):
    try:
        LOGGER.info("Creating IAM User...")
        child_iam_client = assume_role_session.client('iam')
        #check if iam user with same name exists
        response = child_iam_client.list_users()
        for user in response['Users']:
            if user['UserName'] == event["UserName"]:
                print("User already exists! Exiting...")
                RARS_STATUS_CLOSED_INCOMPLETE=0
                return RARS_STATUS_CLOSED_INCOMPLETE, "User already exists! Please ensure that the provided username to be created does not exist already in your account.", FAILED

        response = child_iam_client.create_user(
            UserName=event["UserName"]
        )
        print(response)
        return 1, response, SUCCESS
    except Exception as e:
        LOGGER.error("Something went wrong during IAM User creation - '{0}'".format(e))
        return 1, e, FAILED

def delete_user(event, assume_role_session):
    try:
        #check if iam user exists
        child_iam_client = assume_role_session.client('iam')
        response = child_iam_client.list_users()
        flag=0
        for user in response['Users']:
            if user['UserName'] == event["UserName"]:
                print("User exists. Proceeding with checks:")
                flag=1
                break
        if flag==0:
            msg="User does not exist! Please ensure that the provided username to be deleted exists in your account."
            RARS_STATUS_CLOSED_INCOMPLETE=0
            print("User does not exist! Exiting...")
            return RARS_STATUS_CLOSED_INCOMPLETE, msg, FAILED
        
        #remove group memberships
        group_list=[]
        response = child_iam_client.list_groups_for_user(UserName=event["UserName"])
        for group in response['Groups']:
            group_list.append(group['GroupName'])
        while response["IsTruncated"] == True:
            print("Group List Parameter IsTruncated is True")
            response = child_iam_client.list_groups_for_user(
                UserName=event["UserName"],
                Marker=response['Marker']
            )
        
        while len(group_list) > 0:
            print("Groups Found! Removing user from groups...")
            group = group_list.pop()
            try:
                response = child_iam_client.remove_user_from_group(
                GroupName=group,
                UserName=event["UserName"]
                )
                print(response)
            except Exception as e:
                print(e)
                print("Error in removing user from group")
                return 1, e, FAILED

        #check if iam user has attached policies
        attached_policy_arns_all=[]
        response = child_iam_client.list_attached_user_policies(UserName=event["UserName"])
        for policy in response['AttachedPolicies']:
            attached_policy_arns_all.append(policy['PolicyArn'])
        while response["IsTruncated"] == True:
            print("Policy List Parameter IsTruncated is True")
            response = child_iam_client.list_attached_user_policies(
            UserName=event["UserName"],
            Marker=response['Marker'])
            for policy in response['AttachedPolicies']:
                attached_policy_arns_all.append(policy['PolicyArn'])

        #Deleting attached policies
        while len(attached_policy_arns_all) > 0:
            print("Attached Policies Found! Deleting attached policies...")
            policy = attached_policy_arns_all.pop()
            try:
                response = child_iam_client.detach_user_policy(
                UserName=event["UserName"],
                PolicyArn=policy
                )
                print(response)
            except Exception as e:
                print(e)
                print("Error in deleting attached policies")
                return 1, e, FAILED
        
        #check if iam user has inline policies
        inline_policy_names_all=[]
        response = child_iam_client.list_user_policies(UserName=event["UserName"])
        for policy in response['PolicyNames']:
            inline_policy_names_all.append(policy)
        while response["IsTruncated"] == True:
            print("Policy List Parameter IsTruncated is True")
            response = child_iam_client.list_user_policies(
            UserName=event["UserName"],
            Marker=response['Marker'])
            for policy in response['PolicyNames']:
                inline_policy_names_all.append(policy)
        
        #Deleting inline policies
        while len(inline_policy_names_all) > 0:
            print("Inline Policies Found! Deleting inline policies...")
            policy = inline_policy_names_all.pop()
            try:
                response = child_iam_client.delete_user_policy(
                UserName=event["UserName"],
                PolicyName=policy
                )
                print(response)
            except Exception as e:
                print(e)
                print("Error in deleting inline policies")
                return 1, e, FAILED
        
        #check if iam user has access keys
        access_key_ids_all=[]
        response = child_iam_client.list_access_keys(UserName=event["UserName"])
        for key in response['AccessKeyMetadata']:
            access_key_ids_all.append(key['AccessKeyId'])
        while response["IsTruncated"] == True:
            print("Access Key List Parameter IsTruncated is True")
            response = child_iam_client.list_access_keys(
            UserName=event["UserName"],
            Marker=response['Marker'])
            for key in response['AccessKeyMetadata']:
                access_key_ids_all.append(key['AccessKeyId'])
        
        #Deleting access keys
        while len(access_key_ids_all) > 0:
            print("Access Keys Found! Deleting access keys...")
            key = access_key_ids_all.pop()
            try:
                response = child_iam_client.delete_access_key(
                UserName=event["UserName"],
                AccessKeyId=key
                )
                print(response)
            except Exception as e:
                print(e)
                print("Error in deleting access keys")
                return 1, e, FAILED
        
        #check if iam user has mfa devices
        mfa_devices_all=[]
        response = child_iam_client.list_mfa_devices(UserName=event["UserName"])
        for device in response['MFADevices']:
            mfa_devices_all.append(device['SerialNumber'])
        while response["IsTruncated"] == True:
            print("MFA Device List Parameter IsTruncated is True")
            response = child_iam_client.list_mfa_devices(
            UserName=event["UserName"],
            Marker=response['Marker'])
            for device in response['MFADevices']:
                mfa_devices_all.append(device['SerialNumber'])

        #Deactivating mfa devices
        while len(mfa_devices_all) > 0:
            print("MFA Devices Found! Deactivating mfa devices...")
            device = mfa_devices_all.pop()
            try:
                response = child_iam_client.deactivate_mfa_device(
                UserName=event["UserName"],
                SerialNumber=device
                )
                print(response)
            except Exception as e:
                print(e)
                print("Error in deactivating mfa devices")
                return 1, e, FAILED
        
        #check if iam user has signing certificates
        signing_certificate_ids_all=[]
        response = child_iam_client.list_signing_certificates(UserName=event["UserName"])
        for certificate in response['Certificates']:
            signing_certificate_ids_all.append(certificate['CertificateId'])
        while response["IsTruncated"] == True:
            print("Signing Certificate List Parameter IsTruncated is True")
            response = child_iam_client.list_signing_certificates(
            UserName=event["UserName"],
            Marker=response['Marker'])
            for certificate in response['Certificates']:
                signing_certificate_ids_all.append(certificate['CertificateId'])
        
        #Deleting signing certificates
        while len(signing_certificate_ids_all) > 0:
            print("Signing Certificates Found! Deleting signing certificates...")
            certificate = signing_certificate_ids_all.pop()
            try:
                response = child_iam_client.delete_signing_certificate(
                UserName=event["UserName"],
                CertificateId=certificate
                )
                print(response)
            except Exception as e:
                print(e)
                print("Error in deleting signing certificates")
                return 1, e, FAILED
        
        #check if iam user has ssh public keys
        ssh_public_key_ids_all=[]
        response = child_iam_client.list_ssh_public_keys(UserName=event["UserName"])
        for key in response['SSHPublicKeys']:
            ssh_public_key_ids_all.append(key['SSHPublicKeyId'])
        while response["IsTruncated"] == True:
            print("SSH Public Key List Parameter IsTruncated is True")
            response = child_iam_client.list_ssh_public_keys(
            UserName=event["UserName"],
            Marker=response['Marker'])
            for key in response['SSHPublicKeys']:
                ssh_public_key_ids_all.append(key['SSHPublicKeyId'])

        #Deleting ssh public keys
        while len(ssh_public_key_ids_all) > 0:
            print("SSH Public Keys Found! Deleting ssh public keys...")
            key = ssh_public_key_ids_all.pop()
            try:
                response = child_iam_client.delete_ssh_public_key(
                UserName=event["UserName"],
                SSHPublicKeyId=key
                )
                print(response)
            except Exception as e:
                print(e)
                print("Error in deleting ssh public keys")
                return 1, e, FAILED

        LOGGER.info("Deleting IAM User...")
        response = child_iam_client.delete_user(
            UserName=event["UserName"]
        )
        print(response)
        return 1, response, SUCCESS
    except Exception as e:
        LOGGER.error("Something went wrong during IAM User deletion - '{0}'".format(e))
        return 1, e, FAILED

def non_interactive_user_processing(event):
    """
    function: Assume a role in child account and enables the required infra inside the provided account.
    param: lambda event
    returns: SUCCESS/FAILURE
    """
    try:
        LOGGER.info("Assuming a role in child account:'{0}'".format(event['AccountNumber']))
        session_client = boto3.session.Session()
        sts_master_client = session_client.client('sts')
        iam_arn_string_prefix = "arn:aws:iam::"
        target_account_number = event['AccountNumber']
        child_account_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))
        child_account_role_arn = iam_arn_string_prefix + str(target_account_number) + ":role/AWSControlTowerExecution"
    
        """Assume Role into the child account"""
        child_account_role_creds = sts_master_client.assume_role(RoleArn=child_account_role_arn,RoleSessionName=child_account_session_name)
        child_credentials = child_account_role_creds.get('Credentials')
        child_access_key_id = child_credentials.get('AccessKeyId')
        child_secret_access_key = child_credentials.get('SecretAccessKey')
        child_session_token = child_credentials.get('SessionToken')
        # start a session in child account
        child_assume_role_session = boto3.Session(child_access_key_id, child_secret_access_key,child_session_token)
        # check RequestType
        print("Assumed Role in Child Account, proceeding with processing of request.")
        if event['RequestType'] == 'Add':
            print("Creating User")
            result = create_user(event, child_assume_role_session)
            return result
        elif event['RequestType'] == 'Remove':
            print("Deleting User")
            result = delete_user(event, child_assume_role_session)
            return result
        else:
            LOGGER.error("Invalid RequestType")
            return 1, e, FAILED
    except Exception as e:
        LOGGER.error("Something went wrong in non_interactive_user_processing - '{0}'".format(e))
        return 1, e, FAILED

def invoke_response_lambda(event):
    try:
        LOGGER.info("Invoking response lambda")
        # invoke lambda function
        target_fucntion_name = "platform_noninteractive_user_response"
        lambda_client = session_client.client('lambda', region_name= "us-east-1")
              
        response = lambda_client.invoke(
            FunctionName=target_fucntion_name,
            InvocationType='Event',  # Use 'Event' for asynchronous invocation
            Payload=json.dumps(event)
        )

        print("Lambda Invoke Response:", response)

        return SUCCESS
    except Exception as e:
        LOGGER.error("Something went wrong inside invoke response lambda:'{0}'".format(e))
        notify_operations_automation_failure(event)
        return FAILED

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
            "CustodianMailId": "region",
            "RequestType": "owner_id|image_name",
            "RequestParameter": "<ami owner account id>|<ami_name>",
            "RequestNumber": "RITM*",
            "TRBId": "12345",
            "RequestedDdate": "<time>"
    }
    param: lambda context/runtime
    returns: json response
    """
    try:
        LOGGER.info("Inside the Lambda handler with the event - '{0}'".format(json.dumps(event)))
        RARS_STATUS_CLOSED_INCOMPLETE, child_response_message, child_response_status = non_interactive_user_processing(event)
        LOGGER.info("RARS_STATUS_CLOSED_INCOMPLETE: " + str(RARS_STATUS_CLOSED_INCOMPLETE))
        LOGGER.info("child_response_message: " + str(child_response_message))
        LOGGER.info("child_response_status: " + str(child_response_status))
        if child_response_status == FAILED:
            #checking if request should be marked as closed incomplete
            # call response lambda with RARS STATUS CODE
            if RARS_STATUS_CLOSED_INCOMPLETE == 0:
                event["RARS_status_code"]="4" #status code for request closed incomplete
                event["failure_message"]=child_response_message
                invoke_response= invoke_response_lambda(event)
            elif RARS_STATUS_CLOSED_INCOMPLETE == 1:
                event["RARS_status_code"]="-5" # status code for request pending with automation failure
                response = notify_operations_automation_failure(event,child_response_message)
                event["send_failure_status"]="SUCCESS"
                invoke_response= invoke_response_lambda(event)

            
            
            return RETURN_FAILURE
        # add a record for the request in dynamodb

        
        #send response to the RARS
        elif child_response_status == "SUCCESS":
            print("status is SUCCESS")
            print(child_response_message)
            event["RARS_status_code"]="3" #status code for request closed incomplete
            invoke_response= invoke_response_lambda(event)
            creation_date = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            dynamo_table = dynamodb_resource.Table(database_payer)
            
            table_item = {
                    'UserName': event['UserName'],
                    'AccountNumber': event['AccountNumber'],
                    'RequestNumber': event['RequestNumber'],
                    'AccountName': event['AccountName'],
                    'Requestor':event['RequestorEmail'],
                    'RequestType': event['RequestType'],
                    'ProcessingDateTime': creation_date
            }
            response = dynamo_write(event, table_item, dynamo_table)
            return RETURN_SUCCESS
    except Exception as ex:
        LOGGER.error("Something went wrong inside the Lambda handler'{0}'".format(ex))
        notify_operations_automation_failure(event,ex)
        return RETURN_FAILURE