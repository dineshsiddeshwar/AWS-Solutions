# This lambda was updated as part of RARS Migration from 1.0 to 2.0
from ast import Return
import boto3
import json
import os
import datetime
import base64
import requests
from botocore.exceptions import ClientError

class SendQueueMessageRecieverBox(object):
    def __init__(self, event, context):
        self.exception = []
        self.event = event
        self.context = context
        session_client = boto3.session.Session()
        self.sqs_client = session_client.client('sqs', region_name="us-east-1")
        self.secretManager_client = session_client.client('secretsmanager', region_name="us-east-1")
        self.s3_client = boto3.resource('s3')
        SSM_client = session_client.client('ssm', region_name="us-east-1")
        snow_integration_log_bucket  = SSM_client.get_parameter(Name='SnowNerworkVPCIntegrationLogBucket')
        self.snow_integration_log_bucket = snow_integration_log_bucket['Parameter']['Value']

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

    def send_Snow_Response (self, event):
        try:
            api_data = json.loads(self.get_secret())
            if api_data :
                print("retrieved AWS secret manager data..")
                Bearer_token_data = self.get_SIMAAS_BearerToken(api_data['SIMAAS_URL'], api_data['SIMAAS_client_id'], api_data['SIMAAS_client_secret'],api_data['SIMAAS_username'],api_data['SIMAAS_password'])
                if Bearer_token_data :
                    print("SIMAAS bearer toaken is retrieved ...")
                    dynamicnowdata = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S")
                    print("dynamic now date is framed..")
                    payload = json.dumps({
                            "u_supplier_reference": event['task_number'],
                            "ice4u_target_id": event['task_number'],
                            "u_work_notes": "Work Note - Payload recieved and currently work in progress",
                            "u_close_notes": "",
                            "u_state": "2",
                            "u_short_description": "",
                            "u_description": "",
                            "u_due_date": dynamicnowdata,
                            "u_comments": ""
                        })
                    headers = { 'Authorization': 'Bearer '+Bearer_token_data['access_token'] , 'Content-Type': 'application/json'}
                    response = requests.request("POST", api_data['RARS_URL'], headers=headers, data=payload)
                else:
                    print("Failed to get SIMAAS bearer toaken...")
            else:
                print("failed at getting required secrets from AWS secret manager..")
        except Exception as exception:
            print("Exception while sending response to Snow and error is {}".format(exception))
        else:
            if response.status_code :
                print("bearer API resposne status has been returned and value is:{}".format(response.status_code))
                return response.status_code
            else :
                print("No status code has been returned...")  

    def getQueueURL(self):
        try:
            queue_url = self.sqs_client.get_queue_url(QueueName="platform_snow_networkvpc_request_box.fifo").get('QueueUrl')
            print("Queue URL is {}".format(queue_url))
        except Exception as exception:
            print("Exception in Lambda Handler and error is {}".format(exception))
        return queue_url

    def CreateRecordInS3bucket(self, event):
        print("Recording with event {}".format(event))
        try:
            print("Inside function to create the dynamic .json file...")
            dynamicfilename = datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
            print("filename format created is {}".format(dynamicfilename))
            file_name =  dynamicfilename + "_payload.json"
            print("file name is {}".format(file_name))
            s3_file_name =  event['RequestTaskNo'] + "/" + file_name
            print("s3 bucket path in bucket snow-networkvpc-integration-logs would be  {}".format(s3_file_name))
            local_file_path = "/tmp/payload.json"
            print("file path:{}".format(local_file_path))
            with open(local_file_path, 'w') as fp:
                json.dump(event, fp)
            print("event is stored in local json file")
            self.s3_client.meta.client.upload_file(local_file_path,self.snow_integration_log_bucket, s3_file_name)
            print("file uploaded successfully..")
            os.remove(local_file_path)
            print("File deleted after upload to s3 bucket")
        except Exception as exception:
            print("Exception in Lambda Handler and error is {}".format(exception))

    def ValidateCreatequeueMessage(self, event):
        print("Message recieved from Snow and body is {}".format(event))
        try:
            print("Framing the reciever queue message..")
            if event['snow_variables']['sh_request_type'] == "VPC Extension" and event['snow_variables']['sh_vpc_type'] == "Private":
                print("This is VPC Extension request for Private hence processing for vpc cidr extension")
                if event['snow_variables']['sh_request_type'] == "VPC Extension":
                    OperationType = "Update"
                if event['snow_variables']['sh_region_private'] == "N Virginia (us-east-1)" :
                    NVirginiaValue =  "32" if event['snow_variables']['sh_vpc_size_creation'] == "Small (32)" else ("64" if event['snow_variables']['sh_vpc_size_creation'] == "Medium (64)"  else ("128" if event['snow_variables']['sh_vpc_size_creation'] == "Large (128)"  else "256" ))
                else :
                    NVirginiaValue = "No-VPC"
                if event['snow_variables']['sh_region_private'] == "Ireland (eu-west-1)" :
                    IrelandValue =  "32" if event['snow_variables']['sh_vpc_size_creation'] == "Small (32)" else ("64" if event['snow_variables']['sh_vpc_size_creation'] == "Medium (64)"  else ("128" if event['snow_variables']['sh_vpc_size_creation'] == "Large (128)"  else "256" ))
                else :
                    IrelandValue = "No-VPC"
                if event['snow_variables']['sh_region_private'] == "Singapore (ap-southeast-1)" :
                    SingaporeValue =  "32" if event['snow_variables']['sh_vpc_size_creation'] == "Small (32)" else ("64" if event['snow_variables']['sh_vpc_size_creation'] == "Medium (64)"  else ("128" if event['snow_variables']['sh_vpc_size_creation'] == "Large (128)"  else "256" ))
                else :
                    SingaporeValue = "No-VPC"
                    
                RecieverBoxQueuemessage = {
                    "AccountNumber": event['snow_variables']['sh_aws_account_id'],
                    "AccountName": event['snow_variables']['sh_aws_subscription_name_var'],
                    "RequestTaskNo": event['task_number'],
                    "RequestNo": event['requested_item_number'],
                    "VPCType": event['snow_variables']['sh_vpc_type'],
                    "NVirginia": NVirginiaValue,
                    "Ireland":IrelandValue,
                    "Singapore": SingaporeValue,
                    "RequestType": OperationType,
                    "TaskType": "VPC Extension",
                    "VPCId": event['snow_variables']['sh_vpc_id']
                   }
                print("vpc extension request message for private account is framed now ...")
            
            elif event['snow_variables']['sh_request_type'] == "VPC Extension" and event['snow_variables']['sh_vpc_type'] == "Hybrid":
                print("This is VPC Extension request for Hybrid hence processing for vpc cidr extension")
                if event['snow_variables']['sh_request_type'] == "VPC Extension":
                    OperationType = "Update"
                if event['snow_variables']['sh_region_private'] == "N Virginia (us-east-1)" :
                    NVirginiaValue =  "64" if event['snow_variables']['sh_vpc_size_hybrid'] == "Medium (64)"  else ("128" if event['snow_variables']['sh_vpc_size_creation'] == "Large (128)"  else "256" )
                else :
                    NVirginiaValue = "No-VPC"
                if event['snow_variables']['sh_region_private'] == "Ireland (eu-west-1)" :
                    IrelandValue =  "64" if event['snow_variables']['sh_vpc_size_hybrid'] == "Medium (64)"  else ("128" if event['snow_variables']['sh_vpc_size_creation'] == "Large (128)"  else "256" )
                else :
                    IrelandValue = "No-VPC"
                if event['snow_variables']['sh_region_private'] == "Singapore (ap-southeast-1)" :
                    SingaporeValue =  "64" if event['snow_variables']['sh_vpc_size_hybrid'] == "Medium (64)"  else ("128" if event['snow_variables']['sh_vpc_size_creation'] == "Large (128)"  else "256" )
                else :
                    SingaporeValue = "No-VPC"
                    
                RecieverBoxQueuemessage = {
                    "AccountNumber": event['snow_variables']['sh_aws_account_id'],
                    "AccountName": event['snow_variables']['sh_aws_subscription_name_var'],
                    "RequestNo": event['requested_item_number'],
                    "RequestTaskNo": event['task_number'],
                    "VPCType": event['snow_variables']['sh_vpc_type'],
                    "NVirginia": NVirginiaValue,
                    "Ireland":IrelandValue,
                    "Singapore": SingaporeValue,
                    "RequestType": OperationType,
                    "TaskType": "VPC Extension",
                    "VPCId": event['snow_variables']['sh_vpc_id']
                }
                print("vpc extension request message for hybrid account is framed now ...")        
            
            elif event['snow_variables']['sh_request_type'] == "Non-routable subnets for existing VPC" and event['snow_variables']['sh_vpc_type_non_rou'] == "Private":
                print("This is Non Routable subnet creation request for Private hence processing for vpc cidr extension")
                if event['snow_variables']['sh_request_type'] == "Non-routable subnets for existing VPC":
                    OperationType = "Update"
                RecieverBoxQueuemessage = {
                    "AccountNumber": event['snow_variables']['sh_aws_account_id'],
                    "AccountName": event['snow_variables']['sh_aws_subscription_name_var'],
                    "RequestNo": event['requested_item_number'],
                    "RequestTaskNo": event['task_number'],
                    "RequestType": OperationType,
                    "VPCType": event['snow_variables']['sh_vpc_type_non_rou'],
                    "TaskType": "Non-routable subnets for existing VPC",
                    "VPCId": event['snow_variables']['sh_vpc_id']
                }
                print("non routable subnet creation request message for private account is framed now ...")

            elif event['snow_variables']['sh_request_type'] == "Non-routable subnets for existing VPC" and event['snow_variables']['sh_vpc_type_non_rou'] == "Hybrid":
                print("This is Non Routable subnet creation request for Hybrid hence processing for vpc cidr extension")
                if event['snow_variables']['sh_request_type'] == "Non-routable subnets for existing VPC":
                    OperationType = "Update"
                RecieverBoxQueuemessage = {
                    "AccountNumber": event['snow_variables']['sh_aws_account_id'],
                    "AccountName": event['snow_variables']['sh_aws_subscription_name_var'],
                    "RequestNo": event['requested_item_number'],
                    "RequestTaskNo": event['task_number'],
                    "VPCType": event['snow_variables']['sh_vpc_type_non_rou'],
                    "RequestType": OperationType,
                    "TaskType": "Non-routable subnets for existing VPC",
                    "VPCId": event['snow_variables']['sh_vpc_id']
                }
                print("non routable subnet creation request message for hybrid account is framed now ...")    
            else :
                print ("Unknow request from Snow form hence exiting....")
                exit()
            return RecieverBoxQueuemessage
        except Exception as exception:
            print("Exception in Lambda Handler and error is {}".format(exception))

    def recordAqueueMessage(self, event):
        print("Recording with event {}".format(event))
        try:
            queueurl = self.getQueueURL()
            print("Got queue URL {}".format(queueurl))
            response = self.sqs_client.send_message(QueueUrl=queueurl, MessageBody=json.dumps(event), MessageGroupId="SnowNetwrokRequest")
            print("Send result: {}".format(response))
        except Exception as exception:
            print("Exception in Lambda Handler and error is {}".format(exception))

def lambda_handler(event, context):
    try:
        print("inside the handler checking the event type and data within it....")
        print(type(event))
        print(event)
        if event and event['body-json']['catalog_item_name'] == "AWS Account - Create VPC/Extend IP Address Range":
            print("Event is for AWS@Shell account Create VPC/Extend IP Address Range.. now it will be processed..")
            sendqueueObject = SendQueueMessageRecieverBox(event['body-json'], context)
            print("object is created..")
            print("sending response back to snow to make ticket open..")
            snowResponsecode = sendqueueObject.send_Snow_Response(event['body-json'])
            if snowResponsecode == 201 or snowResponsecode == 200:
                print("task is updated with open status now..")
                ValidateAndFramedResponse = sendqueueObject.ValidateCreatequeueMessage(event['body-json'])
                if ValidateAndFramedResponse :
                    sendqueueObject.CreateRecordInS3bucket(ValidateAndFramedResponse)
                    print("Request data stored in s3 bucket..")
                    sendqueueObject.recordAqueueMessage(ValidateAndFramedResponse)
                    print("invoked the queue message..")
                return {
                        'statusCode': 200,
                        'body': json.dumps('Request considered for AWS@Shell Network Operation ..!')
                }
            else:
                print("task update did not go well hence not processing request now as it could be malicious request..")
                return {
                    'statusCode': 400,
                    'body': json.dumps('Request cannot be processed for other than AWS@Shell Network Operation..!')
                }
        else:
            return {
                    'statusCode': 400,
                    'body': json.dumps('Request cant be processed for other than Onbaord to AWS@Shell..!')
            }
    except Exception as exception:
        print(exception)