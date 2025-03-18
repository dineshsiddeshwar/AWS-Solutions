import csv
import boto3
import sys
import logging
import datetime
import calendar
import os
import gzip
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from boto3.dynamodb.conditions import Key, Attr
import pandas as pd
from io import StringIO, BytesIO

# Configure logger
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

class PIMRoleReport:
    def __init__(self, event, context):
        try:
            LOGGER.info("in init")
            self.event = event
            self.context = context
            self.session = boto3.session.Session()
            session_client = boto3.Session()
            self.ses_client = self.session.client('ses')
            self.ssm_client = self.session.client('ssm')
            self.cloudtrail_client = self.session.client('cloudtrail')
            self.s3 = boto3.client("s3")
            self.s3_client = boto3.client('s3')
            self.bucket_name = os.environ['BUCKET']
            self.request_table = os.environ['REQUEST_DYNAMODB_TABLE']
            self.dd_client = session_client.client('dynamodb', region_name="us-east-1")
        except Exception as ex:
            LOGGER.error("Initialization failed with the error: '%s'", ex)
            raise

    def fetch_cloudtrail_logs(self):
        try:
            current_datetime = datetime.datetime.now()
            current_date = current_datetime.date()
            startTime = (datetime.datetime.now() - datetime.timedelta(days=31)).isoformat()
            newstartTime = startTime[:10] + " 00:00:00"
            endTime = str(current_date) + " 00:00:00"

            self.s3_uri = 's3://' + self.bucket_name + '/'
            privilege_role = self.ssm_client.get_parameter(Name='platform_mastercontributorrolearn')
            sender_response_datalakeid = self.ssm_client.get_parameter(Name='platform_datalakeid')
            permission_set_privilege = privilege_role['Parameter']['Value']
            account_id_payer = self.getAccountId()
            account_id_audit = os.environ['AUDIT_ACCOUNT_ID']
            account_id_logging = os.environ['LOGGING_ACCOUNT_ID']
            account_id_shared = os.environ['SHARED_ACCOUNT_ID']
            datalake_id = sender_response_datalakeid['Parameter']['Value']

            query_statement = f"""
                SELECT useridentity.principalid, eventtype, recipientAccountId, awsregion, eventid, eventname, eventtime 
                FROM {datalake_id} 
                WHERE recipientAccountId IN ('{account_id_payer}', '{account_id_audit}', '{account_id_logging}', '{account_id_shared}') 
                AND eventTime > '{newstartTime}' 
                AND eventTime < '{endTime}' 
                AND readOnly = false 
                AND useridentity.arn LIKE 'arn:aws:sts::{account_id_payer}:assumed-role/AWSReservedSSO_platform_MasterContributorAccess_%'
            """

            response = self.cloudtrail_client.start_query(
                QueryStatement=query_statement,
                DeliveryS3Uri=self.s3_uri,
            )

            LOGGER.info("Query Response: %s", response)
            account_id = self.getAccountId()
            current_date_str = str(current_date).replace('-', '/')
            s3_object_uri = f'AWSLogs/{account_id}/CloudTrail-Lake/Query/{current_date_str}/{response["QueryId"]}/result_1.csv.gz'
            LOGGER.info("S3 Object URI: %s", s3_object_uri)
            return s3_object_uri
        except Exception as ex:
            LOGGER.error("Lambda failed with the error: '%s'", ex)
            return None

    def getAccountId(self):
        try:
            sts_client = boto3.client('sts')
            response = sts_client.get_caller_identity()
            if 'Account' in response:
                return response['Account']
            else:
                LOGGER.error("No account ID found in the STS response")
                return None
        except Exception as ex:
            LOGGER.error("Failed to get account ID: '%s'", ex)
            return None

    def get_csv_file_from_s3(self, bucket_name, key):
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=key)
            file_content = gzip.GzipFile(fileobj=response['Body']).read().decode('utf-8')
            csv_data = StringIO(file_content)

            # Skip lines starting with '#' which are the query details
            df = pd.read_csv(csv_data, comment='#')

            # Save DataFrame to CSV and upload to S3
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            new_key = key.replace('.gz', '')  # Remove .gz from the original key

            return df
        except self.s3_client.exceptions.NoSuchKey:
            LOGGER.error("The specified key does not exist: %s", key)
            return None
        except Exception as error:
            LOGGER.error("Error fetching CSV file from S3: %s", error)
            return None

    def upload_csv_to_s3(self, bucket_name, key, csv_data):
        try:
            self.s3_client.put_object(Bucket=bucket_name, Key=key, Body=csv_data)
            LOGGER.info("Successfully uploaded CSV to S3 at %s/%s", bucket_name, key)
        except Exception as error:
            LOGGER.error("Error uploading CSV to S3: %s", error)

    def create_dataframe_for_csv(self, file):
        try:
            df = pd.DataFrame(file)
            LOGGER.info("First few rows of the DataFrame: \n%s", df.head())
            LOGGER.info("Columns in DataFrame: %s", df.columns)
            
            # Extract the username from the principalid column
            df['username'] = df['principalid'].apply(lambda x: x.split(':')[1])
            LOGGER.info("Transformed CloudTrail DataFrame with username column:\n%s", df.head())
            return df
        except Exception as error:
            LOGGER.error("Error creating DataFrame: %s", error)
            return None

    def query_dynamodb(self):
        try:
            current_date = datetime.datetime.now()
            last_month_date = current_date - datetime.timedelta(days=30)

            response = self.dd_client.scan(TableName=self.request_table)
            dynamodb_data = []
            for item in response['Items']:
                record = {
                    'AccountID': item.get('accountId', {}).get('S', ''),
                    'Email': item.get('email', {}).get('S', ''),
                    'Approver': item.get('approver', {}).get('S', 'N/A'),  # Assign default 'N/A' if empty
                    'Justification': item.get('justification', {}).get('S', ''),
                    'TicketNumber': item.get('ticketNo', {}).get('S', ''),
                    'StartTime': item.get('startTime', {}).get('S', ''),
                    'EndTime': item.get('endTime', {}).get('S', ''),
                    'username': item.get('email', {}).get('S', '')  # Use full email for username field
                }
                
                # Ensure only records within the last month are included
                if 'startTime' in item and 'S' in item['startTime']:
                    start_time = item['startTime']['S']
                    try:
                        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%fZ')  # Adjust format here
                        if start_time >= last_month_date:
                            dynamodb_data.append(record)
                    except ValueError:
                        LOGGER.error("Failed to parse startTime: %s", start_time)
                else:
                    dynamodb_data.append(record)

            return pd.DataFrame(dynamodb_data)
        except Exception as error:
            LOGGER.error("Error querying DynamoDB: %s", error)
            return None

    def save_dataframe_to_s3(self, df, base_filename):
        try:
            current_date_str = datetime.datetime.now().strftime('%Y-%m-%d')
            filename = f"{base_filename}_{current_date_str}.csv"
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            self.s3_client.put_object(Bucket=self.bucket_name, Key=filename, Body=csv_buffer.getvalue())
            LOGGER.info("Successfully saved DataFrame to S3 at %s/%s", self.bucket_name, filename)
            return filename
        except Exception as error:
            LOGGER.error("Error saving DataFrame to S3: %s", error)
            return None

def lambda_handler(event, context):
    try:
        LOGGER.info("Calling class object")
        obj = PIMRoleReport(event, context)
        LOGGER.info("Calling fetch_cloudtrail_logs function")
        query_responsecsv = obj.fetch_cloudtrail_logs()
        if not query_responsecsv:
            LOGGER.error("Failed to fetch CloudTrail logs.")
            return "FAILED"
        time.sleep(120)  # Increased wait time to ensure the file is available in S3
        ct_df_file = obj.get_csv_file_from_s3(obj.bucket_name, query_responsecsv)
        if ct_df_file is None:
            LOGGER.error("Failed to retrieve CSV file from S3")
            return "FAILED"
        LOGGER.info("Successfully retrieved the CSV file from S3")
        cloudtrail_df = obj.create_dataframe_for_csv(ct_df_file)
        if cloudtrail_df is None:
            LOGGER.error("Failed to create DataFrame from CSV")
            return "FAILED"
        LOGGER.info("Successfully created DataFrame from CSV file")
        
        # Log CloudTrail DataFrame
        LOGGER.info("CloudTrail DataFrame:\n%s", cloudtrail_df.head())

        # Save CloudTrail DataFrame to CSV in S3
        cloudtrail_csv_key = 'cloudtrail_dataframe.csv'

        # Query DynamoDB and create DataFrame
        dynamodb_df = obj.query_dynamodb()
        if dynamodb_df is None:
            LOGGER.error("Failed to create DataFrame from DynamoDB")
            return "FAILED"
        LOGGER.info("Successfully created DataFrame from DynamoDB data")
        
        # Log DynamoDB DataFrame
        LOGGER.info("DynamoDB DataFrame:\n%s", dynamodb_df.head())

        # Check if 'username' columns exist in both DataFrames
        if 'username' not in cloudtrail_df.columns:
            LOGGER.error("Column 'username' not found in CloudTrail DataFrame")
            return "FAILED"
        if 'username' not in dynamodb_df.columns:
            LOGGER.error("Column 'username' not found in DynamoDB DataFrame")
            return "FAILED"

        # Merge the DataFrames on the username field
        merged_df = pd.merge(cloudtrail_df, dynamodb_df, on='username', how='inner')
        LOGGER.info("Successfully merged DataFrames")
        
        # Log merged DataFrame
        LOGGER.info("Merged DataFrame:\n%s", merged_df.head())

        # Select the specified columns
        final_df = merged_df[['username', 'eventname', 'eventid', 'AccountID', 'Approver', 'Justification', 'TicketNumber', 'StartTime', 'EndTime']]

        # Log final DataFrame
        LOGGER.info("Final DataFrame:\n%s", final_df.head())

        # Save merged DataFrame to CSV in S3
        merged_csv_key = obj.save_dataframe_to_s3(final_df, 'pim_report')
        if not merged_csv_key:
            LOGGER.error("Failed to save merged DataFrame to S3")
            return "FAILED"

        return "SUCCESS"
    except Exception as ex:
        LOGGER.error("Lambda failed with the error: '%s'", ex)
        return "FAILED"

if __name__ == "__main__":
    # Test the lambda_handler function
    test_event = {}
    test_context = {}
    result = lambda_handler(test_event, test_context)
    LOGGER.info("Result: %s", result)
