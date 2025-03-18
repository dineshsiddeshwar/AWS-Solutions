from distutils.log import error
import requests
import msal
import jwt
import cryptography
import cffi
import boto3
from cryptography.hazmat.backends import default_backend
from cryptography import x509
import json
from datetime import datetime
import datetime
import time
import boto3
import base64
import logging
import botocore
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

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
        LOGGER.erro("Encountered error while getting parameters".format(ex))

DYNAMOTABLE = get_ssm_param("IPAWS-SCIM-DYNAMO-TABLE")
Group_Creation_Error = "Group creation failed. Manual intervention required"



def alert_operations(security_group_name, account_name,request_id, message, error_code):
    try:
        ses_client = boto3.client('ses')
        failure_operation_dl_str = get_ssm_param("failure_operation_dl")
        sender_id = get_ssm_param("sender_id")
        body_text = """Hello Team\n The following error occurred during creation of iPAWS Security group """ \
            + """.\n• Security group : """ + str(security_group_name) + " "\
                + """.\n• Account Number """ + str(account_name) + " "\
                    + """.\n• Error : """ + str(message) + " "\
                    + """\nBest Regards,\n AWS Platform Engineering team"""

            # The HTML body of the email.
        if error_code == 422:
                message = "Please pass at least two Shell staff as owners. Try to create the group with at lease 2 shell staffers"
        body_html = body_html = """<html>
                <body>
                <p style="font-family:'Arial Nova'">Hello Team,<p>
                <p></p>
                <p style="font-family:'Arial Nova'">The following error occurred during creation of iPAWS Security Group creattion. Please refer the SOP/ Release Docs / iPAWS User guide for """ + "further action," + """.</p>
                <ul>
                <li style="font-family:'Arial Nova'">Account Number: """ + str(account_name) + """</li>
                </ul>
                <ul>
                <li style="font-family:'Arial Nova'">Request Number: """ + str(request_id) + """</li>
                </ul>
                <ul>
                <li style="font-family:'Arial Nova'">Error: """ + str(security_group_name) + """</li>
                </ul>
                <ul>
                <li style="font-family:'Arial Nova'">Error: """ + str(message) + """</li>
                </ul>
                <p style="font-family:'Arial Nova'"></p>
                <p style="font-family:'Arial Nova'">Thanks,</p>
                <p style="font-family:'Arial Nova'"> AWS Platform Engineering Team.</p>
                </body>
                </html>
            """

        send_mail_response = ses_client.send_email(
            Source= sender_id,
            Destination={
                'ToAddresses': [failure_operation_dl_str]
            },
            Message={
                'Subject': {
                    'Data':' ALERT: iPAWS Group Creation Failed'
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
        print(send_mail_response)
        return send_mail_response
    except Exception as e:
        print(str(e))
        return str(e)





def event_marshall(event):
    """
    method: dress group member to join Shell Corp via IPAWS and store to dynamo
    param: event
    returns: event with group owners to match mandatory requirements of IPAWS
    """
    
    aws_sso_groups_list = []
    association_status = "False"
    account_type = 'EXC'
    return_event = {}

    try:
        dynamo_client = boto3.client('dynamodb')
        now = datetime.datetime.now()
        creation_time = now.hour
        """Parallel step function input is converted to single input."""
        if type(event) == list:
            temp_event = {}
            for every_dict in event:
                temp_event.update(every_dict)
            return_event = temp_event
            LOGGER.info("Converted list of dict to a single dict",return_event)
        else:
            return_event = event
            LOGGER.info("Received a single event intput from the stepfunction", return_event)
        
        if return_event["RequestType"] != "Create":
            return_event["IPAWSStatus"] = "SUCCESS"
            return return_event

        return_event["IPAWSStatus"] = "FAILED"
        account_number = return_event['accountNumber']

        if return_event['ResourceProperties']['Environment'] == 'Public-Production':
            account_type = 'PUB'
        elif return_event['ResourceProperties']['Environment'] == 'Private-Production':
            account_type = 'PVT'
        elif return_event['ResourceProperties']['Environment'] == 'Staging':
            account_type = 'STG'
        elif return_event['ResourceProperties']['Environment'] == 'Hybrid-Account':
            account_type = 'HBD'
        else:
            account_type = 'EXC'
        #Groups to be created in Shell Corp AD
        account_name = '-' + return_event['ResourceProperties']['AccountName'] + '-'
        group_prefix = get_ssm_param("IPAWS-prefix")
        BusinessContributorsName = group_prefix + account_type + account_name + account_number + '-' + 'BusinessContributors'
        BusinessOperatorsName = group_prefix+ account_type + account_name + account_number + '-' + 'BusinessOperators'
        BusinessLimitedOperatorsName = group_prefix + account_type + account_name + account_number + '-' + 'BusinessLimitedOperators'
        BusinessReadOnlyName = group_prefix + account_type + account_name + account_number + '-' + 'BusinessReadOnly'
        BusinessCustomName = group_prefix + account_type + account_name + account_number + '-' + 'BusinessCustom'
        return_event['ShellADBusinessContributors'] = BusinessContributorsName
        return_event['ShellADBusinessOperators'] = BusinessOperatorsName
        return_event['ShellADBusinessLimitedOperators'] = BusinessLimitedOperatorsName
        return_event['ShellADBusinessReadOnlyName'] = BusinessReadOnlyName
        return_event['ShellADBusinessCustomName'] = BusinessCustomName
    
        return_event["iPAWS_Account_Type"] = account_type

        BusinessContributors = return_event['ResourceProperties']['BusinessContributors']
        BusinessOperators = return_event['ResourceProperties']['BusinessOperators']
        BusinessLimitedOperators = return_event['ResourceProperties']['BusinessLimitedOperators']
        BusinessReadOnly = return_event['ResourceProperties']['BusinessReadOnly']
        BusinessCustom = return_event['ResourceProperties']['BusinessCustom']
        
        # check if business Custom role required
        checkCustomRequired = False
        if "NotOpted" not in BusinessCustom:
            checkCustomRequired = True

        #Dynamo column item to be stored
        if checkCustomRequired:
            table_item = {
                    'AccountNumber': {"S": account_number},
                    'AssociationStatus': {"S": association_status},
                    'AccountType':{"S": account_type},
                    'ADBusinessContributorsName': {"S": BusinessContributorsName},
                    'ADBusinessOperatorsName':{"S": BusinessOperatorsName},
                    'ADBusinessLimitedOperatorsName':{"S": BusinessLimitedOperatorsName},
                    'ADBusinessReadOnlyName':{"S": BusinessReadOnlyName},
                    'ADBusinessCustomName':{"S": BusinessCustomName},
                    'IsChecked':{"S": 'False'},
                    'BusinessContributors': {"SS": BusinessContributors},
                    'BusinessOperators': {'SS': BusinessOperators},
                    'BusinessLimitedOperators': {"SS":BusinessLimitedOperators},
                    'BusinessReadOnly': {"SS": BusinessReadOnly},
                    'BusinessCustom': {"SS": BusinessCustom},
                    'CreationTime': {"N": str(creation_time)}
                    }
            LOGGER.info("Writing to Dynamo DB:'{0}'".format(table_item))
            dynamo_response = dynamo_client.put_item(
            TableName= DYNAMOTABLE,
            Item=table_item
            )
        else: 
            table_item = {
                    'AccountNumber': {"S": account_number},
                    'AssociationStatus': {"S": association_status},
                    'AccountType':{"S": account_type},
                    'ADBusinessContributorsName': {"S": BusinessContributorsName},
                    'ADBusinessOperatorsName':{"S": BusinessOperatorsName},
                    'ADBusinessLimitedOperatorsName':{"S": BusinessLimitedOperatorsName},
                    'ADBusinessReadOnlyName':{"S": BusinessReadOnlyName},
                    'IsChecked':{"S": 'False'},
                    'BusinessContributors': {"SS": BusinessContributors},
                    'BusinessOperators': {'SS': BusinessOperators},
                    'BusinessLimitedOperators': {"SS":BusinessLimitedOperators},
                    'BusinessReadOnly': {"SS": BusinessReadOnly},
                    'CreationTime': {"N": str(creation_time)}
                    }
            LOGGER.info("Writing to Dynamo DB:'{0}'".format(table_item))
            dynamo_response = dynamo_client.put_item(
            TableName= DYNAMOTABLE,
            Item=table_item
            )
        if len(BusinessOperators) < 2:
            BusinessOperators.append(BusinessContributors)
        if len(BusinessLimitedOperators) < 2:
            BusinessLimitedOperators.append(BusinessContributors)
        if len(BusinessReadOnly) < 2:
            BusinessReadOnly.append(BusinessContributors)
        if '' in BusinessOperators:
            BusinessOperators.remove("")
        if '' in BusinessLimitedOperators:
            BusinessLimitedOperators.remove("")
        if '' in BusinessReadOnly:
            BusinessReadOnly.remove("")
        if '' in BusinessCustom:
            BusinessCustom.remove("")
        return_event['ResourceProperties']['BusinessContributors']= BusinessContributors
        return_event['ResourceProperties']['BusinessOperators'] = BusinessOperators 
        return_event['ResourceProperties']['BusinessLimitedOperators'] = BusinessLimitedOperators
        return_event['ResourceProperties']['BusinessReadOnly'] = BusinessReadOnly
        return_event['ResourceProperties']['BusinessCustom'] = BusinessCustom
        return_event["IPAWSStatus"] = "SUCCESS"
        return return_event
    except Exception as ex:
        LOGGER.error("Encountered error while marshalling parameters".format(ex))
        return return_event['IPAWSStatus']


def create_groups_ipaws(url,event,headers,group_owners,group_name):
    """
    method: calling IPAWS Post
    param: URI of the IPAWS
    param: request body
    param: header for authentication
    """
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(DYNAMOTABLE)
    IPAWSStatus = "FAILED"
    group_status = {}
    try:
        LOB = event['ResourceProperties']['LOB']
        if LOB == "Global Functions (GF)":
            LOB = "GF"
        elif LOB == "Downstream (DS)":
            LOB = "DS"
        elif LOB == "Project & Technologies":
            LOB = "PT"
        elif LOB == "UP (Upstream)":
            LOB = "UP"
        request_body = {
                "Requestor": event['ResourceProperties']['CustodianUser'],
                "ServiceNowRequestID": event['ResourceProperties']['RequestNo'],
                "Service": "AWAS",
                "BusinessCode": "GF",
                "AssetOperatingEnvironment": "P",
                "GroupDescription": "AWS SSO Group for "+ event['accountNumber'],
                "Subscription":event['subscription_name'],
                "Owners": group_owners,
                "GroupName": group_name
        }
        LOGGER.info("Entered Post with '{0}".format(request_body))
        request_body['Owners'] = group_owners
        request_body["GroupName"] = group_name
        request_response = requests.post(url, data=json.dumps(request_body), headers=headers, timeout= 100000)
        status_code = request_response.status_code
        status_message = request_response.json()
        if status_code != 202:
            LOGGER.info("Something wrong with the creation of security group please refer below response code in IPAWS guide.")
            LOGGER.info("Error code'{0}' and error message is '{1}'".format(status_code,status_message))
            alert_operations(group_name, event['accountNumber'],event['ResourceProperties']['RequestNo'], status_message, status_code)
            group_status = { group_name : "FAILED"}
            return group_status
        resonse_header = request_response.headers
        LOGGER.info("Security Group creation is submitted:'{0}".format(status_message))
        if 'Location' in resonse_header:
            LOGGER.info("Security group creation request is submitted in IPAWS. waiting for 120 seconds to check status")
            status_url = resonse_header['Location']
            time.sleep(120)
            creation_status = requests.get(status_url, headers=headers)
            creation_status_code = creation_status.status_code
            stauts_resposne = creation_status.json()
            if creation_status_code not in {201,202}:
                LOGGER.info("Something wrong with the creation of security group please refer below response code in IPAWS guide.")
                LOGGER.info("Error code'{0}' and error message is '{1}'".format(creation_status_code,stauts_resposne))
                alert_operations(group_name, event['accountNumber'],event['ResourceProperties']['RequestNo'], status_message, creation_status_code)
                group_status = { group_name : "FAILED"}
                return group_status
            if creation_status_code == 202:
                time.sleep(60)
                creation_status = requests.get(status_url, headers=headers)
                creation_status_code = creation_status.status_code
                stauts_resposne = creation_status.json()
                if creation_status_code != 201:
                    alert_operations(group_name, event['accountNumber'],event['ResourceProperties']['RequestNo'], stauts_resposne, creation_status_code)
                    group_status = { group_name : "FAILED"}
                    return group_status
            group_status = {group_name : "SUCCESS"}
            return group_status
            LOGGER.info("Security group creation status and updating the dynamo db table:'{0}'".format(creation_status.json()))
        else:
            LOGGER.info("Security group creation failed. Manual intervention required.")
            return "FAILED"
    except Exception as e:
        LOGGER.error(e)
        return "FAILED"

def make_owners(input):
    """
    method: prepare list of dict of owners to match ipaws requirements
    param: a list of owners
    returns: list of dict of owners
    """
    LOGGER.info("Making owners")
    temp_list = []
    for item in input:
        temp_dict = {"Email":item}
        temp_list.append(temp_dict)
    return temp_list
    

def lambda_handler(event, context):
    """
    author: Shanmukha SP (shanmukhaswamy.p@shell.com)
    method: start of the lambda function to integrate ipaws
    event: get the event from lambda 
    context: runtime environment context of the lambda
    return: success or failure of group creation in azure AD
    """
    try:
        print(json.dumps(event))
        ip = requests.get('https://checkip.amazonaws.com').text.strip()
        LOGGER.info("The traffic is masked with the IP:'{0}'".format(ip))
        s3 = boto3.client('s3')
        modified_event= {}
        iPAWS_reponse = []

        #marshalling event data
        modified_event = event_marshall(event)

        #Update request
        if modified_event["RequestType"] != "Create":
            modified_event["IPAWSStatus"] = "SUCCESS"
            print(json.dumps(modified_event))
            return modified_event
    
        s3_bucket_name =get_ssm_param("IPAWS-Cert-Bucket")
        status = s3.download_file(s3_bucket_name, 'priv-key.pem', '/tmp/cert.pem')
        f = open('/tmp/cert.pem', "rb")
        pem_data = f.read()
        f.close()
        LOGGER.info("Retrieved private key from s3")
    
        LOGGER.info("Initiating Authentication Context")
    
        SPN_ID = get_ssm_param('IPAWS_SPN_ID')
        CERT_AUTHORITY =get_ssm_param('CERT_AUTHORITY')
        CERT_THUMBPRINT = get_ssm_param('CERT_THUMBPRINT')
        CERT_AUTHORITY = get_ssm_param('CERT_AUTHORITY')
        SCOPE = get_ssm_param('SCOPE')

        app = msal.ConfidentialClientApplication(SPN_ID, authority=CERT_AUTHORITY,
        client_credential={"thumbprint":CERT_THUMBPRINT, "private_key":pem_data})
        LOGGER.info("Looking for cached token")
        result = app.acquire_token_silent([SCOPE],account=None)


        if result is None:
            LOGGER.info("Cache-mis: Initiating new token retreival")
            result = app.acquire_token_for_client([SCOPE])
        url = get_ssm_param('IPAWS_URI')
        contributor_owners = make_owners(modified_event['ResourceProperties']['BusinessContributors'])

        headers = {
            'Content-Type': 'Application/json',
            'Authorization': 'Bearer'+ ' ' + result['access_token']}
        group_creation_status = create_groups_ipaws(url,modified_event,headers,contributor_owners,modified_event['ShellADBusinessContributors'])
        if group_creation_status == "FAILED":
            LOGGER.error(Group_Creation_Error)
            modified_event["IPAWSStatus"] = "FAILED"
            return modified_event
        else:
            iPAWS_reponse.append(group_creation_status)
        
        limited_operators_owners = make_owners(modified_event['ResourceProperties']['BusinessLimitedOperators'])
        group_creation_status = create_groups_ipaws(url,modified_event,headers,limited_operators_owners,modified_event['ShellADBusinessLimitedOperators'])
        if group_creation_status == "FAILED":
            LOGGER.error(Group_Creation_Error)
            modified_event["IPAWSStatus"] = "FAILED"
            return modified_event
        else:
            iPAWS_reponse.append(group_creation_status)
        
        limited_operators_owners = make_owners(modified_event['ResourceProperties']['BusinessOperators'])
        group_creation_status = create_groups_ipaws(url,modified_event,headers,limited_operators_owners,modified_event['ShellADBusinessOperators'])
        if group_creation_status == "FAILED":
            LOGGER.error(Group_Creation_Error)
            modified_event["IPAWSStatus"] = "FAILED"
            return modified_event
        else:
            iPAWS_reponse.append(group_creation_status)
        
        limited_operators_owners = make_owners(modified_event['ResourceProperties']['BusinessReadOnly'])
        group_creation_status = create_groups_ipaws(url,modified_event,headers,limited_operators_owners,modified_event['ShellADBusinessReadOnlyName'])
        if group_creation_status == "FAILED":
            LOGGER.error(Group_Creation_Error)
            modified_event["IPAWSStatus"] = "FAILED"
            return modified_event
        else:
            iPAWS_reponse.append(group_creation_status)
        
        if "NotOpted" not in modified_event['ResourceProperties']['BusinessCustom']:
            limited_operators_owners = make_owners(modified_event['ResourceProperties']['BusinessCustom'])
            group_creation_status = create_groups_ipaws(url,modified_event,headers,limited_operators_owners,modified_event['ShellADBusinessCustomName'])
            if group_creation_status == "FAILED":
                LOGGER.error(Group_Creation_Error)
                modified_event["IPAWSStatus"] = "FAILED"
                return modified_event
            else:
                iPAWS_reponse.append(group_creation_status)
            
        modified_event["IPAWSStatus"] = iPAWS_reponse
        print(json.dumps(modified_event))
        return modified_event
    except Exception as ex:
        LOGGER.error("Lambda failed with the error:'{0}'".format(ex))
        return modified_event