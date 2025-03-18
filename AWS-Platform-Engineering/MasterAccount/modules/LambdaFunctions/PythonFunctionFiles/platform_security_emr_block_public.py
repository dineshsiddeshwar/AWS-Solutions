"""
This module is used to Enable EMR Block Public Settings in the child account.
"""
import random
import logging
import boto3

LOGGER = logging.getLogger('logging')
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


class EnableEMRBlockPublic:
    """
    # Class: Enable EMR Block Public Settings
    # Description: Includes method to Enable EMR Block Public Settings in the child account
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            # get relevant input params from event
            session_client = boto3.Session()

            self.res_dict = {}
            self.reason_data = ""
            self.sts_client = session_client.client('sts')
            self.account_number = event['accountNumber']
            self.region = event['whitelisted_regions']
            self.child_account_role_arn = "arn:aws:iam::{}:role/AWSControlTowerExecution". \
                format(self.account_number)
            self.child_account_session_name = "childAccountSession-" + \
                                              str(random.randint(1, 100000))
            self.child_account_role = self.sts_client.assume_role(
                RoleArn=self.child_account_role_arn,
                RoleSessionName=self.child_account_session_name)
            self.child_credentials = self.child_account_role.get('Credentials')
            self.child_access_key = self.child_credentials.get('AccessKeyId')
            self.child_secret_access_key = self.child_credentials.get('SecretAccessKey')
            self.child_session_token = self.child_credentials.get('SessionToken')
            self.child_assume_role_session = boto3.Session(
                self.child_access_key,
                self.child_secret_access_key,
                self.child_session_token)

        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)

    def enable_emr_block_public(self):
        """
        Lambda Function to Enable EMR Block Public Settings in the child account.
        """
        print("Enable EMR Block Public Settings Function")
        try:
            for region in self.region:
                print('Inside Region - {}'.format(region))
                emr_client = self.child_assume_role_session.client('emr', region_name=region)
                emr_client.put_block_public_access_configuration(
                    BlockPublicAccessConfiguration={
                        'BlockPublicSecurityGroupRules': True,
                        'PermittedPublicSecurityGroupRuleRanges': [
                            {
                                'MinRange': 0,
                                'MaxRange': 0
                            }
                        ]
                    }
                )
                self.validate_emr_block_public(emr_client)

        except Exception as exception:
            print("ERROR Checking Status", exception)
            self.reason_data = "Enable EMR Block Public Settings %s" % exception
            LOGGER.error(self.reason_data)
            self.res_dict['Enable EMR Block Public'] = 'FAILED'
            return self.res_dict
        return self.res_dict

    def validate_emr_block_public(self, emr_client):
        """
        Lambda Function to Validate Enable EMR Block Public Settings in the child account.
        """
        print("Validate Status Function")
        response = emr_client.get_block_public_access_configuration()
        if response['BlockPublicAccessConfiguration']['BlockPublicSecurityGroupRules'] is True:
            self.res_dict['Enable EMR Block Public'] = 'PASSED'
        else:
            raise Exception('Validation of EMR Public Block Failed')


def lambda_handler(event, context):
    """"
    Lambda handler that calls the function to Enable EMR Block Public Settings
    """
    result_value = {}
    try:
        result_value.update(event)
        enable_emr_block_public_obj = EnableEMRBlockPublic(event, context)
        output_value = enable_emr_block_public_obj.enable_emr_block_public()
        print("Output of the function : " + str(output_value))
        result_value.update(output_value)
        return result_value

    except Exception as exception:
        print("Error in Lambda Handler", exception)
        result_value['Handler Exception'] = str(exception)
        return result_value
