"""
This module is used to Get Security Hub Findings and Invoke the respective
child Lambda for Remediation or Notification
"""

import logging
import json
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


class GetFindingsAndInvoke:
    """
    # Class: Get Findings from Security Hub and Invoke
    # Description: Includes method to Get Findings from Security Hub and invoke
      the respective Child Lambda
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            # get relevant input params from event

            self.reason_data = ""
            self.session_client = boto3.Session()

            self.res_dict = {}
            self.event = event
            print(self.event)

        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)

    def get_findings_invoke(self):
        """
        Get Findings & Invoke Child Lambda.
        """
        try:
            for record in self.event['Records']:
                print(record)
                event_data = json.loads(record['body'])
                account_id = event_data['account']
                region = event_data['region']
                resources = event_data['resources'][0]
                compliance = event_data['detail']['findings'][0]['Compliance']['Status']
                lambda_arn = 'arn:aws:lambda:' + region + ':' + account_id + ':function:'
                lambda_client = self.session_client.client('lambda', region_name=region)
                # if ('cis-aws-foundations-benchmark/v/1.2.0/4.1/' in resources) or \
                #         ('cis-aws-foundations-benchmark/v/1.2.0/4.2/' in resources):
                if ('aws-foundational-security-best-practices/v/1.0.0/EC2.18/' in resources) or \
                        ('security-control/EC2.13/' in resources) or \
                        ('security-control/EC2.14/' in resources) or \
                        ('security-control/EC2.18/' in resources) or \
                        ('security-control/EC2.19/' in resources) or \
                        ('aws-foundational-security-best-practices/v/1.0.0/EC2.19/' in resources):
                    invoke_child = lambda_client.invoke(
                        FunctionName=lambda_arn + 'platform_remediate_port_22_3389',
                        InvocationType='Event',
                        Payload=json.dumps(event_data),
                    )
                    self.res_dict['StatusCode'] = invoke_child['StatusCode']
            if self.res_dict['StatusCode'] == 202:
                self.res_dict['Send Notification'] = 'PASSED'

        except Exception as exception:
            print("ERROR Getting Findings", exception)
            self.reason_data = "Get Findings & Invoke Lambda - %s" % exception
            LOGGER.error(self.reason_data)
            self.res_dict['Send Notification'] = 'FAILED'
            return self.res_dict
        return self.res_dict


def lambda_handler(event, context):
    """
    Lambda handler that calls the function to get findings and invoke lambda
    """
    result_value = {}
    try:
        sec_hub_obj = GetFindingsAndInvoke(event, context)
        output_value = sec_hub_obj.get_findings_invoke()
        print("Output of the function : " + str(output_value))
        result_value.update(output_value)
        return result_value

    except Exception as exception:
        print("Error in Lambda Handler", exception)
        result_value['Handler Exception'] = str(exception)
        return exception
