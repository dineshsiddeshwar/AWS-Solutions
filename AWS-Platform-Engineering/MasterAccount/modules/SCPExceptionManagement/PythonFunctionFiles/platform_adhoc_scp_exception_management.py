import boto3
import logging
import json

LOGGER = logging.getLogger('logging')
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


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


def getQueueURL(sqs_client):
        try:
            queue_url = sqs_client.get_queue_url(QueueName="platform_scp_snow_request_box.fifo").get('QueueUrl')
            print("Queue URL is {}".format(queue_url))
            return queue_url
        except Exception as exception:
            print("Exception in Lambda Handler and error is {}".format(exception))
            return False

def send_sqs_message(message):
    try:
        LOGGER.info("Sending SQS message :- {0}".format(message))
        sqs_client = boto3.client('sqs',region_name='us-east-1')
        queueurl = getQueueURL(sqs_client)
        if queueurl:
            response = sqs_client.send_message(QueueUrl=queueurl, MessageBody=json.dumps(message), MessageGroupId="SnowRequest")
            LOGGER.info("Send result: {}".format(response))
            if response:
                return True
            else:
                return False
    except Exception as exception:
        print("Error inside Send SQS message", exception)
        return False
    
    
def lambda_handler(event, context):
    """
    Sample Event :-
    {
	"RequestType": "New | ""Renewal",
	"RequestNumber": "RITM5012951",
	"task_no": "SCTASK8618256",
	"accountName": "AWS-HYB-Account-Testing-DemoSA",
	"accountNumber": "749229839612",
	"actions": "",
	"Requested_date": "2023-09-07",
	"Due_date": "2024-06-04",
	"old_ritm": "RITM5012881",
	"requestorName": "Dinesh.Siddeshwar@shell.com"
}
    """
    try:
        LOGGER.info("Recieved the event :- {}".format(event))
        if event:
            sqs_status = send_sqs_message(event)
            if sqs_status:
               LOGGER.info("Sending Message to SQS is successfull")
               return {
                        'statusCode': 200,
                        'body': json.dumps('Request considered for Exception at AWS@Shell..!')
                }
        return {
                        'statusCode': 400,
                        'body': json.dumps('Request failed to considered for Exception at AWS@Shell..!')
                }
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        return {
                        'statusCode': 400,
                        'body': json.dumps('Request failed to considered for Exception at AWS@Shell..!')
                }