import json
import logging
import os
import boto3
import random
import time
from datetime import datetime, timezone

LOGGER = logging.getLogger('logging')
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

SUCCESS = "SUCCESS"
FAILED = "FAILED"

dynamodb_resource = boto3.resource('dynamodb')
database_payer = os.environ['platform_trb_details']

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



def send_expiry_email(item,word):
    """This module will send expiry email to custodian and requestor"""
    try:
        LOGGER.info("Inside Send Email ")
        custodian_id = item['CustodianMailId']
        requestorId = item['RequestorEmailID']
        ses_client = boto3.client('ses')
        titan_dl_str = get_ssm_param("tital_dl")
        sender_id = get_ssm_param("sender_id")  
        body_html =  """<p style="font-family:'Futura Medium'">Dear """ + requestorId + """, </p>
                    <p style="font-family:'Futura Medium'">As per the request """ + item["RequestNumber"] + """, The exception On your Account """ + item["AccountNumber"] + word  + """ . Please raise a new exception Request on <a href=https://servicenow.shell.com/sp?id=sc_cat_item_guide&table=sc_cat_item&sys_id=ae72bdb6db9bec5079c7d18c68961929>Service Now</a> <br> Or else Please let us know if we can Remove the provided Exception from the account </p>
                    <P></p>
                    <p style="font-family:'Futura Medium'">If you have any concerns regarding this email, then please contact us at GX-IDSO-ETSOM-DP-CLOUD-AWS-DEVOPS@shell.com</p>
                    <P></p>
                    <p style="font-family:'Futura Medium'">Best Regards,</p>
                    <p style="font-family:'Futura Medium'">Cloud Services Team</p>
                """
        body_text = """Dear Requestor, \n As per the request """ + item["RequestNumber"] + """ , The exception On your Account """ + item["AccountNumber"] + word  + """ . Please raise a new exception Request on <a href=https://servicenow.shell.com/sp?id=sc_cat_item_guide&table=sc_cat_item&sys_id=ae72bdb6db9bec5079c7d18c68961929>Service Now</a>. <br> Or else Please let us know if we can Remove the provided Exception from the account""" \
                    + """\nBest Regards,\n AWS Platform Engineering team"""
       
        send_mail_response = ses_client.send_email(
            Source= sender_id,
            Destination={
                'ToAddresses': [requestorId],
                'CcAddresses': [titan_dl_str,custodian_id]
            },
            Message={
                'Subject': {
                    'Data': '[ Attention Required ] -' + item["RequestNumber"] + ': Exception Request Is Going to Expire'
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
        if send_mail_response['MessageId']:
           status = 'SUCCESS'
        else:
           status = 'FAILED'
        return status    
    except Exception as exception:
        print("send(..) failed in sending email :- :{} ".format(str(exception)))        
        return FAILED
 
 
def alert_operations(exception):
    try:
        ses_client = boto3.client('ses')
        titan_dl_str = get_ssm_param("tital_dl")
        sender_id = "SITI-CLOUD-SERVICES@shell.com"
        body_text = """Hello Team\n The following error occurred during creation of TRB Management Monitoring Handler """ \
                    + """.\n• Error : """ + str(exception) + " "\
                    + """\nBest Regards,\n AWS Platform Engineering team"""

            # The HTML body of the emai
        body_html = body_html = """<html>
                <body>
                <p style="font-family:'Futura Medium'">Hello Team,<p>
                <p></p>
                <p style="font-family:'Futura Medium'">The following error occurred during creation of TRB Management Monitoring handler. Please check</p>
                <li style="font-family:'Futura Medium'">Error / Exception: """ + str(exception) + """</li>
                </ul>
                <p style="font-family:'Futura Medium'"></p>
                <p style="font-family:'Futura Medium'">Thanks,</p>
                <p style="font-family:'Futura Medium'"> AWS Platform Engineering Team.</p>
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
                    'Data':' [ IMPORTANT ] : TRB Management Monitoring handler Failed'
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


def get_db_items():
    try:
        LOGGER.info("Inside Get Dynamo DB client")
        dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb_resource.Table(database_payer)

        response = table.scan()
        data = response['Items']

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
        LOGGER.info("there are {0} number of items in the DYnamo DB table".format(len(data)))
        
        for item in data:
            if item['status'] != "expired":
                LOGGER.info("Checking the {0} Request now...".format(item['RequestNumber']))
                Creation_date = item['CreationTime']
                status, word  = check_expiration(item['RequestNumber'], Creation_date)
                if status:
                    if word == ' has been expired ':
                        update_response = table.put_item(
                            Item={
                                'RequestNumber':item['RequestNumber'] ,
                                'AccountNumber':item['AccountNumber'],
                                'CreationTime':item['CreationTime'],
                                'CustodianMailId':item['CustodianMailId'],
                                'RequestorEmailID':item['RequestorEmailID'],
                                'RequestParameter':item['RequestParameter'],
                                'status':'expired'})
                        send_status = send_expiry_email(item, word)
                    else:
                        send_status = send_expiry_email(item, word)
                        LOGGER.info("Status of sending email :- ".format(send_status))
            else:
                LOGGER.info("Skipping email ")
        return SUCCESS
    except Exception as exception:
        print("send(..) failed in geting db items list:{} ".format(str(exception)))        
        return FAILED

def check_expiration(request_number, date):
    """this module will check the expiry"""
    try:
        LOGGER.info("Getting check expiration")
        date_format = '%Y-%m-%d'
        date =  date.split(' ')
        date = date[0]
        current_time = datetime.now(timezone.utc)
        current_date = current_time.date()
        LOGGER.info("Todays Date is {0}".format(str(current_date)))
        LOGGER.info("Creation Date is {0}".format(str(date)))
        Requested_date = datetime.strptime(date, date_format)
        diff_days = current_date - Requested_date.date()
        days_elapsed = int(str(diff_days).split(" ")[0])
        days_left = 180 - days_elapsed
        
        LOGGER.info("Number of days left before expiry :- {0}".format(str(days_left)))
        if days_left <= 10:
            if days_left <= 0:
                word = ' has been expired '
                return True, word
            else:
                word = ' is going to Expire in ' + str(days_left) + ' days'
            LOGGER.info("Email can be sent")
            return True, word
        else:
            return False,''
    except Exception as ex:
        LOGGER.error("Encountered error while checking date".format(ex))    
        return False,''


def lambda_handler(event, context):
    """
    This lambda handler will check the status of the provisioned product
    """
    try:
        LOGGER.info("INside lambda handler")
        status =  get_db_items() 
        if status == SUCCESS:
            return True
        else:
            return False
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        alert_operations(exception)
        return False