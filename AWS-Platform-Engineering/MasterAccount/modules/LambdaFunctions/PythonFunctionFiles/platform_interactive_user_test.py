import boto3
import logging
import os
import gzip
import json
import random
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

child_account_role_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))

class QueryrunLambda2(object):
    def __init__(self, bucket_name):
        logger.info("Initializing QueryrunLambda2")
        self.session = boto3.session.Session()
        self.s3 = boto3.client("s3")
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3')
        self.interactive_users = []


    def process_object(self, bucket_name, s3_object_uri):
        try:
            # Download the file
            local_filename = '/tmp/' + os.path.basename(s3_object_uri)
            self.s3_client.download_file(bucket_name, s3_object_uri, local_filename)

            # Unzip the file
            with gzip.open(local_filename, 'rb') as f_in:
                object_data_decoded = f_in.read().decode('utf-8')

            # Parse the CloudTrail data
            lines = object_data_decoded.split('\n')
            for line in lines:
                self.process_line(line)
            os.remove(local_filename)
        except Exception as e:
            logger.error(f"An error occurred while processing object: {e}")


    def process_line(self, line):
        if '{userName=' in line:
            username_start = line.find('{userName=') + len('{userName=')
            username_end = line.find('}', username_start)
            account_id_start = line.find(',', username_end) + 1
            username = line[username_start:username_end]
            account_id = line[account_id_start:].strip()  # Strip any leading/trailing whitespace

            # Run get_login_profile API call for each username
            try:
                is_interactive = self.run_get_login_profile(username, account_id)
                if is_interactive:
                    self.interactive_users.append({'username': username, 'account_id': account_id})
            except Exception as e:
                logger.error(f"An error occurred while checking user {username}: {e}")

    def run_get_login_profile(self, username, account_id) -> bool:
        """Run the get_login_profile API call for the given username"""
        try:
            # Assume role in the account of the IAM user
            child_account_role_arn = "arn:aws:iam::" + account_id + ":role/AWSControlTowerExecution"
            logger.info(f"Assuming role: {child_account_role_arn}")

            sts_client = boto3.client('sts')
            assumed_role = sts_client.assume_role(RoleArn=child_account_role_arn,
                                                  RoleSessionName=child_account_role_session_name)
            credentials = assumed_role['Credentials']

            # Create a new IAM client with the assumed role credentials
            assumed_iam_client = boto3.client('iam',
                                              aws_access_key_id=credentials['AccessKeyId'],
                                              aws_secret_access_key=credentials['SecretAccessKey'],
                                              aws_session_token=credentials['SessionToken'])

            # Call get_login_profile API using the assumed role
            response = assumed_iam_client.get_login_profile(UserName=username)
            login_profile = response.get('LoginProfile')
            
            return login_profile is not None  # Return True if login profile exists, else False

        except Exception as e:
            logger.error(f"An error occurred while running get_login_profile API: {e}")
            return False  # Return False in case of any exception


    def send_notification_email(self):
        try:
            # Compose the email message
            subject = "Interactive Result Notification"
            body_text = "Interactive users have been found in your AWS account."
            for user_info in self.interactive_users:
                body_text += f"Username: {user_info['username']}, Account ID: {user_info['account_id']}\n"

            body_html = """<html>
            <head></head>
            <body>
              <p>Interactive users have been found in your AWS account.</p>
              <ul>
            """
            for user_info in self.interactive_users:
                body_html += f"<li>Username: {user_info['username']}, Account ID: {user_info['account_id']}</li>\n"
            
            body_html += """
              </ul>
            </body>
            </html>"""

            # Send the email
            # You need to set up SES client and replace the email addresses
            ses_client = boto3.client('ses')
            response = ses_client.send_email(
                Destination={
                    'ToAddresses': [
                        'GX-SITI-CPE-Team-Titan@shell.com', 'GX-IDSO-SOM-ET-DP-CLOUD-SECURITY-COMPLIANCE@shell.com'
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': 'UTF-8',
                            'Data': body_html,
                        },
                        'Text': {
                            'Charset': 'UTF-8',
                            'Data': body_text,
                        },
                    },
                    'Subject': {
                        'Charset': 'UTF-8',
                        'Data': subject,
                    },
                },
                Source='SITI-ECP-AWS-AT-SHELL@shell.com',  # Replace with sender email address
            )
            logger.info("Email sent successfully.")
        except Exception as e:
            logger.error(f"Error sending email: {e}")

def lambda_handler(event, context):
    try:
        # Retrieve bucket name and object key from event
        bucket_name = os.environ.get('BUCKET')
        s3_object_uri = event['s3_object_uri']

        # Initialize QueryrunLambda2 object with bucket name
        report_generator = QueryrunLambda2(bucket_name)

        # Process CloudTrail data
        report_generator.process_object(bucket_name, s3_object_uri)


        # Send notification email if interactive users are found
        if len(report_generator.interactive_users) > 0:  # Check if there are interactive users
            report_generator.send_notification_email()

        print("Cloudtrail data processed and notification sent")

    except Exception as ex:
        logger.error("Lambda failed with the error: %s", ex)
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(ex)})
        }
