import boto3
import logging
import json
import os

#CLouwatch logger variables
logger = logging.getLogger()
logger.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
logger.addHandler(CH)


SUCCESS = "SUCCESS"
FAILED = "FAILED"


def invoke_lambda_function(event):
    """
    This function invokes the lambda function in dev builder account which has identity configured
    """
    try:
        logger.info("inside invokation function")
        arn = os.environ.get('LAMBDARN')
        #temp_event = json.loads(event)
        temp_event = event
        lambda_event = {"region": temp_event['region'], "instanceId": temp_event['instanceId'], "email": temp_event['email'], "accountId": temp_event['accountId'],"decision": temp_event['decision']}
        # ses_role_arn = "arn:aws:iam::294412549994:role/HIS-236-ses-lambdaRole"
        # sts_client = boto3.client('sts')
        # assumed_role_object = sts_client.assume_role(
        #                     RoleArn=ses_role_arn,
        #                     RoleSessionName="236_ses_role")
        # credentials = assumed_role_object['Credentials']
        # ses_session_client = boto3.session.Session(
        #                                 aws_access_key_id=credentials['AccessKeyId'],
        #                                 aws_secret_access_key=credentials['SecretAccessKey'],
        #                                 aws_session_token=credentials['SessionToken']
        #                             )
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        invoke_response = lambda_client.invoke(
                    FunctionName=arn,
                    InvocationType = 'Event',
                    Payload=json.dumps(lambda_event)
                    )
        if invoke_response:
            return True
        else:
            return False
    except Exception as ex:
        logger.error("There is something went wrong in invoking lambda.:- {}".format(ex))
        raise ex

def lambda_handler(event, context):
    """
    This lambda function acts as API gateway and will recieves the POST request
    """
    try:
        logger.info("Inside lambda handler")
        logger.info("Recived the event: {}".format(event))
        status = invoke_lambda_function(event)
        if status:
            response = {
            'statusCode': 200,
            'body': json.dumps({"Success": event})}
        else:
            response = {
            'statusCode': 400,
            'body': json.dumps({"Failure": "Something went wrong"})}
        return response
    except Exception as ex:
        logger.error("There is something went wrong in lambda handler.:- {}".format(ex))
        raise ex