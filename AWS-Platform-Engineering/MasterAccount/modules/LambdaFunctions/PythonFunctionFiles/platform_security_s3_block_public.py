"""
This module is used to Enable Block Public Access feature of S3 in the child account.
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


class S3BlockPublicAccess:
    """
    # Class: Block Public Access feature of S3
    # Description: Includes method to Block Public Access feature of S3 in the child account
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
            self.req_status = {
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                     }
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
            self.s3_client = self.child_assume_role_session.client('s3control')

        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)

    def s3_block_public(self):
        """
        Check Block Public Access feature of S3 status in the child account.
        """
        try:
            print('Get Block Public Access feature of S3 function')
            get_status = self.s3_client.get_public_access_block(AccountId=self.account_number)
            if get_status['PublicAccessBlockConfiguration'] == self.req_status:
                self.validate_status()
            else:
                self.enable_s3_block_public()
        except Exception as error:
            print(str(error))
            try:
                print('Calling Enable S3 Block Public Access function')
                self.enable_s3_block_public()
            except Exception as exception:
                print("ERROR Checking Status", exception)
                self.reason_data = "Block Public Access feature of S3 Status %s" % exception
                LOGGER.error(self.reason_data)
                self.res_dict['Public Access Block Configuration'] = 'FAILED'
                return self.res_dict
        return self.res_dict

    def enable_s3_block_public(self):
        """
        Lambda Function to Validate Block Public Access feature of S3 status in the child account.
        """
        print("Enable Block Public Access feature of S3 function")
        self.s3_client.put_public_access_block(
            PublicAccessBlockConfiguration=self.req_status,
            AccountId=self.account_number
        )
        self.validate_status()

    def validate_status(self):
        """
        Lambda Function to Validate Block Public Access feature of S3 status in the child account.
        """
        print("Validate Status Function")
        self.res_dict['Public Access Block Configuration'] = 'PASSED'


def lambda_handler(event, context):
    """"
    Lambda handler that calls the function to enable Block Public Access feature of S3
    """
    result_value = {}
    try:
        result_value.update(event)
        s3_block_public_access_obj = S3BlockPublicAccess(event, context)
        output_value = s3_block_public_access_obj.s3_block_public()
        print("Output of the function : " + str(output_value))
        result_value.update(output_value)
        return result_value

    except Exception as exception:
        print("Error in Lambda Handler", exception)
        result_value['Handler Exception'] = str(exception)
        return result_value
