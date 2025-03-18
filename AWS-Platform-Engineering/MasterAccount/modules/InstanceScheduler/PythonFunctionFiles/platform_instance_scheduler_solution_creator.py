'''
EC2 instance scheduler as part of PBI - 333236 which create the lambda in child account from payer account
'''
import logging
import random
import json
import time
import boto3
import os
import requests

SUCCESS = "SUCCESS"
FAILED = "FAILED"

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

class InstanceSchedulerInfraCreator(object):
    """
    # EC2 instance scheduler as part of PBI - 333236
    """
    def __init__(self, event, context):
        self.event = event
        self.context = context
        self.reason_data = " "
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            self.session_client = boto3.Session()
            self.sts_client = self.session_client.client('sts')
            self.ssm_client = self.session_client.client('ssm')
            bucket_name = self.ssm_client.get_parameter(Name='releses3bucket')
            self.bucket_name = (bucket_name['Parameter']['Value'])
            print("release bucket name: {}".format(self.bucket_name))
            folder_name = self.ssm_client.get_parameter(Name='foldername')
            self.folder_name = (folder_name['Parameter']['Value']) 
            print("release folder_name name: {}".format(self.folder_name))
            self.zip_file_name = "{}/Lambda/platform_instance_state_scheduler.zip".format(self.folder_name)  
            print("release bucket name: {}".format(self.zip_file_name))
            self.child_account_number = event['ResourceProperties']['AWSAccountId']
            print(self.child_account_number)
            self.child_account_arn = "arn:aws:iam::{}:role/AWSControlTowerExecution". \
                format(self.child_account_number)
            self.child_account_sessionname = "linkedAccountSession-" + \
                                             str(random.randint(1, 100000))
            child_account_role_creds = self.sts_client.assume_role \
                (RoleArn=self.child_account_arn, RoleSessionName=self.child_account_sessionname)
            child_credentials = child_account_role_creds.get('Credentials')
            child_access_keyid = child_credentials.get('AccessKeyId')
            child_secret_access_key = child_credentials.get('SecretAccessKey')
            child_session_token = child_credentials.get('SessionToken')
            self.child_assume_role_session = boto3.Session(child_access_keyid, child_secret_access_key,
                                                           child_session_token)
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)
            raise Exception(str(exception))

    def createiamrolepolicy(self):
        try:  
            self.iam_childaccount_client = self.child_assume_role_session.client('iam')
            assume_role_policy_document = json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": ["lambda.amazonaws.com", "events.amazonaws.com"]
                        },
                        "Action": "sts:AssumeRole"
                        }
                    ]
                })
            create_role_response = self.iam_childaccount_client.create_role( RoleName = "platform_instance_scheduler_role", AssumeRolePolicyDocument = assume_role_policy_document)
            if create_role_response:
                print("create role succeeded attaching a policy now..!!")
                responseEC2 = self.iam_childaccount_client.attach_role_policy( RoleName='platform_instance_scheduler_role', PolicyArn='arn:aws:iam::aws:policy/AmazonEC2FullAccess')
                responseEVENT = self.iam_childaccount_client.attach_role_policy( RoleName='platform_instance_scheduler_role', PolicyArn='arn:aws:iam::aws:policy/CloudWatchEventsFullAccess')
                responseSSM= self.iam_childaccount_client.attach_role_policy( RoleName='platform_instance_scheduler_role', PolicyArn='arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess')
                responseLAMBDA = self.iam_childaccount_client.attach_role_policy( RoleName='platform_instance_scheduler_role', PolicyArn='arn:aws:iam::aws:policy/AWSLambda_FullAccess')
                responseLAMBDA2 = self.iam_childaccount_client.attach_role_policy( RoleName='platform_instance_scheduler_role', PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole')
                if responseEC2 and responseEVENT and responseSSM and responseLAMBDA and responseLAMBDA2 :
                    print("attach role policy succeeded..!!")
                    return create_role_response
                else:
                    print("attach role policy failed..!!")
            else:
                print("role creation failed , manual check needed..!!")
        except Exception as exception:
            print("Exception in Lambda Handler", exception)

    def createeventrule_toschedule(self, roleARN, lambdaARN):
        try:
            self.events_childaccount_client = self.child_assume_role_session.client('events', region_name="us-east-1")
            self.lambda_childaccount_client = self.child_assume_role_session.client('lambda', region_name="us-east-1")
            eventrule = self.events_childaccount_client.put_rule(Name="platform_instance_scheduler_event", ScheduleExpression="rate(30 minutes)", State="ENABLED" ,Description="Scheduled Rule for every 30 minutes" ,RoleArn=roleARN)
            if eventrule:
                print("Lambda invoke event rule created successfully..!")
                eventtarget = self.events_childaccount_client.put_targets(
                                    Rule="platform_instance_scheduler_event",
                                    Targets=[
                                        {
                                            "Id": "TargetFunctionV1",
                                            "Arn": lambdaARN,
                                        }
                                    ]
                                )
                if eventtarget:
                    print("Event target created successfully..!")
                    lambdaPermission = self.lambda_childaccount_client.add_permission(
                                            FunctionName=lambdaARN,
                                            StatementId="platforminstanceschedulerlambdapermission",
                                            Action="lambda:InvokeFunction",
                                            Principal="events.amazonaws.com",
                                            SourceArn=eventrule["RuleArn"]
                                        )
                    if lambdaPermission:
                        response_data = {
                            'AccountId': self.event['ResourceProperties']['AWSAccountId'],
                            'RequestNumber':self.event['ResourceProperties']['RequestNo'],
                            'Status': 'Lambda create successful..!!'
                            }
                        self.send(
                            self.event,
                            self.context,
                            SUCCESS,
                            response_data,
                            self.reason_data
                        )
                        print("Lambda permission addition is successfull..!")
                    else:
                        response_data = {
                            'AccountId': self.event['ResourceProperties']['AWSAccountId'],
                            'RequestNumber':self.event['ResourceProperties']['RequestNo'],
                            'Status': 'Lambda creation failed..!!'
                            }
                        self.send(
                            event=self.event,
                            context=self.context,
                            response_status=FAILED,
                            response_data=response_data,
                            reason_data=self.reason_data
                        )
                        print("Lambda permission addition is creation failed..!")
                else: 
                    print("Event target creation failed..!")
            else:
                print("Lambda invoke event rulle creation failed..!")  
        except Exception as exception:
            print("Exception in Lambda Handler", exception)

    def downloadzipfile(self):
        try:  
            ## s3://azure-devops-da2.0-release-dev-us-east-1/Release-382/Lambda/platform_ami_tagging_eks.zip
            self.s3_local_client = self.session_client.client('s3', region_name="us-east-1", verify=False)
            self.s3_local_client.download_file(self.bucket_name, self.zip_file_name, "/tmp/platform_instance_state_scheduler.zip")
            if os.path.exists("/tmp/platform_instance_state_scheduler.zip"):
                print("file downloaded successfully..!!")
                return True
            else:
                print("zip file not downlaoded in path..!!")
                exit()
        except Exception as exception:
            print("Exception happend at downlaod in Lambda Handler", exception)

    def removezipfile(self):
        try:
            os.remove("/tmp/platform_instance_state_scheduler.zip")
            if not os.path.exists("/tmp/platform_instance_state_scheduler.zip"):
                print("file removed successfully..!!")
            else:
                print("file not removed, please check it manaully..!!")
        except Exception as exception:
            print("Exception in Lambda Handler", exception)

    def aws_file(self):
        try:
            with open('/tmp/platform_instance_state_scheduler.zip', 'rb') as file_data:
                bytes_content = file_data.read()
            return bytes_content
        except Exception as exception:
            print("Exception in Lambda Handler", exception)

    def checkifLambdaExist(self):
        try:
            self.lambda_childaccount_client = self.child_assume_role_session.client('lambda', region_name="us-east-1")
            checklambda_response = self.lambda_childaccount_client.get_function(FunctionName='platform_instance_state_scheduler')
            if checklambda_response:
                return True
        except Exception as exception:
            print("Exception in Lambda Handler", exception)
            return False

    def lambda_creator_update(self, create, roleARN):
        try:
            response_data = {}
            self.lambda_childaccount_client = self.child_assume_role_session.client('lambda', region_name="us-east-1")
            if create:
                create_response = self.lambda_childaccount_client.create_function(
                    Code={
                        'ZipFile': self.aws_file()
                    },
                    Description='This is instance state scheduler lambda',
                    FunctionName='platform_instance_state_scheduler',
                    Handler='platform_instance_state_scheduler.lambda_handler',
                    Publish=True,
                    Timeout=900,
                    MemorySize=1024,
                    Role=roleARN,
                    Runtime='python3.8',
                    Tags={
                          'platform_donotdelete': 'Yes'
                        }
                )
                if create_response :
                    print("Lambda create successful..")
                    return create_response
                else: 
                    print("Lambda creation failed..!!")
            else:
                update_response = self.lambda_childaccount_client.update_function_code(FunctionName='platform_instance_state_scheduler', ZipFile= self.aws_file(), Publish=True)
                if update_response:
                    response_data = {
                            'AccountId': self.event['ResourceProperties']['AWSAccountId'],
                            'RequestNumber':self.event['ResourceProperties']['RequestNo'],
                            'Status': 'Lambda create successfull..!!'
                           }
                    self.send(
                        self.event,
                        self.context,
                        SUCCESS,
                        response_data,
                        self.reason_data
                    )
                    print("Lambda update successful..")
                else: 
                    response_data = {
                        'AccountId': self.event['ResourceProperties']['AWSAccountId'],
                        'RequestNumber':self.event['ResourceProperties']['RequestNo'],
                        'Status': 'Lambda update failed..!!'
                        }
                    self.send(
                        self.event,
                        self.context,
                        FAILED,
                        response_data,
                        self.reason_data
                    )
                    print("Lambda update failed..!!")

        except Exception as exception:
            print("Exception in Lambda Handler", exception)
            return False          

    def send(self, event, context, response_status, response_data, reason_data):
        '''
        Send status to the cloudFormation
        Template.
        '''
        print("Inside send method")
        response_url = event['ResponseURL']

        response_body = {}
        response_body['Status'] = response_status
        response_body['Reason'] = reason_data + ' See the details in CloudWatch Log Stream: ' + \
                                  context.log_stream_name
        response_body['PhysicalResourceId'] = event['StackId'] + event['RequestId']
        response_body['StackId'] = event['StackId']
        response_body['RequestId'] = event['RequestId']
        response_body['LogicalResourceId'] = event['LogicalResourceId']
        if response_status == FAILED:
            json_responsebody = json.dumps(response_body)
        else:
            response_body['Data'] = response_data

            json_responsebody = json.dumps(response_body)

        print("Response body:{}".format(json_responsebody))

        headers = {
            'content-type': '',
            'content-length': str(len(json_responsebody))
        }

        try:
            response = requests.put(response_url,
                                    data=json_responsebody,
                                    headers=headers)
            print("Status code:{} ".format(response.reason))
        except Exception as exception:
            print("send(..) failed executing requests.put(..):{} ".format(str(exception)))

    def cleanup_instance_scheduler(self):
        try:
            response_data = {}
            self.lambda_childaccount_client = self.child_assume_role_session.client('lambda', region_name="us-east-1")
            self.events_childaccount_client = self.child_assume_role_session.client('events', region_name="us-east-1")
            self.iam_childaccount_client = self.child_assume_role_session.client('iam')
             
            print('lambda deletion started.....')
            if self.checkifLambdaExist():
                self.lambda_childaccount_client.delete_function(FunctionName='platform_instance_state_scheduler')
            print('lambda deleted successfully..!')

            if self.iam_childaccount_client.get_role(RoleName='platform_instance_scheduler_role'):
                attached_role_policies= self.iam_childaccount_client.list_attached_role_policies(RoleName='platform_instance_scheduler_role')
                for delete_policy in attached_role_policies['AttachedPolicies']:
                        self.iam_childaccount_client.detach_role_policy(RoleName='platform_instance_scheduler_role', PolicyArn=delete_policy['PolicyArn'])
                self.iam_childaccount_client.delete_role(RoleName='platform_instance_scheduler_role')
            print('role deleted successfully..!')

            if self.events_childaccount_client.describe_rule(Name='platform_instance_scheduler_event'): 
                self.events_childaccount_client.remove_targets(Rule='platform_instance_scheduler_event',Ids=['TargetFunctionV1',])
                self.events_childaccount_client.delete_rule(Name='platform_instance_scheduler_event')
            print('event rule deleted successfully..!')
                    
            response_data = {
                            'AccountId': self.event['ResourceProperties']['AWSAccountId'],
                            'RequestNumber':self.event['ResourceProperties']['RequestNo'],
                            'Status': 'Deleting instance scheduler successfull..!!'
                           }
            self.send(
                        self.event,
                        self.context,
                        SUCCESS,
                        response_data,
                        self.reason_data
                    )
        except Exception as exception:
            print("Exception in Lambda Handler", exception)
            response_data = {
                            'AccountId': self.event['ResourceProperties']['AWSAccountId'],
                            'RequestNumber':self.event['ResourceProperties']['RequestNo'],
                            'Status': 'Error at instance scheduler cleanup..!!'
                           }
            self.send(
                        self.event,
                        self.context,
                        FAILED,
                        response_data,
                        self.reason_data
                    )
            return False 

def lambda_handler(event, context):
    """"
    # EC2 instance scheduler as part of PBI - 333236
    """
    try:
        print("Event {}".format(event))
        create_instancescheduler_obj = InstanceSchedulerInfraCreator(event, context)
        if event['RequestType'] != 'Delete':
            Isdownloaded = create_instancescheduler_obj.downloadzipfile()
            if Isdownloaded :
                if create_instancescheduler_obj.checkifLambdaExist() :
                    print("Lambda exists hence only updates code..!!")
                    create =  False
                    create_instancescheduler_obj.lambda_creator_update(create, "not_required")
                    print("Instance scheduler set up is updated successful..!!")
                else:
                    print("Lambda does not exists hence creates it..!!")
                    create =  True
                    roleresults = create_instancescheduler_obj.createiamrolepolicy()
                    if roleresults :
                        print(roleresults['Role']['Arn'])
                        time.sleep(30)
                        Lambdaresults = create_instancescheduler_obj.lambda_creator_update(create, roleresults['Role']['Arn'])
                        if Lambdaresults :
                            print(Lambdaresults['FunctionArn'])
                            create_instancescheduler_obj.createeventrule_toschedule(roleresults['Role']['Arn'], Lambdaresults['FunctionArn'])
                            print("Instance scheduler set up is created successful..!!")
                create_instancescheduler_obj.removezipfile()
        else:
            create_instancescheduler_obj.cleanup_instance_scheduler()
        print("platform instance scheduler solution task is successful..")
    except Exception as exception:
        print("Exception in Lambda Handler", exception)
