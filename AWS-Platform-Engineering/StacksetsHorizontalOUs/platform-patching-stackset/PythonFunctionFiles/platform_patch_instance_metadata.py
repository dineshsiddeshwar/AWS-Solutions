import json
import time
import boto3
import json
import datetime
import os
import random
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
logger.addHandler(CH)

class PatchMetadata(object):
    def __init__(self, event, context):
        self.session = boto3.session.Session()
        self.ssm_client = self.session.client('ssm')

    def get_instances(self,region,ssm_client,ec2_client):
        ssm_client = boto3.client('ssm',region_name=region)
        ec2_client = boto3.client('ec2',region_name=region)
        try:
            instances=ec2_client.describe_instances(MaxResults=999)
            all_instances=[]
            instance_image_mapping={}
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    for tag in (instance['Tags']):
                        if tag['Key']=='platform_install_patch':
                            instance_id=instance['InstanceId']
                            all_instances.append(instance_id)
            return all_instances
        except Exception as e:
            print(e)

    def get_instance_metadata(self, all_instances,ssm_client,ec2_client,region):
        account = self.getAccountId()
        list_of_kbid=''
        missing_count='0'
        failed_count='0'
        pending_reboot_count='0'
        last_run=[]
        event={}
        for instance in all_instances:
            print(instance)
            details=self.get_patch_information(instance,list_of_kbid,missing_count,failed_count,pending_reboot_count,last_run,ssm_client,ec2_client)
            unix = time.time() * 1000
            unix = int(unix)
            message_body={
            'unix_timestamp': str(unix),   
            'instance_id':instance,
            'kbid': details[1],
            'missing_count': details[2],
            'failed_count': details[3],
            'pending_reboot_count': details[4],
            'account': account,
            'region': os.environ['REGION'],
            'last run': details[5],
            'instance_state': details[6],
            'ssm_status': details[7]
            }
            print(message_body)
            self.write_to_sqs(message_body)
            list_of_kbid=''
    def get_patch_information(self, instance,list_of_kbid,missing_count,failed_count,pending_reboot_count,last_run,ssm_client,ec2_client):
        details=[]
        response = ssm_client.describe_instance_patches(
        InstanceId=instance,
        Filters=[{'Key': 'State', 'Values': ['Missing']}]
        )
        result=response['Patches']
        while 'nextToken' in response:
            response = ssm_client.describe_instance_patches(
                InstanceId=instance,
                Filters=[{'Key': 'State', 'Values': ['Missing']}],
                nextToken=response['NextToken'])
            result.extend(response['Patches'])
        if result:
            for item in result:
                list_of_kbid=list_of_kbid+','+str(item['KBId'])
        print(instance)
        print(list_of_kbid)
        response = ssm_client.describe_instance_patch_states(
        InstanceIds=[instance]
        )
        result=response['InstancePatchStates']
        while 'nextToken' in response:
            response = ssm_client.describe_instance_patch_states(InstanceIds=[instance],nextToken=response['NextToken'])
            result.extend(response['InstancePatchStates'])
        if result:
            for item in result:
                missing_count=str(item['MissingCount'])
                failed_count=str(item['FailedCount'])
                pending_reboot_count=str(item['InstalledPendingRebootCount'])
                #print(item['KBId'])
        print(missing_count)
        ssm_status=''
        try:
            ssm_response = ssm_client.describe_instance_information(
            InstanceInformationFilterList=[
            {
            'key': 'InstanceIds',
            'valueSet': [instance]
            }
           ]
           )
            if len(ssm_response['InstanceInformationList'])==0:
                ssm_status='Not reporting to ssm'
            else:
                for parameter in ssm_response['InstanceInformationList']:
                    for key,value in parameter.items():
                        if key=='PingStatus':
                            ssm_status=value
            print(ssm_status)
        except Exception as e:
            ssm_status=''
            print(e)
        instance_state=''
        try:
            state_response=ec2_client.describe_instances(
                InstanceIds=[instance])
            instance_state=state_response['Reservations'][0]['Instances'][0]['State']['Name']
            print(instance_state)
        except Exception as e:
            instance_state=''
            print(e)
        last_run=self.get_last_doc_run(instance)
        last_run_date=str(last_run[0])
        details.append(instance)
        details.append(list_of_kbid)
        details.append(missing_count)
        details.append(failed_count)
        details.append(pending_reboot_count)
        details.append(last_run_date)
        details.append(instance_state)
        details.append(ssm_status)
        return details
    def write_to_sqs(self,message_body):
        sqs_region='us-east-1'
        sqs_client = boto3.client('sqs', region_name=sqs_region)
        try:
            queue='https://sqs.us-east-1.amazonaws.com/'+os.environ['ACCOUNT_ID']+'/patching_metadata_queue'
            response=sqs_client.send_message(
                QueueUrl=queue,
                MessageBody=json.dumps(message_body))
            print('written to sqs')
        except Exception as e:
            print(e)

    def get_last_doc_run(self,instance_id):
        print('in last doc run', instance_id)
        run_command_list=[]
        ssm_client = boto3.client('ssm')
        command_id=''
        requested_date=''
        response=''
        try:
            response = ssm_client.list_command_invocations(
                InstanceId=instance_id,
            Filters=[
                {
                    'key': 'DocumentName',
                    'value': 'AWS-RunPatchBaseline'
                },
            ])
            print('instance id.....',instance_id)
            if response['CommandInvocations']:
                print('command id...',response)
                command_invocations=sorted(response['CommandInvocations'], key=lambda x: x['RequestedDateTime'], reverse=True)
                latest_run=command_invocations[0]
                command_id=latest_run['CommandId']
                requested_date=latest_run['RequestedDateTime']
                #command_id=response['CommandInvocations'][0]['CommandId']
                #requested_date=response['CommandInvocations'][0]['RequestedDateTime']
            else:
                command_id='No data history found'
                requested_date='No data history found'
        except Exception as exception:
            command_id='No data history found'
            requested_date='No data history found'
            print(exception)

        run_command_list.append(requested_date)  
        print(requested_date)
        return run_command_list

    def getAccountId(self):
            try:
                sts_client = boto3.client('sts')
                response = sts_client.get_caller_identity()
                account_id = response['Account']
                return account_id  
            except Exception as ex:
                logger.error("Lambda failed with the error:'{0}'".format(ex))
                return "FAILED"      

    def orchestration_func(self,region):
        ssm_client = boto3.client('ssm',region_name=region)
        ec2_client = boto3.client('ec2',region_name=region)
        all_instances=self.get_instances(region,ssm_client,ec2_client)
        if len(all_instances)>0:
             self.get_instance_metadata(all_instances,ssm_client,ec2_client,region)
        else:
            all_instances=[]
            print('no instances found')

def lambda_handler(event, context):
    patch_metadata= PatchMetadata(event, context)
    region=os.environ['REGION']
    patch_metadata.orchestration_func(region)