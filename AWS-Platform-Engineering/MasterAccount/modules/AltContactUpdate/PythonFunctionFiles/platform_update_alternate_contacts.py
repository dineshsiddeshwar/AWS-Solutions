import json
import os
import boto3
import logging

log = logging.getLogger()
log.setLevel(logging.INFO)


def lambda_handler(event, context):
    security_email = os.environ["SECURITY_EMAIL"]
    security_contact_name = os.environ["SECURITY_CONTACT_NAME"]
    security_contact_title = os.environ["SECURITY_CONTACT_TITLE"]
    security_contact_phone = os.environ["SECURITY_CONTACT_PHONE"]

    operations_email = os.environ["OPERATIONS_EMAIL"]
    operations_contact_name = os.environ["OPERATIONS_CONTACT_NAME"]
    operations_contact_title = os.environ["OPERATIONS_CONTACT_TITLE"]
    operations_contact_phone = os.environ["OPERATIONS_CONTACT_PHONE"]


    print(event)
    
    if event["detail"]["eventName"] == "UpdateManagedAccount":
         accountId = event['detail']['serviceEventDetails']['updateManagedAccountStatus']['account']['accountId']
    else:
        accountId = event['detail']['serviceEventDetails']['createManagedAccountStatus']['account']['accountId']
    print(accountId)

    client = boto3.client('account')

    # Updating security contact information

    try:
        response = client.put_alternate_contact(
            AccountId=accountId,
            AlternateContactType='SECURITY',
            EmailAddress=security_email,
            Name=security_contact_name,
            PhoneNumber=security_contact_phone,
            Title=security_contact_title
        )
        log.info("Succussfully updated security contact information.")
    except Exception as error:
        log.error(
            f' There is issue while updating security contact information. Please troubleshoot further with below error.'
            f' Template. Raw Error: {error}')
        raise
    
    # Updating operations contact information
    try:
        response = client.put_alternate_contact(
            AccountId=accountId,
            AlternateContactType='OPERATIONS',
            EmailAddress=operations_email,
            Name=operations_contact_name,
            PhoneNumber=operations_contact_phone,
            Title=operations_contact_title
        )
        log.info("Succussfully updated operations contact information.")
    except Exception as error:
        log.error(
            f' There is issue while updating operations contact information. Please troubleshoot further with below error.'
            f' Template. Raw Error: {error}')
        raise

