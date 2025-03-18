"""
This module is used to segregate the logs for Config and CloudTrail from a
single bucket into respective S3 buckets
"""
import os
import logging
import json
import boto3

LOGGER = logging.getLogger('logging')
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


class FilterLogs:
    """
    # Class: Filter Logs between Config & CloudTrail
    # Description: Includes method to filter and copy files into S3 Bucket
    """

    def __init__(self, event, context):

        try:
            # get relevant input params from event
            self.reason_data = ""
            self.res_dict = {}
            self.event = event
            self.context = context
            LOGGER.info("Event: %s" % self.event)
            LOGGER.info("Context: %s" % self.context)

            session_client = boto3.Session()
            self.s3_client = session_client.client('s3')

            self.res_dict = {}
            self.setup = os.environ['setup_env']
            self.ou_id = os.environ['ou_id']
            self.event = event

        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)

    def filter_copy_logs(self):
        """
        Method to Filter and Copy S3 Files to S3 Buckets
        """
        try:
            print("Inside Filter and Copy S3 Files Function")
            for record in self.event['Records']:
                event_data = json.loads(record['body'])
                s3_data = event_data['Records'][0]['s3']
                src_bucket = s3_data['bucket']['name']
                src_key = s3_data['object']['key']
                config_bucket = 'platform-da2-central-config-{}'.format(self.setup)
                cloud_trail_bucket = 'platform-da2-central-cloudtrail-{}'.format(self.setup)

                destination_bucket = ''
                destination_bucket_key = src_key.strip(self.ou_id)

                if '/Config/' in src_key:
                    destination_bucket = config_bucket
                elif '/CloudTrail/' in src_key:
                    destination_bucket = cloud_trail_bucket
                else:
                    self.res_dict['destination_bucket'] = 'None'

                self.res_dict['destination_bucket'] = destination_bucket
                self.res_dict['destination_bucket_key'] = destination_bucket_key
                self.res_dict['source_bucket'] = src_bucket
                self.res_dict['source_key'] = src_key

                copy_response = self.s3_client.copy_object(Bucket=destination_bucket,
                                                           Key=destination_bucket_key,
                                                           CopySource={'Bucket': src_bucket,
                                                                       'Key': src_key},
                                                           MetadataDirective='REPLACE')
                self.res_dict['CopyResult'] = copy_response['CopyObjectResult']['ETag']
                self.validate_logs()

        except Exception as exception:
            print("ERROR Filtering & Copying S3 Files", exception)
            self.reason_data = "Filter & Copy S3 Files - %s" % exception
            LOGGER.error(self.reason_data)
            self.res_dict['LogsSegregation'] = 'FAILED'
            return self.res_dict

        return self.res_dict

    def validate_logs(self):

        print('Inside Log Validation')
        if self.res_dict['CopyResult'] is not None:
            self.res_dict['LogsSegregation'] = 'PASSED'
        else:
            raise Exception('Copy of Findings failed')


def lambda_handler(event, context):
    """
    Lambda handler that calls the function to enable Security Hub
    """
    result_value = {}
    try:
        filter_obj = FilterLogs(event, context)
        output_value = filter_obj.filter_copy_logs()
        print("Output of the function : " + str(output_value))
        result_value.update(output_value)
        return result_value

    except Exception as exception:
        print("Error in Lambda Handler", exception)
        result_value['Exception'] = str(exception)
        return result_value
