
import time
import boto3
import os
import logging
from botocore.config import Config
from datetime import datetime

year = str(datetime.today().year)
month = str(datetime.today().month)
day = str(datetime.today().day)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
logger.addHandler(CH)

class FailedBackupsReport(object):
    def __init__(self, event, context):
        self.athena_client = boto3.client('athena')
        self.s3_client = boto3.client('s3', config=Config(signature_version='s3v4'))
        self.s3_resource = boto3.resource('s3')

        try:
            self.database = os.environ['DATABASE']
            self.output_bucket = os.environ['OUTPUTBUCKET']
            self.query = os.environ['QUERY']
        except Exception as exp:
            logger.info('Failed at init')
            raise Exception(str(exp))
            
    def athena_query(self,query):
        response = self.athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': self.database
            },
            ResultConfiguration={
                'OutputLocation': 's3://{}/'.format(self.output_bucket)
            }
        )
        time.sleep(5)
        return response['QueryExecutionId']

    def get_athena_results(self, query_id):
        status = False
        while status != True:
            response = self.athena_client.get_query_execution(
                QueryExecutionId=query_id
            )
            if response['QueryExecution']['Status']['State'] == ('FAILED' or 'CANCELLED'):
                query_id = self.athena_query()
            elif response['QueryExecution']['Status']['State'] == ('RUNNING' or 'QUEUED'):
                time.sleep(5)
            elif response['QueryExecution']['Status']['State'] == 'SUCCEEDED':
                status = True

        return query_id


    def rename_file(self, file_name):
        now = datetime.now()
        day = now.strftime('%d')
        month = now.strftime('%B')
        year = now.strftime('%Y')
        key = 'Daily-Reports/failed_backup_jobs_{}_{}_{}.csv'.format(day,month,year)
        copy_source = '{}/{}.csv'.format(self.output_bucket, file_name)
        self.s3_client.copy_object(
            CopySource=copy_source, 
            Bucket=self.output_bucket, 
            Key=key
        ) 
        return key

    def generate_report_main(self):
        query_id = self.athena_query(self.query)
        file_location = self.get_athena_results(query_id)
        new_file_location = self.rename_file(file_location)

def lambda_handler(event, context):
    failed_backups_report = FailedBackupsReport(event, context)
    failed_backups_report.generate_report_main()

