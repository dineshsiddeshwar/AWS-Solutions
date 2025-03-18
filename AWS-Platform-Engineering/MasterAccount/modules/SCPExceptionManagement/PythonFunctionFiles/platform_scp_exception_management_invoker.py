import boto3
import json
import random
import datetime
import time
import logging


LOGGER = logging.getLogger('logging')
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

class SendQueueMessageRecieverBox(object):

    def __init__(self, event, context):
        self.exception = []
        self.event = event
        self.context = context
        session_client = boto3.session.Session()
        self.sqs_client = session_client.client('sqs', region_name="us-east-1")
        self.servicecatalog_client = session_client.client('servicecatalog', region_name="us-east-1")
        self.cloudformation_client = session_client.client('cloudformation', region_name="us-east-1")
        self.stepfunction_client = session_client.client('stepfunctions', region_name="us-east-1")
        self.ssm_client = session_client.client('ssm', region_name="us-east-1")
        response = self.ssm_client.get_parameter(Name="admin_account")
        self.admin_account = response['Parameter']['Value']

    def GetQueueURL(self):
        try:
            queue_url = self.sqs_client.get_queue_url(QueueName="platform_scp_snow_request_box.fifo").get('QueueUrl')
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
    
    
    def get_control_tower_product_count(self):
        """This module will check if there are more than 8 control tower product under change"""
        try:
            count = 0
            print("Inside get control tower product method")
            control_tower_response = self.servicecatalog_client.search_provisioned_products(Filters={"SearchQuery":["productName:AWS Control Tower Account Factory"]})
            result = control_tower_response['ProvisionedProducts']
            while 'NextPageToken' in control_tower_response:
                sc_response = self.servicecatalog_client.search_provisioned_products(Filters={"SearchQuery":["productName:AWS Control Tower Account Factory"]}, PageToken=control_tower_response['NextPageToken'])
                result.extend(sc_response['ProvisionedProducts'])
            if (result):
                for item in result:
                    if item['Status'] == 'UNDER_CHANGE':
                        count +=1
            else:
                count = -1
            return count
        except Exception as exception:
            print("There is no message found in queue hence now exits...!! and error message is:", exception)
            return -1

    def InvokeStateMachine(self, QueueMesage):
        try:
            RequestNumber = json.loads(QueueMesage)
            print(f"Type of queue message {QueueMesage}")
            print(f"{QueueMesage}")
            step_function_name = RequestNumber['RequestNumber'] + '-' + \
                                 str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + '-' + RequestNumber['accountName'] + '-' + RequestNumber['accountNumber'] + \
                                 str(random.randint(1, 1000))
            print(step_function_name)
            if len(step_function_name) > 80:
                step_function_name = step_function_name[:80]
            print("Step function name framed is:{}".format(step_function_name))
            response = self.stepfunction_client.start_execution(
                stateMachineArn='arn:aws:states:us-east-1:{}:stateMachine:platform_SCPStatemachine'.format(self.admin_account),
                name=step_function_name,
                input=QueueMesage
            )
            if response :
                print("The response after invoke of step function {}".format(response))
                return response
            else:
                return False
        except Exception as exception:
            print("Exception occured while invoking the step function and error is {}", exception)
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

def alert_operations():
    try:
        ses_client = boto3.client('ses')
        titan_dl_str = get_ssm_param("tital_dl")
        sender_id = "SITI-CLOUD-SERVICES@shell.com"
        body_text = """Hello Team\n Theere an error occurred during SCP management invoking """ \
                    + """\nBest Regards,\n AWS Platform Engineering team"""

            # The HTML body of the emai
        body_html = body_html = """<html>
                <body>
                <p style="font-family:'Arial Nova'">Hello Team,<p>
                <p></p>
                <p style="font-family:'Arial Nova'">There is an error occurred during invoking SCP Management Invoker.</p>
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
                    'Data':' [ ACTION REQUIRED ] : SCP Exception Management Automation Failed at Invoker stage'
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
        sendqueueObject = SendQueueMessageRecieverBox(event, context)
        print("Checking if account control tower product is running or not.....")
        count = sendqueueObject.get_control_tower_product_count()
        if count != -1:
            print("There is failure in checking control tower product status")
            return event
        elif count == 0 or count > 8:
            print("There are more than 8 control product running. Hence cannot trigger automation. Check in the next iteration")
            return event
        else:
            print("There are less than 8 under change product . hence triggering the automation")
        print("object is created for class SendQueueMessageRecieverBox..")
        MessageAtQueue = sendqueueObject.CheckAndRetrieveMessage()
        print("message queue...............................................:- ", MessageAtQueue)
        if MessageAtQueue :
            for message in MessageAtQueue:
                print("A message found in SQS queue..Now it inovkes step function..!")
                print(f"Invoking step for message {message}")
                StepfunctionInvokeResponse = sendqueueObject.InvokeStateMachine(message['Body'])
                if StepfunctionInvokeResponse :
                    print("Invoked the step functions successfully..!")
                    time.sleep(30)
                else:
                    print("Error occured while inviking step function, hence exits current cycle..!!!")
                    alert_operations()
                    exit()
        else:
            print("No messages to process in request queue box, hence exits current cycle..!!!")
            alert_operations()
            exit()
    except Exception as exception:
        print(exception)