import csv
import boto3
import logging
import os
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
from io import StringIO # Python 3.x
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

class vm_failed_backup:
    def __init__(self):
        LOGGER.info("in init")
        self.session = boto3.session.Session()
        self.athena_client = boto3.client('athena')
        self.ses_client = self.session.client('ses')
        self.ssm_client = self.session.client('ssm')
        self.s3_client=boto3.client("s3")
        self.bucket_name_backup=os.environ['bucket_name']
        self.athena_query_backup=os.environ['athena_query']


    def run_athena_query(self):
        try:
            
            response = self.athena_client.start_query_execution(
                QueryString=self.athena_query_backup,
                QueryExecutionContext={
                    'Database': 'default'  # Replace with your database name
                },
                ResultConfiguration={
                    'OutputLocation': f's3://{self.bucket_name_backup}/failed_backups/'  # Replace with your S3 bucket
                }
            )
            query_execution_id = response['QueryExecutionId']
            return query_execution_id
            
        except Exception as exception:
            print(exception)
            return False

    def download_csv_files_from_s3(self, prefix, download_dir):
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name_backup,
                Prefix=prefix
            )
            for obj in response.get('Contents', []):
                key = obj['Key']
                if key.endswith('.csv'):
                    file_name = os.path.basename(key)
                    download_path = os.path.join(download_dir, file_name)
                    self.s3_client.download_file(self.bucket_name_backup, key, download_path)
                    print(f"Downloaded {key} to {download_path}")
            return download_path
        except Exception as exception:
            print(exception)
            
    def send_results(self, path):
        try:
            #file_key = s3_object_uri
            print("Inside Send Mail")
            sender_response = self.ssm_client.get_parameter(Name='sender_id')
            sender_id = "SITI-ECP-AWS-AT-SHELL@shell.com"
            rec_response = "GX-IDSO-SOM-ET-DP-CLOUD-SECURITY-COMPLIANCE@shell.com"
            to_recipient = rec_response
            recipient_list = to_recipient.split(',')
            # The email body for recipients with non-HTML email clients.
            body_text = "Hello\r\nPlease find the attached report of failed backups for AWS@Shell."\
                        "\r\nRegards,\r\nAWS@Shell Platform Engineering Team"
            # The HTML body of the email.
            body_html = """<html>
            <head></head>
            <body>
            <p style="font-family:'Futura Medium'">Hello Team,</p>
            <p style="font-family:'Futura Medium'">Please find the attached report of failed backups for AWS@Shell.</p>
            <p style="font-family:'Futura Medium'">Best Regards,</p>
            <p style="font-family:'Futura Medium'">AWS@Shell Platform Engineering Team</p>
            <href>GX-SITI-CPE-Team-Titan@shell.com</href>
            </body>
            </html>
            """
            LOGGER.info('mailing')
            mail_subject = "AWS failed backup reports"
            #attachment_template = file_name  # "{}".format(file_name)
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
            attachment_template = path
            print('put value in attachment')
            attribute = MIMEApplication(open(attachment_template, 'rb').read())
            print('read the attribute')
            attribute.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_template))
            message.attach(attribute)
            message.attach(message_body)
            mail_response = self.ses_client.send_raw_email(
                Source=sender_id,
                Destinations=recipient_list,
                RawMessage={
                    'Data': message.as_string()

                })
            LOGGER.info('mailed')

        except Exception as exception:
            print(exception)

    def delete_objects_in_prefix(self, prefix):
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name_backup, Prefix=prefix)
            if 'Contents' in response:
                objects = [{'Key': obj['Key']} for obj in response['Contents']]
                self.s3_client.delete_objects(Bucket=self.bucket_name_backup, Delete={'Objects': objects})
                LOGGER.info(f"Deleted {len(objects)} objects in '{prefix}' prefix.")
        except Exception as ex:
            LOGGER.error(f"Failed to delete objects in prefix '{prefix}'. Error: {ex}")
        
def lambda_handler(event, context):
    vm_backup_obj = vm_failed_backup()
    if vm_backup_obj.run_athena_query() :
        time.sleep(10)
        prefix = 'failed_backups/'  # Prefix of CSV files
        download_dir = '/tmp'  # Directory to save downloaded CSV files
        path = vm_backup_obj.download_csv_files_from_s3(prefix, download_dir)
        vm_backup_obj.send_results(path)
        time.sleep(10)
        # Delete objects in the Unsaved folder
        vm_backup_obj.delete_objects_in_prefix(prefix)
    
