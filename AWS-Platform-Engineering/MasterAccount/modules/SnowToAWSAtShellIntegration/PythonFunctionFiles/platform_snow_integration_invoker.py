import boto3
import json
import random
import datetime
import time

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
            queue_url = self.sqs_client.get_queue_url(QueueName="platform_snow_request_box.fifo").get('QueueUrl')
        except Exception as exception:
            print("Exception in Lambda Handler", exception)
        return queue_url

    def CheckAndRetrieveMessage(self, ResultOfAVMRun):
        try:
            print("Inside check and retrieve SQS message...!!")
            queueurl = self.GetQueueURL()
            print("Got queue URL : {}".format(queueurl))
            response = self.sqs_client.receive_message( QueueUrl=queueurl, AttributeNames=['All'], MaxNumberOfMessages= ResultOfAVMRun)
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
                
                
                # if len(delete_response['Successful']) != len(entries):
                #     print("The queue message not deleted hence exits..!!")
                #     exit()
                # else:
                #     print("The queue message is deleted successfully..!!")
                # return response['Messages']   
        except Exception as exception:
            print("There is no message found in queue hence now exits...!! and error message is:", exception)
            exit()

    def CheckIfAVMProvisionRunning(self):
        try:
            account_list = 0
            response = self.servicecatalog_client.search_provisioned_products(Filters={"SearchQuery":["productName:platform_avm_product"]})
            result = response['ProvisionedProducts']
            while 'NextPageToken' in response:
                response = self.servicecatalog_client.search_provisioned_products(Filters={"SearchQuery":["productName:platform_avm_product"]}, PageToken=response['NextPageToken'])
                result.extend(response['ProvisionedProducts'])
            if (result):
                print("avm products results found and now checking the status..!!")
                for item in result:
                    if item['Status'] == 'UNDER_CHANGE' or item['Status'] == 'PLAN_IN_PROGRESS' :
                        account_list += 1
                print(f"{account_list} products are already running. Fetching {5-account_list} to start account creation")
                return 5-account_list
        except Exception as exception:
            print("Exception in Lambda Handler of function CheckIfAVMProvisionRunning and error is : {} ".format(exception))
            return False

    def InvokeStateMachine(self, QueueMesage):
        try:
            RequestNumber = json.loads(QueueMesage)
            print(f"Type of queue message {QueueMesage}")
            print(f"{QueueMesage}")
            step_function_name = RequestNumber['RequestNo'] + '-' + \
                                 str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + \
                                 str(random.randint(1, 1000))
            print("Step function name framed is:{}".format(step_function_name))
            response = self.stepfunction_client.start_execution(
                stateMachineArn='arn:aws:states:us-east-1:{}:stateMachine:platform_snow_integration_state_machine'.format(self.admin_account),
                name=step_function_name,
                input=QueueMesage
            )
            if response :
                print("The response after invoke of step function {}".format(response))
                return response
        except Exception as exception:
            print("Exception occured while invoking the step function and error is {}", exception)

def lambda_handler(event, context):
    try:
        print("inside the handler..")
        sendqueueObject = SendQueueMessageRecieverBox(event, context)
        print("object is created for class SendQueueMessageRecieverBox..")
        ResultOfAVMRun = sendqueueObject.CheckIfAVMProvisionRunning()
        if ResultOfAVMRun :
            print(f"found that {5-ResultOfAVMRun} AVM provision products are already running , hence retrieving {ResultOfAVMRun} messages from the queue...")
            MessageAtQueue = sendqueueObject.CheckAndRetrieveMessage(ResultOfAVMRun)
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
                        exit()
            else:
                print("No messages to process in request queue box, hence exits current cycle..!!!")
                exit()
        else:
            print("AVM provision products are running so onther instance can not be invoked hence exits current cycle..!!!")
            exit()
        print("invoked the queue message..")
    except Exception as exception:
        print(exception)