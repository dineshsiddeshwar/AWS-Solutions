import boto3
import time
from collections import Counter
import datetime
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import csv
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
logger.addHandler(CH)

class innersourceData(object):
    def __init__(self, event, context):
        self.session = boto3.session.Session()
        self.limit = 100
        self.ssm_client = self.session.client('ssm')
        self.s3 = boto3.client('s3')
        self.config_client = boto3.client('config')
        self.bucket_name = os.environ['BUCKET']
        self.ConfigurationAggregator_Name = 'aws-controltower-ConfigAggregatorForOrganizations'
    def get_aggregated_config_results(self):
        results_dict_list = []
        try:
            now = datetime.datetime.now()
            bucket_name=self.bucket_name
            query_expression="""SELECT accountId,resourceName,resourceId,awsRegion,arn,resourceType,tags.key WHERE tags.key = 'platform_IAC_Source'"""
            response = self.config_client.select_aggregate_resource_config(
                ConfigurationAggregatorName=self.ConfigurationAggregator_Name,
                Expression=query_expression,  # Query expression
                Limit=self.limit,  # Maximum number of results to return
            )
        
            if response:
                results = response["Results"]
                while "NextToken" in response:
                    response = self.config_client.select_aggregate_resource_config(
                        ConfigurationAggregatorName='aws-controltower-ConfigAggregatorForOrganizations',
                        Expression=query_expression,
                        Limit=self.limit,
                        NextToken=response["NextToken"])
                    results.extend(response["Results"])
        
            # convert string to dictionary
            for each_result in results:
                each_result_dict = json.loads(each_result)
                results_dict_list.append(each_result_dict)
        
            print(results_dict_list)
        
        except Exception as e:
            logging.error(f"Error in getting aggregated results: {e}")
            print('FAIL')
        
        day = now.strftime('%d')
        month = now.strftime('%B')
        year = now.strftime('%Y')
        global_l=[]
        column_names=['accountId','resourceName','resourceId','awsRegion','arn','resourceType','resourceCreationTime','tags',]
        with open('/tmp/innersource_data.csv', 'w') as out:
            writer = csv.DictWriter(out,fieldnames=column_names)
            writer.writeheader()
            writer.writerows(results_dict_list)
        try:
            self.s3.upload_file("/tmp/innersource_data.csv",bucket_name,"/tmp/innersource_data.csv")
        except Exception as exception:
            print(exception)
            print('FAILED')
        print('uploaded to s3')
        key = 'innersource_data_report_{}_{}.csv'.format(month,year)
        copy_source = '{}/{}.csv'.format(bucket_name, "/tmp/innersource_data")
        try:
            self.s3.copy_object(
                CopySource=copy_source, 
                Bucket=self.bucket_name, 
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
            file_name_list=['/tmp/innersource_data.csv']
            print("Inside Send Mail")
            session = boto3.session.Session()
            ssm_client = session.client('ssm')
            #sender_response = ssm_client.get_parameter(Name='sender_id')
            sender_id = 'SITI-ECP-AWS-AT-SHELL@shell.com'
            ses_client = session.client('ses')
            rec_response = "d.kumar6@shell.com,Kaushiki.Singh@shell.com,julio.silveira@shell.com,R-Sreedhar.Reddy@shell.com,b-s.yashas@shell.com"
            to_recipient = rec_response
            recipient_list = to_recipient.split(',')
        # The email body for recipients with non-HTML email clients.
            body_text = "Hello\r\nPlease find the innersource tag based resources list for AWS@Shell in attachment."\
                                                                      "\r\nRegards,\r\nCloud Services Team"
        # The HTML body of the email.
            body_html = """<html>
        <head></head>
        <body>
        <p style="font-family:'Futura Medium'">Hello Team,</p>
        <p style="font-family:'Futura Medium'">Please find the innersource tag based resources list for AWS@Shell in attachment.</p>
        <p style="font-family:'Futura Medium'">Best Regards,</p>
        <p style="font-family:'Futura Medium'">Cloud Services Team</p>
        </body>
        </html>
        """
            try:
                # Replace recipient@example.com with a "To" address.
                # # The subject line for the email.
                mail_subject = "Innersource Tag Based Resources List for AWS@Shell"
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
            bucket_name=os.environ['BUCKET']
            self.s3.delete_objects(Bucket=bucket_name, Delete={"Objects":[{"Key":"/tmp/innersource_data.csv"}]})
            print('deleted from s3')
        except Exception as ex:
            print("Lambda failed with the error:'{0}'".format(ex))
            return "FAILED"
def lambda_handler(event, context):
    innersource_report= innersourceData(event, context)
    innersource_report.get_aggregated_config_results()
