# This lambda was updated as part of RARS Migration from 1.0 to 2.0
import json
import logging
import boto3
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

session_client = boto3.session.Session()
secretManager_client = session_client.client('secretsmanager', region_name="us-east-1")

SUCCESS = 'SUCCESS'
FAILED = 'FAILED'

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
        LOGGER.error("Encountered error while getting parameters".format(ex))

def trigger_success_email_create(event):
    try:
        ses_client = boto3.client('ses')
        titan_dl_str = get_ssm_param("tital_dl")
        sender_id = get_ssm_param("sender_id")
        requestor_email = event['RequestorEmail']

        body_text = """Hello Team\n AWS Account - User Access Management (IAM) - <User-Create> has been processed successfully""" \
                    + """\nBest Regards,\n AWS Platform Engineering team"""

            # The HTML body of the email.
        body_html = """<html>
                        <body>
                            <p style="font-family:'Arial Nova'">Hello,</p>
                            <p style="font-family:'Arial Nova'"></p>
                            <p style="font-family:'Arial Nova'">Your request item {} created for AWS Account - User Access Management (IAM) - <User-Create> has been processed successfully.</p>
                            <p style="font-family:'Arial Nova'">Please find the details of the request below:</p>
                            <ul>
                            <li style="font-family:'Arial Nova'">AWS@Shell Account Name: {}</li>
                            <li style="font-family:'Arial Nova'">AWS@Shell Account Number: {}</li>
                            <li style="font-family:'Arial Nova'">Username: {}</li>
                            <li style="font-family:'Arial Nova'">RequestType: {}</li>
                            </ul>
                            <p style="font-family:'Arial Nova'"></p>
                            <p style="font-family:'Arial Nova'">Please proceed to create/download the access and secret keys for the newly created user yourself. It is also important to manage and rotate the access keys regularly with a recommended frequency of at least one rotation every 90 days.</p>
                            <p style="font-family:'Arial Nova'">You may also proceed to attach any required inline or managed policies to the newly created IAM user yourself.</p>
                            <p style="font-family:'Arial Nova'">For detailed information on access key rotation and other guidelines on securing AWS non-interactive users, please refer to the AWS documentation:</p>
                            <a href="https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html">AWS Identity and Access Management (IAM) Best Practices</a>
                            
                            <p style="font-family:'Arial Nova'"></p>
                            <p style="font-family:'Arial Nova'">Caution: Remember that if your AccessKey/SecretKey gets exposed to public Github or internet, there would be no firewall that can stop the compromise of the account. Hence, it is very important to  store these credentials only at Shell Approved places (Secrets Manager/Vault/Github Secrets within sede-x or so/Azure Vault).</p>
                            <p style="font-family:'Arial Nova'">For more information related to AWS@Shell platform, please refer to the our one-pager:</p>
                            <a href="https://devkit.shell.com/content/tools/AWS_at_shell_landing_page">AWS@Shell: All You Will Ever Need To Know</a>

                            <p style="font-family:'Arial Nova'">Thanks,</p>
                            <p style="font-family:'Arial Nova'">AWS Platform Engineering Team.</p>
                        </body>
                        </html>
                        """.format(event['RequestNumber'],event['AccountName'],event['AccountNumber'],event['UserName'],event['RequestType'])


        send_mail_response = ses_client.send_email(
            Source= sender_id,
            Destination={
                'ToAddresses': [titan_dl_str,requestor_email] # replace with titan_dl_str
            },
            Message={
                'Subject': {
                    'Data':'{}: AWS Account - User Access Management (IAM) - <User-Create>'.format(event['RequestNumber'])
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
    

def trigger_success_email_delete(event):
    try:
        ses_client = boto3.client('ses')
        titan_dl_str = get_ssm_param("tital_dl")
        sender_id = get_ssm_param("sender_id")
        requestor_email = event['RequestorEmail']

        body_text = """Hello Team\n AWS Account - User Access Management (IAM) - <User-Delete> has been processed successfully""" \
                    + """\nBest Regards,\n AWS Platform Engineering team"""

            # The HTML body of the email.
        body_html = """<html>
                        <body>
                            <p style="font-family:'Arial Nova'">Hello,</p>
                            <p style="font-family:'Arial Nova'"></p>
                            <p style="font-family:'Arial Nova'">Your request item {} created for AWS Account - User Access Management (IAM) - <User-Delete> has been processed successfully.</p>
                            <p style="font-family:'Arial Nova'">Please find the details of the request below:</p>
                            <ul>
                            <li style="font-family:'Arial Nova'">AWS@Shell Account Name: {}</li>
                            <li style="font-family:'Arial Nova'">AWS@Shell Account Number: {}</li>
                            <li style="font-family:'Arial Nova'">Username: {}</li>
                            <li style="font-family:'Arial Nova'">RequestType: {}</li>
                            </ul>
                            
                            <p style="font-family:'Arial Nova'"></p>
                            <p style="font-family:'Arial Nova'">For more information related to AWS@Shell platform, please refer to the our one-pager:</p>
                            <a href="https://devkit.shell.com/content/tools/AWS_at_shell_landing_page">AWS@Shell: All You Will Ever Need To Know</a>

                            <p style="font-family:'Arial Nova'">Thanks,</p>
                            <p style="font-family:'Arial Nova'">AWS Platform Engineering Team.</p>
                        </body>
                        </html>
                        """.format(event['RequestNumber'],event['AccountName'],event['AccountNumber'],event['UserName'],event['RequestType'])


        send_mail_response = ses_client.send_email(
            Source= sender_id,
            Destination={
                'ToAddresses': [titan_dl_str,requestor_email] # replace with titan_dl_str
            },
            Message={
                'Subject': {
                    'Data':'{}: AWS Account - User Access Management (IAM) - <User-Delete>'.format(event['RequestNumber'])
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
    

def trigger_failure_email(event):
    try:
        ses_client = boto3.client('ses')
        titan_dl_str = get_ssm_param("tital_dl")
        sender_id = get_ssm_param("sender_id")
        requestor_email = event['RequestorEmail']

        body_text = """Hello Team\n AWS Account - User Access Management (IAM) has failed due to wrong input.""" \
                    + """\nBest Regards,\n AWS Platform Engineering team"""

            # The HTML body of the email.
        body_html = """<html>
                        <body>
                            <p style="font-family:'Arial Nova'">Hello,</p>
                            <p style="font-family:'Arial Nova'"></p>
                            <p style="font-family:'Arial Nova'">Your request item {} created for AWS Account - User Access Management (IAM) has failed due to wrong input.</p>
                            <p style="font-family:'Arial Nova'">Please find the details of the request below:</p>
                            <ul>
                            <li style="font-family:'Arial Nova'">AWS@Shell Account Name: {}</li>
                            <li style="font-family:'Arial Nova'">AWS@Shell Account Number: {}</li>
                            <li style="font-family:'Arial Nova'">Username Provided: {}</li>
                            <li style="font-family:'Arial Nova'">RequestType: {}</li>
                            <li style="font-family:'Arial Nova'">Processing Comments: {}</li>
                            </ul>
                            <p style="font-family:'Arial Nova'"></p>
                            <p style="font-family:'Arial Nova'">Your request has been cancelled. Kindly raise a new request with proper inputs.</p>
                            <p style="font-family:'Arial Nova'">For raising a new request related to the same catalog, please visit the link:</p>
                            <a href="https://shell2.service-now.com/sp?id=sc_cat_item_guide&table=sc_cat_item&sys_id=ae72bdb6db9bec5079c7d18c68961929">Amazon Web Services (AWS)</a>
                            
                            <p style="font-family:'Arial Nova'"></p>
                            <p style="font-family:'Arial Nova'">For more information related to AWS@Shell platform, please refer to the our one-pager:</p>
                            <a href="https://devkit.shell.com/content/tools/AWS_at_shell_landing_page">AWS@Shell: All You Will Ever Need To Know</a>

                            <p style="font-family:'Arial Nova'">Thanks,</p>
                            <p style="font-family:'Arial Nova'">AWS Platform Engineering Team.</p>
                        </body>
                        </html>
                        """.format(event['RequestNumber'],event['AccountName'],event['AccountNumber'],event['UserName'],event['RequestType'],event['failure_message'])


        send_mail_response = ses_client.send_email(
            Source= sender_id,
            Destination={
                'ToAddresses': [titan_dl_str,requestor_email] # replace with titan_dl_str
            },
            Message={
                'Subject': {
                    'Data':'{}: AWS Account - User Access Management (IAM)'.format(event['RequestNumber'])
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
        
def notify_operations_automation_failure(event,e):
    """
    Alerts the team in case of failures.
    :param event: lambda event
    """
    try:
        ses_client = boto3.client('ses')
        titan_dl_str = get_ssm_param("tital_dl")
        sender_id = get_ssm_param("sender_id")

        body_text = """Hello Team\n An error occured in Non Interactive User - Response Lambda""" \
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
                <li style="font-family:'Arial Nova'">Response Lambda Name: """ + "platform_noninteractive_user_response" + """</li>
                <li style="font-family:'Arial Nova'">Error / Exception: """ + str(e) + """</li>
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
                if Bearer_token_data :
                    LOGGER.info("SIMAAS bearer toaken is retrieved ...")
                    payload = json.dumps({
                            "u_supplier_reference": event['SCTaskNumber'],
                            "ice4u_target_id": event['SCTaskNumber'],
                            "u_work_notes": "Work Note - Payload processing completed - " + close_notes,
                            "u_close_notes": close_notes,
                            "u_state": RARS_STATUS_CODE,
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
    function: Lambda handler
    param: lambda context/runtime
    returns: json response
    """
    try:
        LOGGER.info("Recieved the event - '{0}'".format(event))
        if event['RARS_status_code'] == "3":
            msg="Request processed successfully and hence sending success email"
            LOGGER.info(msg)
            res= notify_RARS_SNOW(event,event['RARS_status_code'],msg)
            if event['RequestType'] == "Add":
                res = trigger_success_email_create(event)
                return RETURN_SUCCESS
            elif event['RequestType'] == "Remove":
                res = trigger_success_email_delete(event)
                return RETURN_SUCCESS
        
        elif event['RARS_status_code'] == "-5":
            msg="Request processing failed due to automation failure!"
            LOGGER.info(msg)
            if 'send_failure_status' in event.keys() and event['send_failure_status'] == "SUCCESS":
              LOGGER.info("Failure email has already send and hence returning -5")
              close_notes = "The request failed. Please check with the AWS@Shell team."
              res= notify_RARS_SNOW(event,event['RARS_status_code'],msg)
              return RETURN_FAILURE
        
        elif event['RARS_status_code'] == "4":
            msg="Request processing failed due to wrong user input!"
            LOGGER.info(msg)
            response=notify_RARS_SNOW(event,event['RARS_status_code'],msg)
            res = trigger_failure_email(event)
            return RETURN_FAILURE


    except Exception as ex:
        LOGGER.error("Something went wrong inside the Lambda handler'{0}'".format(ex))
        notify_operations_automation_failure(event,ex)
        return RETURN_FAILURE