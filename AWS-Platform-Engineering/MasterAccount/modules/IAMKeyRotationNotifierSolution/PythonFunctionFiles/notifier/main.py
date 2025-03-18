# (c) 2021 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at
# https://aws.amazon.com/agreement/ or other written agreement between Customer
# and Amazon Web Services, Inc.

"""Main.py.

This is the main entry point for this application.
"""

import json,os
import boto3
import logging
from datetime import datetime

from botocore.exceptions import ClientError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Notifier:
    def __init__(self, event, email_template: str, subject: str) -> None:
        self.sender_email = os.getenv('ADMIN_EMAIL')
        self.recipient_email = event.get("email")
        self.template_s3_bucket = os.getenv('S3_BUCKET_NAME')
        self.email_template = email_template
        self.subject = subject
        self.team_dl = os.getenv('TEAM_DL')

    def __get_template(self, template_name):
        log.info(f'Getting template {template_name} from S3')
        s3 = boto3.client('s3')

        try:
            obj = s3.get_object(
                Bucket=self.template_s3_bucket,
                Key=f'EmailTemplate/{template_name}'
            )

            data = obj['Body'].read()
            template = data.decode('utf-8')
            log.info(f'Successfully retrieved content for {template_name}')
            return template
        except ClientError as err:
            log.error(
                f'Error while getting file contents for {template_name}'
                f' - {err}'
            )
            raise

    def __render_email_body(self, template_values: dict):
        subject = self.subject
        # get the appropriate S3 Key for the template
        template_s3_key = self.email_template
        if not template_s3_key:
            log.error(f'Unable to get template for {subject}')
            raise ValueError(f'Unable to get template for {subject}')
        else:
            # stream the template contents from S3
            email = self.__get_template(template_s3_key)

            if email is not None:

                log.info('Rendering email contents')
                print("----------------------------------printing template value-----------------------")
                print(template_values)
                for k, v in template_values.items():
                    placeholder = '{{' + f'{k}' + '}}'
                    if isinstance(v, list):
                        value = self.__format_html_list(v)
                    else:
                        value = str(v)
                    email = email.replace(placeholder, value)

                log.info(f'Rendered Email: {email}')

                return email
            else:

                log.info("Unable to get the email template. Please check logs for further details.")

    @staticmethod
    def __format_html_list(value):
        value_formatted = f'<table border="1"><tr><th>ACTION</th><th>USER NAME</th><th>ACCESS_KEY_ID</th><th>KEY_STATUS</th><th>COMEMNTS</th><th>EXPIRY DATE</th><th>EXPIRY STATUS</th></tr>'
        for line in value:
            print("----------printing lines----------")
            print(line)
            rows = line.split(";")
            value_formatted += f'<tr><td>{rows[0]}</td><td>{rows[1]}</td><td>{rows[2]}</td><td>{rows[3]}</td><td>{rows[4]}</td><td>{rows[5]}</td><td>{rows[6]}</td></tr>'
        value_formatted += f'</table>'
        return value_formatted

    def send_email(self, template_values):
            self.send_ses_email(template_values)

    def send_ses_email(self, template_values):
        my_session = boto3.session.Session()
        my_region = my_session.region_name
        ses = my_session.client('ses', region_name=my_region)

        email_body = self.__render_email_body(template_values)

        try:
            log.info(f'Sending email to {self.recipient_email}')
            resp = ses.send_email(
                Source=self.sender_email,
                Destination={
                    'ToAddresses': [
                        self.recipient_email,
                    ],
                    'CcAddresses':
                        [
                            self.team_dl
                        ]
                },
                Message={
                    'Subject': {
                        'Data': self.subject
                    },
                    'Body': {
                        'Text': {
                            'Data': email_body
                        },
                        'Html': {
                            'Data': email_body
                        }
                    }
                }
            )
            log.info('Email sent successfully - Exiting Gracefully')
            return resp
        except ClientError as err:
            log.error(
                f'Encountered error while attempting to send email - {err}'
            )
            print(err)
            raise err


def lambda_handler(event: dict = None, context=None):
    """Lambda Handler."""
    log.info(f'Event: {json.dumps(event, indent=2)}')

    email_template = event.get('email_template')
    subject = event.get('subject')
    template_values = event.get('template_values')

    admin_email = os.getenv('ADMIN_EMAIL')
    template_values['sender_email'] = admin_email

    notifier = Notifier(event,email_template, subject)
    notifier.send_email(template_values)

