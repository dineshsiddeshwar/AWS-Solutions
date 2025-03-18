"""
This module is used to Enable EBS Default Encryption in the child account.
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


class EnableEBSEncryption:
    """
    # Class: Enable EBS Default Encryption
    # Description: Includes method to Enable EBS Default Encryption in the child account
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            # get relevant input params from event
            session_client = boto3.Session()

            self.reason_data = ""
            self.res_dict = {}
            self.sts_client = session_client.client('sts')
            self.account_number = event['accountNumber']
            self.region = event['whitelisted_regions']
            self.child_account_role_arn = "arn:aws:iam::{}:role/platform_service_inflation". \
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

    def get_ebs_encrypt(self):
        """
        Check EBS Default Encryption status in the child account.
        """
        try:
            print('Check EBS Default Encryption Status function')
            for region in self.region:
                print('Inside Region - {}'.format(region))
                ec2_client = self.child_assume_role_session.client('ec2', region_name=region)
                response = ec2_client.get_ebs_encryption_by_default()
                if response['EbsEncryptionByDefault'] is False:
                    self.enable_ebs_encrypt(ec2_client)
                elif response['EbsEncryptionByDefault'] is True:
                    self.validate_ebs_encrypt(response)

        except Exception as exception:
            print("ERROR Checking Status", exception)
            self.reason_data = "Enable EBS Default Encryption Status %s" % exception
            LOGGER.error(self.reason_data)
            self.res_dict['Enable EBS Encryption'] = 'FAILED'
            return self.res_dict
        return self.res_dict

    def enable_ebs_encrypt(self, ec2_client):
        """
        Lambda Function to Enable EBS Default Encryption status in the child account.
        """
        print("Enable Encryption Function")
        response = ec2_client.enable_ebs_encryption_by_default()
        self.validate_ebs_encrypt(response)

    def validate_ebs_encrypt(self, response):
        """
        Lambda Function to Validate Enable EBS Default Encryption status in the child account.
        """
        print("Validate Status Function")
        if response['EbsEncryptionByDefault'] is True:
            self.res_dict['Enable EBS Encryption'] = 'PASSED'
        else:
            raise Exception('Validation of Enable EBS Default Encryption Failed')


def lambda_handler(event, context):
    """"
    Lambda handler that calls the function to Enable EBS Default Encryption
    """
    result_value = {}
    try:
        result_value.update(event)
        enable_ebs_encryption_obj = EnableEBSEncryption(event, context)
        output_value = enable_ebs_encryption_obj.get_ebs_encrypt()
        print("Output of the function : " + str(output_value))
        result_value.update(output_value)
        return result_value

    except Exception as exception:
        print("Error in Lambda Handler", exception)
        result_value['Handler Exception'] = str(exception)
        return result_value
