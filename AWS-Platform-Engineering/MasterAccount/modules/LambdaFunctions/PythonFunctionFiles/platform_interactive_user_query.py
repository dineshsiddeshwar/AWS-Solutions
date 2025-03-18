import boto3
import logging
import os
import time
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryrunLambda1(object):
    def __init__(self, bucket_name, account_id_payer):
        logger.info("Initializing QueryrunLambda1")
        self.session = boto3.session.Session()
        self.cloudtrail_client = self.session.client('cloudtrail')
        self.bucket_name = bucket_name
        self.account_id_payer = account_id_payer
        self.lambda_client = boto3.client('lambda')  # Initialize Lambda client
        self.response = None  # Initialize response as an instance variable
        self.s3_object_uri = None  # Initialize s3_object_uri as an instance variable
        self.ssm_client = self.session.client('ssm')

    def run_query(self):
        try:
            s3_uri_value = 's3://' + self.bucket_name + '/'
            sender_response_datalakeid = self.ssm_client.get_parameter(Name='platform_datalakeid')
            datalake_id = sender_response_datalakeid['Parameter']['Value']
            query_statement = """
                SELECT DISTINCT requestParameters, recipientAccountId FROM """ + datalake_id + """ WHERE awsRegion = 'us-east-1' AND eventSource LIKE 'iam.amazonaws.com' AND eventName IN ('CreateUser','CreateLoginProfile')
            """

            self.response = self.cloudtrail_client.start_query(
                QueryStatement=query_statement,
                DeliveryS3Uri=s3_uri_value,
            )
            query_id = self.response['QueryId']
            account_id = self.get_account_id()  # Fetch account ID
            current_date = time.strftime("%Y/%m/%d")  # Fetch current date
            self.s3_object_uri = f'AWSLogs/{account_id}/CloudTrail-Lake/Query/{current_date}/{query_id}/result_1.csv.gz'
            logger.info("S3 Object URI: %s", self.s3_object_uri)
            time.sleep(420)

            # Call send_results
            self.send_results(self.s3_object_uri, query_id)

        except Exception as exception:
            logger.error("Error occurred: %s", exception)

    def send_results(self, s3_object_uri, query_id):
        try:
            # Invoke another Lambda function
            self.invoke_another_lambda(query_id, s3_object_uri)

        except Exception as exception:
            logger.error("Error occurred: %s", exception)

    def get_account_id(self):
        try:
            sts_client = boto3.client('sts')
            response = sts_client.get_caller_identity()
            account_id = response['Account']
            return account_id
        except Exception as ex:
            logger.error("Error occurred: %s", ex)
            return "FAILED"

    def invoke_another_lambda(self, query_id, s3_object_uri):
        try:
            # Define the payload for the Lambda function you want to invoke
            payload = {
                "query_id": query_id,
                "s3_object_uri": s3_object_uri
            }
            account_id_payer = self.get_account_id()
            # Specify the ARN of the Lambda function to invoke
            function_name = f"arn:aws:lambda:us-east-1:{account_id_payer}:platform_interactive_user_test"

            # Invoke the Lambda function
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='Event',  # Asynchronous invocation
                Payload=json.dumps(payload)
            )

            logger.info("Invocation of Lambda function successful: %s", response)

        except Exception as e:
            logger.error("Error occurred while invoking Lambda function: %s", e)

def lambda_handler(event, context):
    try:
        # Retrieve bucket name and account ID payer from environment variables
        bucket_name = os.environ.get('BUCKET')
        account_id_payer = os.environ.get('MASTER_ACCOUNT_ID')

        # Initialize QueryrunLambda1 object with bucket name and account ID payer
        query_runner = QueryrunLambda1(bucket_name, account_id_payer)

        # Run CloudTrail query
        query_runner.run_query()

        print("Query execution initiated")

    except Exception as ex:
        logger.error("Lambda failed with the error: %s", ex)
        return "FAILED"
