"""
This module is used to Check SSM Agent Status for the Instance
"""
import boto3

class SSMReportingStatus(object):
    """
    # Class: SSMReportingStatus
    # Description: Check SSMReportingStatus for the provided Instance_ID
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        try:
            # get relevant input params from event
            global session
            self.ami_id = event['ami_id']
            self.ami_name = event['ami_name']
            self.instanceid = event['Instance_ID']
            session = boto3.session.Session()

        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            print("ERROR Self SSMReportingStatus", exception)

    def ssm_reporting_status(self):
        """
        The following method is used to check ssm reporting status of an instance.
        """
        res_dict = {}
        try:
            ssm_client = session.client('ssm')
            response = ssm_client.describe_instance_information(
                Filters=[
                    {
                        'Key': 'InstanceIds',
                        'Values': [self.instanceid]
                    }
                ]
            )
            res_dict['ami_id'] = self.ami_id
            res_dict['ami_name'] = self.ami_name
            res_dict['Instance_ID'] = self.instanceid
            res_dict['ssm_status'] = response['InstanceInformationList'][0].get('PingStatus')
            return res_dict

        except Exception as exception:
            self.reason_data = "SSMReportingStatus %s" % exception
            print("ERROR SSMReportingStatus EC2", exception)
            return exception


def lambda_handler(event, context):
    """
    Lamda handler that calls the ssm_reporting_status function
    """
    try:
        result_value = {}
        result_value.update(event)
        print("Received an event {}".format(event))
        reporting_status = SSMReportingStatus(event, context)
        output_value = reporting_status.ssm_reporting_status()
        print("Output of the function : " + str(output_value))
        result_value.update(output_value)
        return result_value
    except Exception as exception:
        print("Error in Lambda Handler", exception)
        return exception
