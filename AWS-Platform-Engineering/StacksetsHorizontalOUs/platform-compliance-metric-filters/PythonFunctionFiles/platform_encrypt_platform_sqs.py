import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class CheckProfileQ(object):
    """
    # Class: Encrypt Platfrom SQS
    # Description: Encrypt Platfrom SQS in the child account
    """
    def __init__(self, event, context):

        try:
            self.session_client = boto3.Session()
            self.ssm_client = self.session_client.client('ssm', region_name='us-east-1')
            region_names = self.ssm_client.get_parameter(Name='platform_whitelisted_regions')
            self.region_list = (region_names['Parameter']['Value']).split(',')
            print(self.region_list)
        except Exception as exception:
            logger.error(str(exception))

    def q_encrypt(self):
        try:
            for region in self.region_list:
                sqs_client = self.session_client.client('sqs',region_name=region)
                print("Set for region:",region)
                queue_list = sqs_client.list_queues(
                    QueueNamePrefix='platform'
                )
                print("que list:",queue_list)                    
                queue_list_urls =  queue_list['QueueUrls']
                print("queue_list_urls:",queue_list_urls)
                for q_url in queue_list_urls:
                    q_attributes = sqs_client.get_queue_attributes(
                        QueueUrl=q_url,
                        AttributeNames=[
                            'SqsManagedSseEnabled'
                        ]
                    )
                    isSqsEncryptionEnabled = q_attributes['Attributes']['SqsManagedSseEnabled']
                    if isSqsEncryptionEnabled == 'false':
                        print(q_url,": is not encryption enabled")
                        response = sqs_client.set_queue_attributes(
                            QueueUrl=q_url,
                            Attributes={
                                'SqsManagedSseEnabled': 'true'
                            }
                        )
                    print("enabled for region :", region)
        except Exception as exception:
            print(str(exception))   
            
def lambda_handler(event,context):
    try:
        profile_ec2_object = CheckProfileQ(event, context)
        profile_ec2_object.q_encrypt()
    except Exception as exception:
        logger.error(str(exception))

