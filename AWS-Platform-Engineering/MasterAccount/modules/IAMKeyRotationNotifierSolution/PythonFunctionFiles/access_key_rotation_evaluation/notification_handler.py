# (c) 2021 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at
# https://aws.amazon.com/agreement/ or other written agreement between Customer
# and Amazon Web Services, Inc.

"""Notification Handler.

Function for formatting JSON object and invoking the Notifier Module's Lambda.
"""
import json,os
import boto3
import datetime
import dateutil.tz

from account_scan import ActionReasons

import logging

#timestamp = int(round(time.time() * 1000))

# setup script logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def format_notifier_payload(context, account_id, account_name, recipient_email, action_queue,
                             email_template):
    lambdaArn = str(context.invoked_function_arn)
    # partition = lambdaArn.split(':')[1]
    # partition_name = get_partition_name(partition)
    now = datetime.datetime.now(datetime.timezone.utc)

    # Default = 90 days
    rotationPeriod = int(os.getenv('RotationPeriod', 90))

    # how many days ahead of time to warn users of pending actions
    pending_action_warn_period = int(os.getenv('WarnPeriod', 10))

    # TODO Should this be turned into a CloudFormation variable or
    #  added to script logic?
    subject = "[IMPORTANT] AWS IAM Access Key Security Violation" \
              " Detected in your Account."

    actions_formatted = []
    for action_spec in action_queue:
        action = action_spec['action']
        key_metadata = action_spec['key']
        user_name = key_metadata['UserName']
        access_key_id = key_metadata["AccessKeyId"]
        reason = action_spec['reason']
        message = ''
        print("----------------------Printing KEY METADATA------------")
        print(key_metadata)
        key_status = key_metadata['Status']
        key_expired_date = (key_metadata['CreateDate'] + datetime.timedelta(days=rotationPeriod))
        key_expired_date_IST = (key_expired_date + datetime.timedelta(hours = 5.5)).date()
        print(f"printing create data: {key_metadata['CreateDate']}")
        print(f"printing expired data: {key_expired_date_IST}")
        if action != 'WARN':
                message = f'{action};{user_name};{access_key_id};{key_status};{reason.value};{key_expired_date_IST};EXPIRED' \
                        #   f'  ' \
                        #   f'Key Expired on {key_expired_date}'
        else:
            action_date = action_spec['action_date']
            delta = action_date.date() - now.date()
            delta_days = round(delta.total_seconds() / 86400)

            if reason == ActionReasons.KEY_PENDING_ROTATION:
                message = f'{action};{user_name};{access_key_id};{key_status};{reason.value};{key_expired_date_IST};Expiring in {delta_days} days'

            elif reason == ActionReasons.UNUSED_KEY_PENDING_DELETION:
                message = f'{action};{user_name};{access_key_id};{key_status};{reason.value};{key_expired_date_IST};Expiring in {delta_days} days' \

        actions_formatted.append(message)

    # Timestamp for function runtime/invoked date
    now = datetime.datetime.now(tz=dateutil.tz.gettz('UTC'))
    timestamp = now.isoformat()
    template_values = {
        'account_id': account_id,
        'account_name': account_name,
        'timestamp': timestamp,
        'actions': actions_formatted,
        'rotation_period': rotationPeriod,
        'warn_period': pending_action_warn_period
        # 'partition_name': partition_name
    }

    jsonPayload = {
        "email": recipient_email,
        "invoked_by": lambdaArn,
        "subject": subject,
        "email_template": email_template,
        "template_values": template_values
    }

    lambdaPayloadEncoded = json.dumps(jsonPayload).encode('utf-8')

    return lambdaPayloadEncoded


def send_to_notifier(context, account_id, account_name, recipient_email, action_queue,
                     email_template):
    lambdaPayloadEncoded = format_notifier_payload(context, account_id, account_name,
                                                   recipient_email, action_queue,
                                                    email_template)

    # AWS Lambda Client
    lambda_client = boto3.client('lambda')
    notifierLambdaArn = os.getenv('NotifierArn')

    try:
        response = lambda_client.invoke(FunctionName=notifierLambdaArn,
                                        InvocationType='Event',
                                        Payload=lambdaPayloadEncoded)
        log.info(
            f"--Invoked Lambda Function={notifierLambdaArn},"
            f" InvocationType=Event, Payload={str(lambdaPayloadEncoded)}")
    except lambda_client.exceptions.ClientError as error:
        print(error)
        log.error(f"ERROR: Could not invoke Notifier lambda. Please troubleshoot further.")
    return response
