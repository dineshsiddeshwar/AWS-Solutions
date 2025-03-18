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


def invoke_lambda_function(instanceid, region, accountid):
    """
    This function invokes the lambda function in dev builder account which has identity configured
    """
    try:
        emailaccountid = os.environ.get('emailAccount')
        emailLambda = "arn:aws:lambda:us-east-1:"+emailaccountid+":function:Isolation-Sendemail"
        logger.info("inside invokation function")
        dict_items = {'instanceId': instanceid, 'region': region, 'accountId': accountid}
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
                    FunctionName=emailLambda,
                    InvocationType = 'Event',
                    Payload=json.dumps(dict_items)
                    )
        if invoke_response:
            return True
    except Exception as ex:
        logger.error("There is something went wrong in invoking lambda.:- {}".format(ex))
        raise ex



# This lambda should have below
# 1. lambda invoke permission in the account ##### and assume role permission
# resource policy attach to allow sns to trigger
# enviromentvariable emailAccount
# SNS messge should be:- {"instanceId":"i-0766aec8ecbd95eaa","region":"us-east-1","accountId":"749653192239"}

def lambda_handler(event, context):
    """
    This lambda will recieve the message from SNS and post it SES lambda to send the approval email
    """
    try:
        logger.info("Event recieved is:- {}".format(event))
        message = json.loads(event['Records'][0]['Sns']['Message'])
        instanceid = message['instanceId']
        region = message['region']
        accountid = message['accountId']
        status = invoke_lambda_function(instanceid, region, accountid)
        return status
    except Exception as ex:
        logger.error("There is something went wrong in lambda handler.:- {}".format(ex))
        raise ex