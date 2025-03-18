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
import string


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
        raise

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

def notify_RARS_SNOW(event, status):
    """
    sned a notification to RARS api about the processing status
    param event: lambda event
    return: {Action_response, success_message|error_message}
    """
    try:
        LOGGER.info("Inside notify_RARS_SNOW")
        if status == "SUCCESS":
            RARS_STATUS_CODE = "3"
            work_notes = "Request has been processed successfully by our automation."
            sc_task_notes = "Request has been completed successfully."
        elif status == "WORK IN PROGRESS":
            RARS_STATUS_CODE = "2"
            work_notes = "Request has been queued by our automation, please wait for further updates."
            sc_task_notes = "platform_TRB_management_payer_result_aggregator has been triggered successfully."
        elif status == "FAILED":
            RARS_STATUS_CODE = "-5"
            work_notes = "An error was encountered in the automation to process this. Please check with the AWS@Shell platform team."
            sc_task_notes = "platform_TRB_management_payer_result_aggregator has failed. Please see Cloudtrail logs for more details."
        api_data = json.loads(get_secret())
        if api_data :
                LOGGER.info("Retrieved AWS secret manager data..")
                Bearer_token_data = get_SIMAAS_BearerToken(api_data['SIMAAS_URL'], api_data['SIMAAS_client_id'], api_data['SIMAAS_client_secret'],api_data['SIMAAS_username'],api_data['SIMAAS_password'])
                if Bearer_token_data :
                    LOGGER.info("SIMAAS bearer toaken is retrieved ...")
                    payload = json.dumps({
                            "u_supplier_reference": event['SCTaskNumber'],
                            "ice4u_target_id": event['SCTaskNumber'],
                            "u_work_notes": sc_task_notes,
                            "u_close_notes": "The request is processed succesfully.",
                            "u_state": RARS_STATUS_CODE,
                            "u_comments": work_notes
                        })
                    headers = { 'Authorization': 'Bearer '+Bearer_token_data['access_token'] , 'Content-Type': 'application/json'}
                    response = requests.request("POST", api_data['RARS_URL'], headers=headers, data=payload)
                    LOGGER.info("called RARS with the payload'{0}' and recieved '{1}'".format(payload,response.status_code))

                    return SUCCESS_RESPONSE , SUCCESS
                else:
                    LOGGER.info("Failed to get SIMAAS bearer toaken...")
                    raise Exception("Failed to get SIMAAS bearer toaken...")
        else:
            LOGGER.info("failed at getting required secrets from AWS secret manager..")
            raise Exception("failed at getting required secrets from AWS secret manager..")
        
    except Exception as exception:
        error_msg = "Exception while sending response to Snow in notify_RARS_SNOW and error is {}".format(exception)
        LOGGER.error(error_msg)
        raise


def trigger_failure_email(event, success_report, failure_report):
    try:
        ses_client = boto3.client('ses')
        titan_dl_str = get_ssm_param("tital_dl")
        sender_id = get_ssm_param("sender_id")
        requestor_email = event.get('RequestorEmailID')

        body_text = (
            "Hello Team,\n"
            "One or more of the bulk request parameters has failed.\n"
            "Best Regards,\n"
            "AWS Platform Engineering team"
        )

        # Convert the failure report to a formatted JSON string
        formatted_failure_json = json.dumps(failure_report, indent=4)

        # Generate table headers and rows for the success and failure reports
        if success_report:
            success_headers = success_report[0].keys()
            success_html_headers = "".join([f"<th>{header}</th>" for header in success_headers])
            success_html_rows = "".join([f"<tr>{''.join([f'<td>{entry[key]}</td>' for key in success_headers])}</tr>" for entry in success_report])
        else:
            success_html_headers = ""
            success_html_rows = "<tr><td>No Successful Events</td></tr>"

        if failure_report:
            failure_headers = failure_report[0].keys()
            failure_html_headers = "".join([f"<th>{header}</th>" for header in failure_headers])
            failure_html_rows = "".join([f"<tr>{''.join([f'<td>{entry[key]}</td>' for key in failure_headers])}</tr>" for entry in failure_report])
        else:
            failure_html_headers = ""
            failure_html_rows = "<tr><td>No Failed Events</td></tr>"

        body_html = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: 'Arial Nova', Arial, sans-serif;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 20px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f2f2f2;
                        color: black;
                    }}
                    tr:nth-child(even) {{
                        background-color: #f9f9f9;
                    }}
                    tr:hover {{
                        background-color: #f1f1f1;
                    }}
                    h3 {{
                        font-family: 'Arial Nova', Arial, sans-serif;
                        color: #333;
                    }}
                    p {{
                        font-family: 'Arial Nova', Arial, sans-serif;
                    }}
                    a {{
                        color: #1a73e8;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                </style>
            </head>
            <body>
                <p>Hello,</p>
                <p>One or more parameters of your AMI Allowlisting Request has FAILED.</p>
                <p>Please find the details of the request below:</p>
                <table>
                    <tr><th>Request</th><td>{event['RequestNumber']}</td></tr>
                    <tr><th>Requestor</th><td>{event['RequestorEmailID']}</td></tr>
                </table>
                <h3>Failed Events:</h3>
                <table>
                    <tr>{failure_html_headers}</tr>
                    {failure_html_rows}
                </table>
                <h3>Successful Events:</h3>
                <table>
                    <tr>{success_html_headers}</tr>
                    {success_html_rows}
                </table>
                <p>Your request has been put on hold due to one or more failures. Kindly reach out to <a href="mailto:{titan_dl_str}">{titan_dl_str}</a> for assistance.</p>
                <p>For raising a new request related to the same catalog, please visit the link:</p>
                <a href="https://shell2.service-now.com/sp?id=sc_cat_item_guide&table=sc_cat_item&sys_id=ae72bdb6db9bec5079c7d18c68961929">Amazon Web Services (AWS)</a>
                <p>For more information related to AWS@Shell platform, please refer to our one-pager:</p>
                <a href="https://devkit.shell.com/content/tools/AWS_at_shell_landing_page">AWS@Shell: All You Will Ever Need To Know</a>
                <p>Thanks,</p>
                <p>AWS Platform Engineering Team.</p>
            </body>
        </html>
        """

        send_mail_response = ses_client.send_email(
            Source=sender_id,
            Destination={
                'ToAddresses': [titan_dl_str, requestor_email]
            },
            Message={
                'Subject': {
                    'Data': f"{event['RequestNumber']}: TRB approved AMI Allow-Listing"
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
        LOGGER.error("An error occurred while sending an alert: '{0}'".format(e))
        raise

def notify_operations_automation_failure(event,e, notify_requestor=False):
    """
    Alerts the team in case of failures.
    :param event: lambda event
    """
    try:
        ses_client = boto3.client('ses')
        titan_dl_str = get_ssm_param("tital_dl")
        sender_id = get_ssm_param("sender_id")
        requestor_email = event.get('RequestorEmailID')
        recipient_list = [titan_dl_str]
        if notify_requestor:
            recipient_list = [titan_dl_str, requestor_email]


        body_text = """Hello Team\n An error occured in TRB approved AMI Allow-Listing Automation""" \
                    + """\nBest Regards,\n AWS Platform Engineering team"""

            # The HTML body of the email.
        body_html = """<html>
                <body>
                <p style="font-family:'Arial Nova'">Hello Team,<p>
                <p></p>
                <p style="font-family:'Arial Nova'">An error occured during TRB approved AMI Allow-Listing processing, automation needs a manual intevention.</p>
                <ul>
                <li style="font-family:'Arial Nova'">Request Number: """ + str(event['RequestNumber']) + """</li>
                <li style="font-family:'Arial Nova'">State Machine: """ + "TRB_AMI_Exception_Management" + """</li>
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
                'ToAddresses': recipient_list
            },
            Message={
                'Subject': {
                    'Data':' ALERT: TRB_AMI_Exception_Management Failed'
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
        raise

def generate_report(event):
    """
    function: generate_failed_report
    param: event
    return: json response

    """
    try:
        failed_report = []
        success_report = []
        for event in event['LambdaResults']:



            if event['statusCode'] == 400:
                failed_report.append(event)
            
            else:

                # success_statement = 'Successfully allowed AMI for account <b>{}</b> in region <b>{}</b> with request type <b>{}</b> and request parameter <b>{}</b>'.format(event['AccountNumber'],event['Region'],event['RequestType'],event['RequestParameter'])
                # success_report.append(success_statement)
                success_report.append(event)


        
        # success_report should contain only unique values

        return failed_report, success_report
    except Exception as ex:
        error_msg = "An error occured during generation of the failed report.'{0}'".format(ex)
        LOGGER.error(error_msg)
        raise

def dump_data_to_ddb(event):
    """
    function: dump_data_to_ddb
    param: event
    return: SUCCESS or FAILED

    """
    try:
        dynamo_table = dynamodb_resource.Table(database_payer)
        request_number = event['RequestNumber']
        requestor_email = event['RequestorEmailID']
        requested_date = event['RequestedDate']

        for event in event['LambdaResults']:
            # get random alphanumeric value
            random.seed(time.time())
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
            hash_key = request_number + "_" + event['AccountNumber'] + "_" + random_str
            table_item = {
                'AccountNumber': event['AccountNumber'],
                'RequestNumber': hash_key,
                'RequestorEmailID' : requestor_email,
                'CustodianMailId':event['CustodianMailId'],
                'RequestParameter': event['RequestParameter'],
                'RequestType': event['RequestType'],
                'CreationTime': requested_date,
                'status': 'active'
                }
            response = dynamo_table.put_item(
                Item=table_item
                )
            status_code = response.get('ResponseMetadata', FAILED_RESPONSE).get('HTTPStatusCode')   
            if status_code != SUCCESS_RESPONSE:
                LOGGER.error("unable to add the item to the dynamodb.'{0}'".format(table_item))
                error_msg = "unable to add the item to the dynamodb."
                return FAILED, error_msg
        return SUCCESS, None
    except Exception as ex:
        error_msg = "An error occured during dynamo record creation.'{0}'".format(ex)
        LOGGER.error(error_msg)
        raise

def validate_operation_success(event):
    """
    function: validate_operation_success
    param: event
    return: SUCCESS or FAILED

    """
    try:
        # check if all invocations were successful
        for event in event['LambdaResults']:
            if event['statusCode'] == 400:
                return FAILED

        return SUCCESS
    except Exception as ex:
        LOGGER.error("An error occured during validation of the operation.'{0}'".format(ex))
        raise

def send_success_email(event, success_report):
    """
    function: send_success_email
    param: success_report
    return: SUCCESS or FAILED
    """
    try:
        ses_client = boto3.client('ses')
        titan_dl_str = get_ssm_param("tital_dl")
        sender_id = get_ssm_param("sender_id")
        custodians = aggregate_custodian(event)

        body_text = """Hello Team\n TRB approved AMI Allow-Listing Request has been successfully processed""" \
                    + """\nBest Regards,\n AWS Platform Engineering team"""

        # Generate table headers and rows for the success report
        if success_report:
            success_headers = success_report[0].keys()
            success_html_headers = "".join([f"<th>{header}</th>" for header in success_headers])
            success_html_rows = "".join([f"<tr>{''.join([f'<td>{entry[key]}</td>' for key in success_headers])}</tr>" for entry in success_report])
        else:
            success_html_headers = ""
            success_html_rows = "<tr><td>No Successful Events</td></tr>"

        # The HTML body of the email.
        body_html = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: 'Arial Nova', Arial, sans-serif;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 20px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f2f2f2;
                        color: black;
                    }}
                    tr:nth-child(even) {{
                        background-color: #f9f9f9;
                    }}
                    tr:hover {{
                        background-color: #f1f1f1;
                    }}
                    h3 {{
                        font-family: 'Arial Nova', Arial, sans-serif;
                        color: #333;
                    }}
                    p {{
                        font-family: 'Arial Nova', Arial, sans-serif;
                    }}
                    a {{
                        color: #1a73e8;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                </style>
            </head>
            <body>
                <p>Hello Team,</p>
                <p>Your TRB approved AMI Allow-Listing Request has been successfully processed.</p>
                <table>
                    <tr><th>Request Number</th><td>{event["RequestNumber"]}</td></tr>
                    <tr><th>Requestor</th><td>{event["RequestorEmailID"]}</td></tr>
                </table>
                <h3>Successful Events:</h3>
                <table>
                    <tr>{success_html_headers}</tr>
                    {success_html_rows}
                </table>
                <p>Thanks,</p>
                <p>AWS Platform Engineering Team.</p>
            </body>
        </html>
        """

        send_mail_response = ses_client.send_email(
            Source=sender_id,
            Destination={
                'ToAddresses': [titan_dl_str],
                'CcAddresses': custodians
            },
            Message={
                'Subject': {
                    'Data': f'{event["RequestNumber"]}: TRB approved AMI Allow-Listing Request Processed'
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
        LOGGER.error("An error occurred while sending an alert in send_success_email: '{0}'".format(e))
        raise
def aggregate_custodian(event):
    """
    function: aggregate_custodian
    param: event
    return: SUCCESS or FAILED

    """
    try:
        custodian_list = []
        for event in event['LambdaResults']:
            custodian_list.append(event['CustodianMailId'])
        return list(set(custodian_list))
    except Exception as ex:

        LOGGER.error("An error occured during aggregation of the custodian.'{0}'".format(ex))
        raise


def lambda_handler(event, context):
    """
    function: Lambda handler
    param: event from the step function
        
    event =  {
            "status": {
            "statusCode": 400,
            "message": "Invalid AWS region names received.",
            "error_lambda": "platform_TRB_management_payer"
        },
        "RequestNumber": "RITM6200403",
        "RequestorEmailID": "Ajoy.Bharath@shell.com",
        "RequestedDate": "2024-07-22 02:33:55",
        "events": [
            {
            "BusinessAccountNumber": "435372135829",
            "Region": "us-east-1",
            "RequestType": "Owner Account ID",
            "RequestParameter": "\"214298875089\",\"442786542162\","
            } ...
        ],
        "LambdaResults": [
            {
            "statusCode": 400,
            "AccountNumber": "435372135829",
            "Region": "us-east-1",
            "RequestType": "Owner Account ID",
            "RequestParameter": "\"214298875089\",\"442786542162\",",
            "CustodianMailId": "s.pilathottathil@shell.com",
            "message": "Request Failed : No AMI found in the child account with the provided payload"
            },
            {
            "statusCode": 200,
            "AccountNumber": "435372135829",
            "Region": "us-east-1",
            "RequestType": "Image Name",
            "RequestParameter": "ShellCorp-GI-RHEL-8.8-dev*,",
            "CustodianMailId": "s.pilathottathil@shell.com",
            "message": "Request Successful"
            },
            {
            "statusCode": 400,
            "AccountNumber": "435372135829",
            "Region": "us-east-1",
            "RequestType": "Image ID",
            "RequestParameter": "ami-09340bb09f6fcac0f",
            "CustodianMailId": "s.pilathottathil@shell.com",
            "message": "Request Failed : No AMI found in the child account with the provided payload"
            },
            {
            "statusCode": 400,
            "AccountNumber": "975050154427",
            "Region": "us-east-1",
            "RequestType": "Owner Account ID",
            "RequestParameter": "\"214298875089\",\"442786542162\",",
            "CustodianMailId": "Ajoy.Bharath@shell.com",
            "message": "Request Failed : No AMI found in the child account with the provided payload"
            },
            {
            "statusCode": 200,
            "AccountNumber": "975050154427",
            "Region": "us-east-1",
            "RequestType": "Image Name",
            "RequestParameter": "ShellCorp-GI-RHEL-8.8-dev*,",
            "CustodianMailId": "Ajoy.Bharath@shell.com",
            "message": "Request Successful"
            },
            {
            "statusCode": 400,
            "AccountNumber": "975050154427",
            "Region": "us-east-1",
            "RequestType": "Image ID",
            "RequestParameter": "ami-09340bb09f6fcac0f",
            "CustodianMailId": "Ajoy.Bharath@shell.com",
            "message": "Request Failed : No AMI found in the child account with the provided payload"
            },
            {
            "statusCode": 400,
            "AccountNumber": "442786542162",
            "Region": "us-east-1",
            "RequestType": "Owner Account ID",
            "RequestParameter": "\"214298875089\",\"442786542162\",",
            "CustodianMailId": "prasanna-kumar.kn@shell.com",
            "message": "Request Failed : No AMI found in the child account with the provided payload"
            },
            {
            "statusCode": 200,
            "AccountNumber": "442786542162",
            "Region": "us-east-1",
            "RequestType": "Image Name",
            "RequestParameter": "ShellCorp-GI-RHEL-8.8-dev*,",
            "CustodianMailId": "prasanna-kumar.kn@shell.com",
            "message": "Request Successful"
            },
            {
            "statusCode": 200,
            "AccountNumber": "442786542162",
            "Region": "us-east-1",
            "RequestType": "Image ID",
            "RequestParameter": "ami-09340bb09f6fcac0f",
            "CustodianMailId": "prasanna-kumar.kn@shell.com",
            "message": "Request Successful"
            },
            {
            "statusCode": 400,
            "AccountNumber": "627968853206",
            "Region": "us-east-1",
            "RequestType": "Owner Account ID",
            "RequestParameter": "\"214298875089\",\"442786542162\",",
            "CustodianMailId": "Partha-Sarathi.Das@shell.com",
            "message": "Request Failed : No AMI found in the child account with the provided payload"
            },
            {
            "statusCode": 200,
            "AccountNumber": "627968853206",
            "Region": "us-east-1",
            "RequestType": "Image Name",
            "RequestParameter": "ShellCorp-GI-RHEL-8.8-dev*,",
            "CustodianMailId": "Partha-Sarathi.Das@shell.com",
            "message": "Request Successful"
            },
            {
            "statusCode": 400,
            "AccountNumber": "627968853206",
            "Region": "us-east-1",
            "RequestType": "Image ID",
            "RequestParameter": "ami-09340bb09f6fcac0f",
            "CustodianMailId": "Partha-Sarathi.Das@shell.com",
            "message": "Request Failed : No AMI found in the child account with the provided payload"
            },
            {
            "statusCode": 400,
            "AccountNumber": "031794792925",
            "Region": "us-east-1",
            "RequestType": "Owner Account ID",
            "RequestParameter": "\"214298875089\",\"442786542162\",",
            "CustodianMailId": "Pavan.A@shell.com",
            "message": "Request Failed : No AMI found in the child account with the provided payload"
            },
            {
            "statusCode": 400,
            "AccountNumber": "031794792925",
            "Region": "us-east-1",
            "RequestType": "Image Name",
            "RequestParameter": "ShellCorp-GI-RHEL-8.8-dev*,",
            "CustodianMailId": "Pavan.A@shell.com",
            "message": "Request Failed : Failed to create event bridge rule in the child account."
            },
            {
            "statusCode": 400,
            "AccountNumber": "031794792925",
            "Region": "us-east-1",
            "RequestType": "Image ID",
            "RequestParameter": "ami-09340bb09f6fcac0f",
            "CustodianMailId": "Pavan.A@shell.com",
            "message": "Request Failed : No AMI found in the child account with the provided payload"
            }
        ]
    }
    param: lambda context/runtime
    returns: json response
    """
    try:
        LOGGER.info("Inside the Lambda handler with the event - '{0}'".format(json.dumps(event)))
        #Enable changes in the child account

        if event['status']['statusCode'] == 400:
            if event['status']['message'] == "Invalid AWS region names received.":
                error_msg = "Invalid AWS region names received in input payload."
                LOGGER.error("Invalid AWS region names received in input payload.")
                notify_operations_automation_failure(event,error_msg, notify_requestor=True)
                notify_RARS_SNOW(event, "FAILED")
                return {
                    'statusCode': 400,
                    'message': "Request Failed:  Error in platform_TRB_management_payer"
                }

        operation_response = validate_operation_success(event)
        RARS_status = "SUCCESS"
        failed_report, success_report = generate_report(event)

        if operation_response == FAILED:

            RARS_status = "FAILED"

            trigger_failure_email(event, success_report, failed_report)

        
        else:

            #write the data to dynamodb

            dump_data_to_ddb(event)

            #send the success report to the RARS
            
            send_success_email(event, success_report)

        notify_RARS_SNOW(event, RARS_status)
        
        return {
        'statusCode': 200,
        'message': "Request Successful"
        }
        
    except Exception as ex:
        LOGGER.error("Something went wrong inside the Lambda handler'{0}'".format(ex))
        notify_RARS_SNOW(event, "FAILED")
        notify_operations_automation_failure(event,ex)
        return {
        'statusCode': 400,
        'message': "Request Failed:  Error in platform_TRB_management_payer_result_aggregator"
        }