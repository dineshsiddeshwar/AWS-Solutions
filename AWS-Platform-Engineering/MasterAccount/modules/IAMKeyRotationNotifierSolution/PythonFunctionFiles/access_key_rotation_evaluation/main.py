# (c) 2021 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content
# is provided subject to the terms of the AWS Customer Agreement available at
# https://aws.amazon.com/agreement/ or other written agreement between Customer
# and Amazon Web Services, Inc.


import time
import sys

from account_scan import get_actions_for_account
from notification_handler import send_to_notifier
import boto3, os
import logging
from key_actions import log_actions
from botocore.exceptions import ClientError


#timestamp = int(round(time.time() * 1000))

# setup script logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class EvaluateRotation:
    def __init__(self, event, context):

        self.lambda_client = boto3.client('lambda')

        self.emailTemplateAudit = os.getenv('EmailTemplateAudit')
        self.iamAssumedRoleName = os.getenv('IAMAssumedRoleName')
        self.roleSessionName = os.getenv('RoleSessionName')

        # Parse event to get Account ID and Email
        self.aws_account_id = event['account']
        self.account_name = event['name']
        self.account_email = event['email']
        log.info(f'Currently evaluating Account ID: {self.aws_account_id} | Account Name: {self.account_name}')

    def get_account_session(self):

        my_session = boto3.session.Session()
        my_region = my_session.region_name
        # partition = get_partition_for_region(my_region)
        # Call the assume_role method of the STSConnection object and pass the
        # role ARN and a role session name.
        roleArnString = f"arn:aws:iam::{self.aws_account_id}:" \
                        f"role/{self.iamAssumedRoleName}"
        # Create an STS client object that represents a live connection to the
        # STS service

        base_sts_client = my_session.client('sts')
        try:
            credentials = base_sts_client.assume_role(
                RoleArn=roleArnString,
                RoleSessionName=self.roleSessionName
            )['Credentials']
            log.info("Succussfully assumed Member account IAM role.")
        except base_sts_client.exceptions.ClientError as error:
            log.error(
                f'Check that AccountID: [{self.aws_account_id}] has the correct IAM'
                f' Assume Role deployed to it via the CloudFormation StackSet'
                f' Template. Raw Error: {error}')
            raise

        # From the response that contains the assumed role, get the temporary
        # credentials that can be used to make subsequent API calls

        try: 
            assumed_session = boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken']
            )
            return assumed_session
        except ClientError as err:
            log.error(
                f'Error while assuming session of child account'
                f' - {err}'
            )
            raise


def lambda_handler(event, context):
    """Handler for Lambda.

    :param event: Dictionary account object (Account ID and Email) sent to Lambda via 'Account Inventory' Lambda Function
    :param context: Lambda context object
    """

    log.info('Function starting.')
    log.info(event)

    # Error handling - Ensure that the correct object is getting passed
    # to the function
    if "account" not in event and "email" not in event and "name" not in event:
        log.error(
            'The JSON Event Message getting passed to this Lambda Function'
            ' is malformed. Please ensure it has "account", "name" and "email" as'
            ' part of the JSON body.')
        sys.exit("Couldn't find all required information. Please check the logs further.")

    evaluate_rotation = EvaluateRotation(event, context)

    account_session = evaluate_rotation.get_account_session()

    if account_session is not None:

        action_queue = get_actions_for_account(account_session)

        if action_queue:
            log_actions(action_queue)

            # Send notifications

            send_to_notifier(context, evaluate_rotation.aws_account_id, evaluate_rotation.account_name, evaluate_rotation.account_email,
                            action_queue, evaluate_rotation.emailTemplateAudit)

        log.info('---------------------------')
        log.info('Function has completed.')

    else:
        log.info('Child Account session could not be assumed. Please check logs for further details')

