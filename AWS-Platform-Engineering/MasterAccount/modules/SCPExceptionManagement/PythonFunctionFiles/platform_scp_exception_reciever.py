# This lambda was updated as part of RARS Migration from 1.0 to 2.0
import boto3
import logging
import json
import base64
import datetime
import requests

LOGGER = logging.getLogger('logging')
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)
SUCCESS = 'SUCCESS'
FAILED = 'FAILED'
session_client = boto3.session.Session()
secretManager_client = session_client.client('secretsmanager', region_name="us-east-1")

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
        LOGGER.error("Encountered error while getting parameters".format(ex))


def alert_operations(exception,request_id,account_name):
    try:
        ses_client = boto3.client('ses')
        titan_dl_str = get_ssm_param("tital_dl")
        sender_id = "SITI-CLOUD-SERVICES@shell.com"
        body_text = """Hello Team\n The following error occurred during creation of SCP Management Reciever Lambda """ \
                    + """.\n• Error : """ + str(exception) + " "\
                    + """\nBest Regards,\n AWS Platform Engineering team"""

            # The HTML body of the emai
        body_html = body_html = """<html>
                <body>
                <p style="font-family:'Arial Nova'">Hello Team,<p>
                <p></p>
                <p style="font-family:'Arial Nova'">The following error occurred during creation of SCP Management Reciever Lambda.</p>
                <ul>
                <li style="font-family:'Arial Nova'">Account Number: """ + str(account_name) + """</li>
                </ul>
                <ul>
                <li style="font-family:'Arial Nova'">Request Number: """ + str(request_id) + """</li>
                </ul>
                <ul>
                <li style="font-family:'Arial Nova'">Error / Exception: """ + str(exception) + """</li>
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
                'ToAddresses': [titan_dl_str]
            },
            Message={
                'Subject': {
                    'Data':' [ ACTION REQUIRED ] : SCP Exception Management Automation Failed'
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
    

def event_dresser(event):
    """
    This module will format the event
    """
    try:
        if event["Requesttype"] == 'Renewal':
            event["snow_variables"].update({"sh_services_action_allowed":""})
        elif event["Requesttype"] == 'New':
            event["snow_variables"].update({"sh_approved_ticket":""})
        payload = {}
        print(event)
        LOGGER.info("Inside event dresser!!")
        payload = {
            "RequestType": event["Requesttype"],
            "RequestNumber": event["requested_item_number"],
            "task_no": event["task_number"],
            "accountName": event["snow_variables"]["sh_aws_account_name"],
            "accountNumber": event["snow_variables"]["sh_account_id"],
            "actions": event["snow_variables"]["sh_services_action_allowed"],
            "Requested_date": event["snow_variables"]["sh_request_date"],
            "Due_date": event["snow_variables"]["sh_deviation_duration"],
            "old_ritm": event["snow_variables"]["sh_approved_ticket"],
            "requestorName": event["requested_for_email"]
        }
        return payload
    except Exception as exception:
        print("Error inside Event dresser", exception)
        return False


def getQueueURL(sqs_client):
        try:
            queue_url = sqs_client.get_queue_url(QueueName="platform_scp_snow_request_box.fifo").get('QueueUrl')
            print("Queue URL is {}".format(queue_url))
            return queue_url
        except Exception as exception:
            print("Exception in Lambda Handler and error is {}".format(exception))
            return False

def send_sqs_message(message):
    try:
        LOGGER.info("Sending SQS message :- {0}".format(message))
        sqs_client = boto3.client('sqs',region_name='us-east-1')
        queueurl = getQueueURL(sqs_client)
        if queueurl:
            response = sqs_client.send_message(QueueUrl=queueurl, MessageBody=json.dumps(message), MessageGroupId="SnowRequest")
            LOGGER.info("Send result: {}".format(response))
            if response:
                return True
            else:
                return False
    except Exception as exception:
        print("Error inside Send SQS message", exception)
        return False


def get_SIMAAS_BearerToken(url, client_id, client_secret,username,password):
    """
    Generate SIMAAS Bearer Token to authorise to update the RARS task's status
    param url: url of RARS
    param client_id: RARS Client over SIMAAS
    param client_secret: secret to authenticat from the AAD
    """
    try:
        payload='client_id='+client_id+'&client_secret='+client_secret+'&grant_type=password'+'&username='+username+'&password='+password
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.request("POST", url, headers=headers, data=payload)
        bearer_token = json.loads(response.text)
        if bearer_token :
            LOGGER.info("bearer token has been returned...")
            return bearer_token
        else :
            LOGGER.info("No bearer token has been returned...")
            return None
    except Exception as exception:
        LOGGER.error("Exception while getting SIMAAS Bearer token and error is {}".format(exception))
        return None

def get_secret():
    """
    Retrieve secrets from the secrets manager to authenticate to RARS
    """
    secret_name = "IntegrationCreds-RARS"
    try:
        get_secret_value_response = secretManager_client.get_secret_value( SecretId=secret_name)
        if get_secret_value_response:
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                return secret
            else:
                decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
                return decoded_binary_secret
    except Exception as ex:
        LOGGER.error("Something went wrong while reading secrets'{0}".format(ex))
        return None


def notify_RARS_SNOW(event, RARS_STATUS_CODE, close_notes):
    """
    sned a notification to RARS api about the processing status
    param event: lambda event
    return: Null
    """
    try:
        LOGGER.info("Inside notify_RARS_SNOW")
        api_data = json.loads(get_secret())
        if api_data :
                LOGGER.info("Retrieved AWS secret manager data..")
                Bearer_token_data = get_SIMAAS_BearerToken(api_data['SIMAAS_URL'], api_data['SIMAAS_client_id'], api_data['SIMAAS_client_secret'],api_data['SIMAAS_username'],api_data['SIMAAS_password'])
                dynamicnowdata = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S")
                if Bearer_token_data :
                    LOGGER.info("SIMAAS bearer toaken is retrieved ...")
                    payload = json.dumps({
                            "u_supplier_reference": event["task_number"],
                            "ice4u_target_id": event["task_number"],
                            "u_work_notes": "Work Note - Payload processing completed..",
                            "u_close_notes": close_notes,
                            "u_state": RARS_STATUS_CODE,
                            "u_short_description": "",
                            "u_description": "",
                            "u_due_date": dynamicnowdata,
                            "u_comments": "Comments - This catalog is managed by our backend automation system. Please wait for the completion of the request."
                        })
                    headers = { 'Authorization': 'Bearer '+Bearer_token_data['access_token'] , 'Content-Type': 'application/json'}
                    response = requests.request("POST", api_data['RARS_URL'], headers=headers, data=payload)
                    LOGGER.info("called RARS with the payload'{0}' and recieved '{1}'".format(payload,response.status_code))
                    LOGGER.info(response.status_code)
                    return SUCCESS
                else:
                    LOGGER.info("Failed to get SIMAAS bearer toaken...")
                    return FAILED
        else:
            LOGGER.info("failed at getting required secrets from AWS secret manager..")
            return FAILED
    except Exception as exception:
        LOGGER.info("Exception while sending response to Snow and error is {}".format(exception))
        return FAILED    
    
def lambda_handler(event, context):
    """
    Sample Event :-
    {
        "Requesttype": "New" | "Renewal",
        "RequestNumber": "RITM12345",
        "task_no": "SCTASK12344",
        "accountName": "test",
        "accountNumber": "1234",
        "Requested_date": "24-07-2023",
        "actions": "textract:*,inspector:*",
        "Due_date": "24-07-2024",
        "requestorName": "dinesh.siddeshwar@shell.com"
        "exception_req_number": "RITM123345" | ""
    }
    """
    try:
        LOGGER.info("Recieved the event :- {}".format(event))
        if event['snow_variables']['sh_type_of_request'] == 'New Service':
            event.update({"Requesttype": "New"})
        elif event['snow_variables']['sh_type_of_request'] == 'Renew the Existing Service Exception':
            event.update({"Requesttype": "Renewal"})
        else:
            close_notes = "The request failed. Please cehck with the AWS@Shell team."
            notify_RARS_SNOW(event,"-5",close_notes)
            return {
                        'statusCode': 400,
                        'body': json.dumps('Request failed to considered for Exception at AWS@Shell..!')
                }
        modified_event =  event_dresser(event)
        if modified_event:
            sqs_status = send_sqs_message(modified_event)
            if sqs_status:
               LOGGER.info("Sending Message to SQS is successfull")
               close_notes = "Work Note - Payload recieved and currently work in progres"
               notify_RARS_SNOW(event,"2",close_notes)
               return {
                        'statusCode': 200,
                        'body': json.dumps('Request considered for Exception at AWS@Shell..!')
                }
        close_notes = "The request failed. Please cehck with the AWS@Shell team."
        notify_RARS_SNOW(event,"-5",close_notes)
        return {
                        'statusCode': 400,
                        'body': json.dumps('Request failed to considered for Exception at AWS@Shell..!')
                }
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        close_notes = "The request failed. Please cehck with the AWS@Shell team."
        notify_RARS_SNOW(event,"-5",close_notes)
        alert_operations(exception,event["RequestNumber"],event["accountName"])
        return {
                        'statusCode': 400,
                        'body': json.dumps('Request failed to considered for Exception at AWS@Shell..!')
                }