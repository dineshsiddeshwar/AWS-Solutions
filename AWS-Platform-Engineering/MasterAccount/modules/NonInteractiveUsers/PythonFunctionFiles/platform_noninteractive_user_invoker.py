import json
import logging
import os
import boto3
import datetime
import random
import time

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

class SendQueueMessageRecieverBox(object):

    def __init__(self, event, context):
        self.exception = []
        self.event = event
        self.context = context
        session_client = boto3.session.Session()
        self.sqs_client = session_client.client('sqs', region_name="us-east-1")
        self.lambda_client = session_client.client('lambda', region_name= "us-east-1")
        self.servicecatalog_client = session_client.client('servicecatalog', region_name="us-east-1")
        self.cloudformation_client = session_client.client('cloudformation', region_name="us-east-1")
        self.ssm_client = session_client.client('ssm', region_name="us-east-1")
        response = self.ssm_client.get_parameter(Name="admin_account")
        self.admin_account = response['Parameter']['Value']

    def GetQueueURL(self):
        try:
            queue_url = self.sqs_client.get_queue_url(QueueName="platform_noninteractive_user_snow_request_box.fifo").get('QueueUrl')
        except Exception as exception:
            print("Exception in Lambda Handler", exception)
        return queue_url

    def CheckAndRetrieveMessage(self):
        try:
            print("Inside check and retrieve SQS message...!!")
            queueurl = self.GetQueueURL()
            print("Got queue URL : {}".format(queueurl))
            response = self.sqs_client.receive_message( QueueUrl=queueurl, AttributeNames=['All'], MaxNumberOfMessages= 1)
            print("Got queue recieve message result: {}".format(response))
            if response['Messages']:
                print("There is message found in queue...!!")
                entries = [{'Id': msg['MessageId'], 'ReceiptHandle': msg['ReceiptHandle']} for msg in response['Messages']]
                delete_response = self.sqs_client.delete_message_batch( QueueUrl=queueurl, Entries=entries)
                print(f"deleting response --- {delete_response}")
                
                # print(f"below messages were failed due to below reasons: {delete_response["Failed"]}")
                
                deleted_message_batch  = []
                for messageID in delete_response["Successful"]:

                   for item in response["Messages"]:
                        if messageID["Id"] == item["MessageId"]:
                            deleted_message_batch.append(item)
                print(f"List of succesfully deleted msgs ---- {deleted_message_batch}")
                return deleted_message_batch  
        except Exception as exception:
            print("There is no message found in queue hence now exits...!! and error message is:", exception)
            exit()
    
    
    

    def InvokeUserManagementPayerLambda(self, QueueMesage):
        try:
            RequestNumber = json.loads(QueueMesage)
            print(f"Type of queue message {QueueMesage}")
            print(f"{QueueMesage}")
            LOGGER.info("Invoking response lambda")
            # invoke lambda function
            target_fucntion_name = "platform_noninteractive_user_payer"
            
                
            response = self.lambda_client.invoke(
                FunctionName=target_fucntion_name,
                InvocationType='Event',  # Use 'Event' for asynchronous invocation
                Payload=json.dumps(RequestNumber)
            )

            print("Lambda Invoke Response:", response)

            return response
        except Exception as e:
            LOGGER.error("Something went wrong inside InvokeUserManagementPayerLambda lambda:'{0}'".format(e))
            return False

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

def notify_operations_automation_failure(e):
    """
    Alerts the team in case of failures.
    :param event: lambda event
    """
    try:
        ses_client = boto3.client('ses')
        titan_dl_str = get_ssm_param("tital_dl")
        sender_id = get_ssm_param("sender_id")

        body_text = """Hello Team\n An error occured in Non Interactive User - Invoker Lambda""" \
                    + """\nBest Regards,\n AWS Platform Engineering team"""

            # The HTML body of the email.
        body_html = """<html>
                <body>
                <p style="font-family:'Arial Nova'">Hello Team,<p>
                <p></p>
                <p style="font-family:'Arial Nova'">An error occured during noninteractive user processing, automation needs a manual intevention.</p>
                <li style="font-family:'Arial Nova'">Invoker Account Lambda Name: """ + "platform_noninteractive_user_invoker" + """</li>
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



def lambda_handler(event, context):
    try:
        print("inside the handler..")
        sendqueueObject = SendQueueMessageRecieverBox(event, context)
        
        print("object is created for class SendQueueMessageRecieverBox..")
        MessageAtQueue = sendqueueObject.CheckAndRetrieveMessage()
        print("message queue...............................................:- ", MessageAtQueue)
        if MessageAtQueue :
            for message in MessageAtQueue:
                print("A message found in SQS queue..Now it inovkes payer lambda..!")
                print(f"Invoking payer lambda for message {message}")
                PayerLambdaInvokeResponse = sendqueueObject.InvokeUserManagementPayerLambda(message['Body'])
                if PayerLambdaInvokeResponse :
                    print("Invoked the PayerLambda successfully..!")
                    time.sleep(30)
                else:
                    mesg="Error occured while invoking payer lambda, hence exits current cycle..!!!"
                    print(mesg)
                    notify_operations_automation_failure(mesg)
                    exit()
        else:
            print("No messages to process in request queue box, hence exits current cycle..!!!")
            exit()
    except Exception as exception:
        print(exception)
        notify_operations_automation_failure(exception)