import boto3
import time
from collections import Counter
import datetime
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import calendar
import os
import csv
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
logger.addHandler(CH)

class readDataDynamo(object):
    def __init__(self, event, context):
        self.session = boto3.session.Session()
        self.ssm_client = self.session.client('ssm')
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.s3 = boto3.client('s3')

    def getLatestData(self):
        table_name = 'Patch_Metadata'
        table = self.dynamodb.Table(table_name)
         # Get the start and end timestamps for the current month in milliseconds
        now = datetime.datetime.now()
        start_of_month = datetime.datetime(now.year, now.month, 1)
        end_of_month = datetime.datetime(now.year, now.month+1, 1) - datetime.timedelta(days=1)
        start_timestamp = int(start_of_month.timestamp() * 1000)
        end_timestamp = int(end_of_month.timestamp() * 1000)
        # Initialize dictionaries to hold the latest run for each db_name
        latest_runs = {}
        results = []
        bucket_name=os.environ['OUTPUTBUCKET']
        try:
            response = table.scan(
                        FilterExpression=Key('unix_timestamp').between(start_timestamp, end_timestamp)
                    )
            for item in response['Items']:
                print('item',item)
                results.append(item)
            while 'LastEvaluatedKey' in response:
                response = table.scan(
                    FilterExpression=Key('unix_timestamp').between(start_timestamp, end_timestamp),
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                print(response)
                for item in response['Items']:
                    print('item',item)
                    results.append(item)
            print(results)
        except Exception as exception:
            print(exception)
            print('FAILED')
        day = now.strftime('%d')
        month = now.strftime('%B')
        year = now.strftime('%Y')
        global_l=[]
        column_names=['unix_timestamp','kbid','instance_id','missing_count','failed_count','instance_state','account','pending_reboot_count','region','last run', 'ssm_status', ]
        with open('/tmp/patch_metadata.csv', 'w') as out:
            writer = csv.DictWriter(out,fieldnames=column_names)
            writer.writeheader()
            writer.writerows(results)
        try:
            self.s3.upload_file("/tmp/patch_metadata.csv",bucket_name,"/tmp/patch_metadata.csv")
        except Exception as exception:
            print(exception)
            print('FAILED')
        print('uploaded to s3')
        key = 'Monthly-Reports/patching_instance_metadata_report_{}_{}.csv'.format(month,year)
        copy_source = '{}/{}.csv'.format(bucket_name, "/tmp/patch_metadata")
        try:
            self.s3.copy_object(
                CopySource=copy_source, 
                Bucket=bucket_name, 
                Key=key
            ) 
            print(key)
        except Exception as exception:
            print(exception)
            print('FAILED')
        self.send_report()

    def send_report(self):
        try:
            print('Inside send mail')
            file_name_list=['/tmp/patch_metadata.csv']
            print("Inside Send Mail")
            session = boto3.session.Session()
            ssm_client = session.client('ssm')
            #sender_response = ssm_client.get_parameter(Name='sender_id')
            sender_id = 'SITI-ECP-AWS-AT-SHELL@shell.com'
            ses_client = session.client('ses')
            rec_response = "GX-IDSO-SOM-ET-DP-CLOUD-SECURITY-COMPLIANCE@shell.com"
            to_recipient = rec_response
            recipient_list = to_recipient.split(',')
        # The email body for recipients with non-HTML email clients.
            body_text = "Hello\r\nPlease find the attached baseline report for AWS@Shell."\
                                                                      "\r\nRegards,\r\nCloud Services Team"
        # The HTML body of the email.
            body_html = """<html>
        <head></head>
        <body>
        <p style="font-family:'Futura Medium'">Hello Team,</p>
        <p style="font-family:'Futura Medium'">Please find the attached filtered reports and the baseline report for AWS@Shell.</p>
        <p style="font-family:'Futura Medium'">Best Regards,</p>
        <p style="font-family:'Futura Medium'">Cloud Services Team</p>
        </body>
        </html>
        """
            try:
                # Replace recipient@example.com with a "To" address.
                # # The subject line for the email.
                mail_subject = "Patch instance metadata Reports"
                message = MIMEMultipart('mixed')
                message['Subject'] = mail_subject
                message['From'] = sender_id
                message['To'] = to_recipient
                message_body = MIMEMultipart('alternative')
                char_set = "utf-8"
                textpart = MIMEText(body_text.encode(char_set), 'plain', char_set)
                htmlpart = MIMEText(body_html.encode(char_set), 'html', char_set)
                message_body.attach(textpart)
                message_body.attach(htmlpart)
                for f in file_name_list:
                    attachment_template = f 
                    attribute = MIMEApplication(open(attachment_template, 'rb').read())
                    attribute.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_template))
                    message.attach(attribute)
                message.attach(message_body)
                mail_response = ses_client.send_raw_email(
                    Source=sender_id,
                    Destinations=recipient_list,
                    RawMessage={
                    'Data': message.as_string()
                })
                print('Sent email')

            except Exception as exception:
                print(exception)
            self.delete_from_s3()
        except Exception as exception:
            print(exception)

    def delete_from_s3(self):
        try:
            bucket_name=os.environ['OUTPUTBUCKET']
            self.s3.delete_objects(Bucket=bucket_name, Delete={"Objects":[{"Key":"/tmp/patch_metadata.csv"}]})
            print('deleted from s3')
        except Exception as ex:
            print("Lambda failed with the error:'{0}'".format(ex))
            return "FAILED"

def lambda_handler(event, context):
    dynamo_report= readDataDynamo(event, context)
    dynamo_report.getLatestData()