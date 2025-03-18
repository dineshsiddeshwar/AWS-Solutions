import json
import time
import boto3
import json
import datetime
import os
import random
class sqsToDynamo(object):
    def __init__(self, event, context):
        self.session = boto3.session.Session()
    def process_message(self,message_body):
        print('processing',message_body)
        try:
            dynamodb_client=boto3.client('dynamodb')
            item={
                                'unix_timestamp': {'N' : message_body['unix_timestamp']},
                                'instance_id': {'S': message_body['instance_id']},
                                'kbid': {'S':message_body['kbid']},
                                'missing_count': {'S':message_body['missing_count']},
                                'failed_count': {'S':message_body['failed_count']},
                                'pending_reboot_count': {'S':message_body['pending_reboot_count']},
                                'account': {'S': message_body['account']},
                                'region': {'S': message_body['region']},
                                'last run': {'S': message_body['last run']},
                                'instance_state': {'S': message_body['instance_state']},
                                'ssm_status': {'S': message_body['ssm_status']}
                        }
        except Exception as e:
            print(e)
        try:
            dynamodb_client.put_item(
                TableName='Patch_Metadata',
                Item=item
                )
            print('Item added to dynamo', item)
        except Exception as e:
            print(e)
def lambda_handler(event, context):
        #poll_and_write_to_dynamodb()
        print(event)
        sqs_to_dynamo= sqsToDynamo(event, context)
        for record in event['Records']:
            message_body=json.loads(record['body'])
            sqs_to_dynamo.process_message(message_body)