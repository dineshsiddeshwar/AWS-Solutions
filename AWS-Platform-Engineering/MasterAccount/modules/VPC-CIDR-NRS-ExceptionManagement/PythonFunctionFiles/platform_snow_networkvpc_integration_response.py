# This lambda was updated as part of RARS Migration from 1.0 to 2.0
from ast import Return
from cgi import print_directory
import boto3
import json
import datetime
import base64
import requests
from botocore.exceptions import ClientError

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


class SendResponseOfRequests(object):

    def __init__(self, event, context):
        self.exception = []
        self.event = event
        self.context = context
        session_client = boto3.session.Session()
        self.sqs_client = session_client.client('sqs', region_name="us-east-1")
        self.ses_client = session_client.client('ses', region_name="us-east-1")
        self.secretManager_client = session_client.client('secretsmanager', region_name="us-east-1")

   ## Not used code.
    def GetQueueURL(self):
        try:
            queue_url = self.sqs_client.get_queue_url(QueueName="platform_snow_networkvpc_response_box.fifo").get('QueueUrl')
        except Exception as exception:
            print("Exception in Lambda Handler", exception)
        return queue_url

     ## Not used code.
    def CheckAndRetrieveMessage(self):
        try:
            print("Inside check and retrieve SQS message...!!")
            queueurl = self.GetQueueURL()
            print("Got queue URL : {}".format(queueurl))
            response = self.sqs_client.receive_message( QueueUrl=queueurl, AttributeNames=['All'], MaxNumberOfMessages=1)
            print("Send result: {}".format(response))
            if response and response['Messages']:
                print("There is message found in queue...!!")
                entries = [{'Id': msg['MessageId'], 'ReceiptHandle': msg['ReceiptHandle']} for msg in response['Messages']]
                delete_response = self.sqs_client.delete_message_batch( QueueUrl=queueurl, Entries=entries)
                if len(delete_response['Successful']) != len(entries):
                    print("The queue message not deleted hence exits..!!")
                    exit()
                else:
                    print("The queue message is deleted successfully..!!")
                return response['Messages']
            else:
                print("There is no message found in queue hence now it ends the run...!!")
        except Exception as exception:
            print("Exception in Lambda Handler", exception)

    def get_secret(self):
        secret_name = "IntegrationCreds-RARS"
        try:
            get_secret_value_response = self.secretManager_client.get_secret_value( SecretId=secret_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise e
        else:
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                return secret
            else:
                decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
                return decoded_binary_secret

    def get_SIMAAS_BearerToken(self, url, client_id, client_secret,username,password):
        try:
            payload='client_id='+client_id+'&client_secret='+client_secret+'&grant_type=password'+'&username='+username+'&password='+password
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.request("POST", url, headers=headers, data=payload)
            bearer_token = json.loads(response.text)
        except Exception as exception:
            print("Exception while getting SIMAAS Bearer token and error is {}".format(exception))
        else:
            if bearer_token :
                print("bearer token has been returned...")
                return bearer_token
            else :
                print("No bearer token has been returned...")

    def send_Snow_Resonse (self, event):
        try:
            if event['StatusAfterUpdate'] == "AVAILABLE":
                statecode = "3"
                close_notes = "VPC CIDR Extension/Non-Routable subnets request is processed with success status.."
            else:
                statecode = "-5"
                close_notes = "VPC CIDR Extension/Non-Routable subnets is processed with failed status.."
            api_data = json.loads(self.get_secret())
            if api_data :
                print("retrieved AWS secret manager data..")
                Bearer_token_data = self.get_SIMAAS_BearerToken(api_data['SIMAAS_URL'], api_data['SIMAAS_client_id'], api_data['SIMAAS_client_secret'],api_data['SIMAAS_username'],api_data['SIMAAS_password'])
                if Bearer_token_data :
                    print("SIMAAS bearer toaken is retrieved ...")
                    dynamicnowdata = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S")
                    print("dynamic now date is framed..")
                    payload = json.dumps({
                            "u_supplier_reference": event['RequestEventData']['RequestTaskNo'],
                            "ice4u_target_id": event['RequestEventData']['RequestTaskNo'],
                            "u_work_notes": "Work Note - Payload processing completed..",
                            "u_close_notes": close_notes,
                            "u_state": statecode,
                            "u_short_description": event['RequestEventData']['AccountNumber'],
                            "u_description": event['RequestEventData']['AccountName'],
                            "u_due_date": dynamicnowdata,
                            "u_comments": "",
                        })
                    print("payload ->",payload)
                    headers = { 'Authorization': 'Bearer '+Bearer_token_data['access_token'] , 'Content-Type': 'application/json'}
                    print(headers)
                    response = requests.request("POST", api_data['RARS_URL'], headers=headers, data=payload)
                    print(response.status_code)
                    print(response)
                else:
                    print("Failed to get SIMAAS bearer toaken...")
            else:
                print("failed at getting required secrets from AWS secret manager..")
        except Exception as exception:
            print("Exception while sending response to Snow and error is {}".format(exception))
        else:
            if response.status_code :
                print("RARS API response status has been returned and value is:{}".format(response.status_code))
                return response.status_code
            else :
                print("No status code has been returned...")  
                
    def get_custodian(self,accountid):
        """this module will return custodian email id"""
        try:
            print("Getting custodian Email id from DB")
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
            print("Encountered error while getting custoain Email ID",ex)    
            return False
            
    def send_Processed_email(self, event):
        try:
            custodian_id = self.get_custodian(event['ProvisionedProductList'][0]['AccountNumber'])
            print("Sending email now....")
            # The email body for recipients with non-HTML email clients.
            body_text = """
                Hello Team,
                
                AWS@Shell VPC CIDR Extension/Non-routable subnets request is processed now. Below are the processed details and results.          
                    * Account Number : """ + event['ProvisionedProductList'][0]['AccountNumber'] + """
                    * Account Name : """ + event['RequestEventData']['AccountName'] + """
                    * Task : """ + event['RequestEventData']['TaskType'] + """                 
                    * Environment : """ + event['RequestEventData']['VPCType'] + """
                    * Snow Request Task No : """ + event['RequestEventData']['RequestTaskNo'] + """
                    * Snow Request No : """ + event['RequestEventData']['RequestNo'] + """
                    * VPC Id : """ + event['RequestEventData']['VPCId'] + """

                Kindly check your account for the VPC CIDR Extension/ Non-routable Subnets provisioned successfully and let us know if you have any concern or else confirm us to ticket closure.
                
                Best Regards,
                Cloud Services Team
                """

            # The HTML body of the email.
            body_html = """<html>
                <head>
                <style>
                    table, td {
                    border: 1px solid black;
                    border-collapse: collapse;
                    }
                    
                    
                    th {
                    border: 1px solid black;
                    border-collapse: collapse;
                    font-weight: bold
                    }
                    
                    
                    td, th {
                    padding-left: 15px;
                    text-align: left;
                    }
                </style>
                </head>
                <body>
                <p style="font-family:'Futura Medium'">Hello Team,</p>
                <p style="font-family:'Futura Medium'">A AWS@Shell VPC CIDR Extension/Non-routable subnets request is processed now. Below are the processed details and results.</p>
                
                <table style="width:100%">
                    <col style="width:50%">
                    <col style="width:50%">
                  <tr bgcolor="yellow">
                    <td width="50%">Account Property Names</td>
                    <td width="50%">Account Values</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Number</td>
                    <td width="50%">""" + event['ProvisionedProductList'][0]['AccountNumber'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Account Name</td>
                    <td width="50%">""" + event['RequestEventData']['AccountName'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Task</td>
                    <td width="50%">""" + event['RequestEventData']['TaskType'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Environment</td>
                    <td width="50%">""" + event['RequestEventData']['VPCType'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Snow Request Task No</td>
                    <td width="50%">""" + event['RequestEventData']['RequestTaskNo'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">Snow Request No</td>
                    <td width="50%">""" + event['RequestEventData']['RequestNo'] + """</td>
                  </tr>
                  <tr>
                    <td width="50%">VPC Id</td>
                    <td width="50%">""" + event['RequestEventData']['VPCId'] + """</td>
                  </tr>
                </table>

                <p><b>Kindly check your account for the VPC CIDR Extension/ Non-routable Subnets provisioned successfully and let us know if you have any concern or else confirm us to ticket closure.</b></p>
                
                <p style="font-family:'Futura Medium'">Best Regards,</p>
                <p style="font-family:'Futura Medium'">Cloud Services Team</p>
                </body>
                </html>
                """
            # Provide the contents of the email.
            send_mail_response = self.ses_client.send_email(
                Source="SITI-CLOUD-SERVICES@shell.com",
                Destination={
                    'ToAddresses': ["GX-SITI-CPE-Team-Titan@shell.com", custodian_id]
                },
                Message={
                    'Subject': {
                        'Data': event['RequestNo']+": AWS@Shell VPC CIDR Extension/ Non-routable Subnets request processed"

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

def lambda_handler(event, context):
    try:
        print("inside the handler..")
        print("Event recieved from sqs queue.. and below is the event")
        print(event) 
        print(event['Records'][0]['body'])
        if isinstance(event['Records'][0]['body'], str):
            event = json.loads(event['Records'][0]['body'])
            print("Type after conversion is at below...")
            print(type(event))
        else:
            event = json.loads(event['Records'][0]['body'])
            print("Type after conversion is at below...")
            print(type(event))
        sendqueueObject = SendResponseOfRequests(event, context)
        print("object is created for class SendResponseOfRequests..")
        ResponseToSnow = sendqueueObject.send_Snow_Resonse(event)
        if ResponseToSnow :
            print("response is sent back to snow and now sending eamil...")
        else:
            print("failed to send response to snow...")
        SendConsolidatedEmail = sendqueueObject.send_Processed_email(event)
        if SendConsolidatedEmail :
            print("Email sent...")
        else:
            print("failed to send email...")
    except Exception as exception:
        print(exception)