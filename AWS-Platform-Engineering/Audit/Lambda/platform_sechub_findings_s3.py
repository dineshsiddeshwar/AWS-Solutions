"""
This module is used to Get Master Security Hub Findings from the Audit account
"""

import logging
import json
import os
import boto3
import time

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


class GetUpdateFindings:
    """
    # Class: Get Findings from Master Security Hub
    # Description: Includes method to Get Findings from Master Security Hub
    from the Audit account
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            # get relevant input params from event
            self.reason_data = ""
            self.res_dict = {}
            self.session_client = boto3.Session()

            self.event = event
            print(self.event)

        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)

    def get_findings(self):
        """
        Get & Update Findings from Audit Account.
        """
        try:
            for record in self.event['Records']:
                print(record)
                event_data = json.loads(record['body'])
                print ("event data : ", event_data)
                region = event_data['region']
                print ("region  : ", region)
                finding_id = event_data['detail']['findings'][0].get('Id')
                print ("finding id  : ", finding_id)
                bucket_name = 'platform-da2-central-securityhub-' + os.environ['setup_env']
                print ("bucket name  : ", bucket_name)
                self.res_dict = {'destination_bucket': bucket_name}
                severity =  event_data['detail']['findings'][0].get('Severity')
                print("Severity label: ", severity['Label'])
                if severity['Label'] != "INFORMATIONAL" and severity['Label'] != "LOW" :
                    print("Finding severity is as expected hence uploads to s3:" , severity['Label'])
                    sec_hub_client = self.session_client.client('securityhub', region_name=region)
                    s3_client = self.session_client.client('s3', region_name=region)
                    retries = 0
                    get_finding_status = 'False'
                    while retries < 2 and get_finding_status == 'False':
                        get_finding = sec_hub_client.get_findings(
                            Filters={
                                'Id': [
                                    {
                                            'Value': finding_id,
                                        'Comparison': 'EQUALS'
                                        }
                                ]
                            }
                        )
                        print("result values of api : ", get_finding)
                        temp_res_code = get_finding['ResponseMetadata']['HTTPStatusCode']
                        if temp_res_code == 200:
                            get_finding_status = 'True'
                        else: 
                            time_to_sleep = 4 ** retries
                            retries += 1
                            time.sleep(time_to_sleep)
                    key_name = finding_id+'.JSON'
                    print("Key name :", key_name)
                    obj_data = json.dumps(get_finding['Findings'])
                    print("Object data :", obj_data)
                    put_response = s3_client.put_object(
                        ACL='bucket-owner-full-control',
                        Body=obj_data,
                        Bucket=bucket_name,
                        Key=key_name
                    )
                    print("upload in s3 bucket response", put_response)
                    self.res_dict['destination_bucket_key'] = key_name
                    self.res_dict['PutResult'] = put_response['ETag']
                    if self.res_dict['PutResult'] is not None:
                        self.res_dict['UploadFindings'] = 'PASSED'
                    else:
                        raise Exception('Uploading of Findings failed')
                else:
                    print("Skipping since finding severity lebel is other than expected", severity['Label'])
        except Exception as exception:
            print("ERROR Filtering & Copying S3 Files", exception)
            self.reason_data = "Filter & Copy S3 Files - %s" % exception
            LOGGER.error(self.reason_data)
            self.res_dict['UploadFindings'] = 'FAILED'
            return self.res_dict
        return self.res_dict

def lambda_handler(event, context):
    """
        Lambda handler that calls the function to accept get findings
    """
    result_value = {}
    try:
        sec_hub_obj = GetUpdateFindings(event, context)
        output_value = sec_hub_obj.get_findings()
        print("Output of the function : " + str(output_value))
        result_value.update(output_value)
        return result_value
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        result_value['Handler Exception'] = str(exception)
        return exception