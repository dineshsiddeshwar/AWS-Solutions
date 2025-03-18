import random
import boto3
import logging

LOGGER = logging.getLogger('logging')
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


class TagExceptionAMIs(object):
    """
    # Class: TagExceptionAMIs
    # Description: To Tag AMIs passed as an event to this lambda as an exception
    Standalone lambda which require below event, Append data in list when you update more than 1 time
        {
            "TargetAccountNumber" : "<AccountID>",
            "exception_amis_name" : ["<ami name, ex :amzn-ec2-macos-*>"],
            "owners_id" : ["<AMI_owner_ID, ex : 123456789012 or amazon>"],
            "regions" :["<region name which is asked to enable AMI, ex: "us-east-1", "eu-west-1>"]
        }
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        LOGGER.info("Event: %s" % self.event)
        LOGGER.info("Context: %s" % self.context)
        try:
            self.reason_data = ""
            session_client = boto3.Session()
            self.sts_client = session_client.client('sts')
            self.ssm_client = session_client.client('ssm')
            self.dynamodb_client = session_client.client('dynamodb', region_name="us-east-1")
            self.regions = event["regions"]
            self.account_number = str(event['TargetAccountNumber'])
            self.exception_amis = event['exception_amis_name']
            self.ami_owners = event["owners_id"]
            ami_tags_response = self.ssm_client.get_parameter(Name="ami_tags")
            self.ami_tags_str = ami_tags_response['Parameter']['Value']
            self.tagging = self.ami_tags_str.split(',')
            acnts_table_response = self.ssm_client.get_parameter(Name="ExceptionAMIDynamoDBTableName")
            self.exception_ami_table_name = acnts_table_response['Parameter']['Value']
            secondaryRoleArn = "arn:aws:iam::{}:role/AWSControlTowerExecution".format(self.account_number)
            secondarySessionName = "SecondarySession-" + str(random.randint(1, 100000))

            # Logging to child account.
            secondaryRoleCreds = self.sts_client.assume_role(RoleArn=secondaryRoleArn,
                                                             RoleSessionName=secondarySessionName)
            credentials = secondaryRoleCreds.get('Credentials')
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)

    def tag_exception_describe_images(self):
        try:
            for region in self.regions:
                ec2_client = self.assumeRoleSession.client('ec2', region_name=region)
                print("ENTERING INTO REGION", region)
                response = ec2_client.describe_images(
                    Owners=self.ami_owners,
                    Filters=[
                        {'Name': 'name', 'Values': self.exception_amis}
                    ]
                )
                images = response['Images']
                print("IMAGES DESCRIBED ARE ", images)
                self.tag_exception_tagging_images(images, ec2_client)
        except Exception as exception:
            print("Error in describing Images", exception)
            self.reason_data = "Exception in AMI Describing %s" % exception
            LOGGER.error(self.reason_data)

    def tag_exception_tagging_images(self, images, ec2_client):
        try:
            for image in images:
                image_id = image['ImageId']
                print("Name of the Image", image['Name'])
                ec2_client.create_tags(Resources=[image_id], Tags=[{'Key': self.tagging[0],
                                                                    'Value': self.tagging[1], }, ], )
            print("AMIs Tagged Successful")
            self.update_account_table()
        except Exception as exception:
            print("ERROR AMI Tagging", exception)
            self.reason_data = "Exception in AMI Tagging %s" % exception
            LOGGER.error(self.reason_data)

    def update_account_table(self):
        try:
            exceptionAMIregions = ','.join(self.regions)
            exceptionAMIname = ','.join(self.exception_amis)
            ami_owners = ','.join(self.ami_owners)
            insert_response = self.dynamodb_client.put_item(
                TableName=self.exception_ami_table_name,
                Item={
                    'AccountNumber': {"S": self.account_number},
                    'ExceptionAMIName': {"S": exceptionAMIname},
                    'ExceptionAMIRegion': {"S": exceptionAMIregions},
                    'ExceptionAMIOwner': {"S": ami_owners}
                })
            print(insert_response)
            print(self.exception_ami_table_name, "Table updated with exception AMIs successfully!!!")

        except Exception as exception:
            print("DynamoDB Table updation failed!!!", exception)
            self.reason_data = "DynamoDB Table update Failed %s" % exception
            LOGGER.error(self.reason_data)


def lambda_handler(event, context):
    try:
        tag_exception_ami_obj = TagExceptionAMIs(event, context)
        tag_exception_ami_obj.tag_exception_describe_images()
    except Exception as exception:
        print("Error in Lambda Handler", exception)
