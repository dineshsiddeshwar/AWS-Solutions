"""
This module is used to terminate the EC2 instance launched for CIS Report
"""

import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class TermianteEC2(object):
    """
    # Class: GetCISReport
    # Description: Check GetCISReport for the latest AMI
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        try:
            # get relevant input params from event
            global session
            self.ami_id = event['ami_id']
            self.ami_name = event['ami_name']
            self.instanceid = event['Instance_ID']
            session = boto3.session.Session()
            self.ec2_client = session.client('ec2', region_name='us-east-1')

        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            logger.error(self.reason_data)
            print("ERROR Self GetCISReport", exception)

    def terminate_ins(self):
        """
        The following method is used to terminate EC2 instance
        after updating the CIS score in Dynamo DB.
        """
        res_dict = {}
        try:
            response = self.ec2_client.terminate_instances(
                InstanceIds=[self.instanceid]
            )
            Instance_state = str(response['TerminatingInstances'][0]['CurrentState']['Name'])
            res_dict['ami_id'] = self.ami_id
            res_dict['ami_name'] = self.ami_name
            res_dict['Instance_ID'] = self.instanceid
            res_dict['Instance_Status'] = Instance_state
            return res_dict

        except Exception as exception:
            self.reason_data = "TermianteEC2 %s" % exception
            logger.error(self.reason_data)
            print("ERROR Termiante EC2", exception)
            return exception
def lambda_handler(event, context):
    """
    This is lambda handler calls the function to terminate EC2 instance
    """
    try:
        result_value = {}
        result_value.update(event)
        print("Received an event {}".format(event))
        terminate_instance = TermianteEC2(event, context)
        output_value = terminate_instance.terminate_ins()
        print("Output of the function : " + str(output_value))
        result_value.update(output_value)
        return result_value
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        return exception
