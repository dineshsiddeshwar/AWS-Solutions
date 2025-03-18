import boto3
import logging
from time import sleep
from botocore.exceptions import ClientError

SUCCESS = "SUCCESS"
FAILED = "FAILED"
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

"""
This Lambda is used to add stacksets for the regions not governed by Control Tower
This lambda can be removed when CT enables the region
"""


class AddStackToStackset(object):
    def __init__(self, event, context):
        try:
            print(event, context)
            self.event = event
            self.context = context
            session_client = boto3.Session()
            self.CFT = session_client.client('cloudformation')
            self.ssm_client = session_client.client('ssm')
            # Name of the stackset for enabling config and its resources
            self.ss_name = "platform-enable-config-manual"
            self.account = event["accountNumber"]
            regions_response = self.ssm_client.get_parameter(Name="whitelisted_custom_regions")
            self.whitelisted_regions_ssm = regions_response['Parameter']['Value']
            self.regions = self.whitelisted_regions_ssm.split(',')

        except Exception as e:
            raise Exception(str(e))

    def does_stack_set_instance_exists(self):
        """Return True if stackset Instance already exists"""
        result = False
        ss_list = list()

        try:
            cft_paginator = self.CFT.get_paginator('list_stack_instances')
            cft_page_iterator = cft_paginator.paginate(StackSetName=self.ss_name)
            for page in cft_page_iterator:
                ss_list += page['Summaries']

            for item in ss_list:
                if item['Account'] == self.account and item['Status'] == 'CURRENT':
                    self.event["custom_stackset_status"] = item['Status']
                    result = True

        except Exception as exe:
            LOGGER.error('Unable to list stacksets %s', str(exe))

        return result

    def add_stack_instance(self):
        """ Adds StackSet Instances """

        result = {'OperationId': None}
        ops = {
            'MaxConcurrentPercentage': 1,
            'FailureTolerancePercentage': 0
        }
        output = self.does_stack_set_instance_exists()

        if not output:
            try:
                LOGGER.info('Add Stack Set Instances')
                result = self.CFT.create_stack_instances(StackSetName=self.ss_name,
                                                         Accounts=[self.account],
                                                         Regions=self.regions,
                                                         OperationPreferences=ops)
                operationId = result['OperationId']
                self.get_stack_operation_status(operationId)
            except ClientError as exe:
                LOGGER.error("Unexpected error: %s", str(exe))
                result['Status'] = exe
        else:
            LOGGER.error('StackSet instance %s already exist', self.account)

    def get_stack_operation_status(self, operation_id):
        """ Wait and return the status of the operation """

        count = 25
        status = 'UNKNOWN'

        while count > 0:
            count -= 1
            try:
                output = self.CFT.describe_stack_set_operation(StackSetName=self.ss_name,
                                                               OperationId=operation_id)
                status = output['StackSetOperation']['Status']
            except Exception as exe:
                count = 0
                LOGGER.error('Stackset operation check failed: %s', str(exe))
                self.event["custom_stackset_status"] = status

            if status == 'RUNNING':
                LOGGER.info('Stackset operation %s, waiting for 30 sec', status)
                sleep(30)
            elif status in ['FAILED', 'STOPPING', 'STOPPED', 'UNKNOWN']:
                LOGGER.error('Exception on stackset operation: %s', status)
                count = 0
                self.event["custom_stackset_status"] = status
                break
            elif status == 'SUCCEEDED':
                LOGGER.info('StackSet Operation Completed: %s', status)
                self.event["custom_stackset_status"] = status
                break
        return count > 0


def lambda_handler(event, context):
    try:
        stack_set_object = AddStackToStackset(event, context)
        stack_set_object.add_stack_instance()
        return event
    except Exception as e:
        print(str(e))
