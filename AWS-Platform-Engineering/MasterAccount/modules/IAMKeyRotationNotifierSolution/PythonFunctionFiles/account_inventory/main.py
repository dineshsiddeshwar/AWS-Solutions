# (c) 2021 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at
# https://aws.amazon.com/agreement/ or other written agreement between Customer
# and Amazon Web Services, Inc.

"""Account Inventory Handler.

This module provides the functionality to dynamically query AWS Organizations 
for a full list of account IDs and emails. This script kicks off the 
access_key_rotation_evaluation function.
"""

import boto3
import os
import json
import logging

# setup script logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class TriggerAudit:
    def __init__(self, event, context):

        self.lambda_client = boto3.client('lambda')
        self.lambdaRotationEvaluationFunction = os.environ['LambdaRotationEvaluationFunction']

        self.orgListAccount = os.getenv('OrgListAccount')
        self.orgListRole = os.getenv('OrgListRole')
        self.roleSessionName = os.getenv('RoleSessionName')
        self.dynamodb_table = os.getenv('DynamoDBTable')

        # Assume role in account with Organizations permissions
        self.org_session = self.get_account_session(self.orgListAccount, self.orgListRole, self.roleSessionName)
        self.org_client = self.org_session.client('organizations')

    def get_account_session(self, aws_account_id, orgListRole, roleSessionName):
        # config = Config()

        # Create an STS client object that represents a live connection to the
        # STS service
        my_session = boto3.session.Session()
        my_region = my_session.region_name

        base_sts_client = my_session.client('sts')

        # partition = get_partition_for_region(my_region)

        # Call the assume_role method of the STSConnection object and pass the
        # role ARN and a role session name.
        roleArnString = f"arn:aws:iam::{aws_account_id}:" \
                        f"role/{orgListRole}"

        try:
            credentials = base_sts_client.assume_role(
                RoleArn=roleArnString,
                RoleSessionName=roleSessionName
            )['Credentials']
            log.info("Successfully assumed IAM role to list organization accounts.")
        except base_sts_client.exceptions.ClientError as error:
            log.error(
                f'Check that AccountID: [{aws_account_id}] has the correct IAM'
                f' Role deployed to it via the CloudFormation Stack'
                f' Template. Raw Error: {error}')
            raise

        # From the response that contains the assumed role, get the temporary
        # credentials that can be used to make subsequent API calls
        assumed_session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
        return assumed_session

    def list_all_aws_accounts(self, org_client):
        """
        Gets the current list of all AWS Accounts from AWS Organizations.

        :return The current dict of all AWS Accounts.
        """
        account_list = []

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(self.dynamodb_table)

        try:
            # max limit of 20 users per listing
            # use paginator to iterate through each page
            paginator = org_client.get_paginator('list_accounts')
            page_iterator = paginator.paginate()
            for page in page_iterator:
                for acct in page['Accounts']:
                    try:
                        response = table.get_item(Key={
                            'AccountNumber': acct['Id']
                        })
                        custodian_user = response['Item']['CustodianUser']
                        acct['CustodianUser'] = custodian_user
                        log.info(f"Custodian Email for account {acct['Id']} is {custodian_user}.")
                    except Exception as error:
                        log.error(f"No entry found in dynamodb for {acct['Id']}")

                    account_list.append(acct)
            log.info(f'Successfully retrieved accounts list under organization.')
        except org_client.exceptions.ClientError as error:
            log.error(f'Error: {error}')
            log.error(f'Could not retrieve accounts list, please troubleshoot further')

        return account_list

    def run_lambda_function(self, awsAccountArray, lambdaFunction):
        """
        Invokes the Lambda Function that evaluates whether rotation of key is required. If yes, it notifies the account owner.

        :return Response from Invoke command.
        """
        for account in awsAccountArray:
            # skip accounts that are suspended
            if account['Status'] != 'ACTIVE':
                continue
            print(f"account--{account}")

            if 'CustodianUser' not in account:
                print(f"No Custodian exists for {account['Id']}. Hence, will be sending email to Root DL instead of custodian user.")
                jsonPayload = {
                    "account": account['Id'],
                    "name": account['Name'],
                    "email": account['Email']
                }

            else:

                jsonPayload = {
                    "account": account['Id'],
                    "name": account['Name'],
                    "email": account['CustodianUser']
                }
            lambdaPayloadEncoded = json.dumps(jsonPayload).encode('utf-8')

            try:
                response = self.lambda_client.invoke(
                    FunctionName=lambdaFunction, InvocationType='Event',
                    Payload=lambdaPayloadEncoded)
                lambdaPayloadEncoded_str = str(lambdaPayloadEncoded)
                log.info(f'Invoked: FunctionName= {lambdaFunction},'
                        f' InvocationType=Event,'
                        f' Payload= {lambdaPayloadEncoded_str}')
            except self.lambda_client.exceptions.ClientError as error:
                log.error(f'Error: {error}')
                log.error(f'ERROR: Could not invoke Key Rotation Evaluation Lambda, Please troubleshoot further.')
    # return response


# main Python Function, parses events sent to lambda
def lambda_handler(event, context):
    trigger_audit = TriggerAudit(event, context)

    account_list = trigger_audit.list_all_aws_accounts(trigger_audit.org_client)
    # loop through all accounts and trigger the key Rotation Evaluation Lambda
    trigger_audit.run_lambda_function(account_list, trigger_audit.lambdaRotationEvaluationFunction)

