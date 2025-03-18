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


class TagExceptionAMIsScheduled(object):
    """
    # Class: TagExceptionAMIsScheduled
    # Description: Scheduled Exception AMI Tagging in the child account
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
            ami_tags_response = self.ssm_client.get_parameter(Name="ami_tags")
            self.ami_tags_str = ami_tags_response['Parameter']['Value']
            self.tagging = self.ami_tags_str.split(',')
            acnts_table_response = self.ssm_client.get_parameter(Name="ExceptionAMIDynamoDBTableName")
            self.exception_ami_table_name = acnts_table_response['Parameter']['Value']
        except Exception as exception:
            self.reason_data = "Missing required property %s" % exception
            LOGGER.error(self.reason_data)

    def get_exception_ami_accounts(self):
        try:
            # querying the exception AMI table
            query_response = \
                self.dynamodb_client.scan(TableName=self.exception_ami_table_name)
            print(query_response)
            try:
                for item in query_response["Items"]:
                    account_number = item['AccountNumber']['S']
                    regions = item['ExceptionAMIRegion']['S'].split(",")
                    ami_owners = item['ExceptionAMIOwner']['S'].split(",")
                    exception_amis = item['ExceptionAMIName']['S'].split(",")
                    secondaryRoleArn = "arn:aws:iam::{}:role/AWSControlTowerExecution".format(account_number)
                    secondarySessionName = "SecondarySession-" + str(random.randint(1, 100000))
                    secondaryRoleCreds = self.sts_client.assume_role(RoleArn=secondaryRoleArn,
                                                                     RoleSessionName=secondarySessionName)
                    credentials = secondaryRoleCreds.get('Credentials')
                    accessKeyID = credentials.get('AccessKeyId')
                    secretAccessKey = credentials.get('SecretAccessKey')
                    sessionToken = credentials.get('SessionToken')
                    assumerolesession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)
                    print("Assumed role in Account", account_number)
                    self.tag_exception_describe_images(assumerolesession, regions, ami_owners, exception_amis)
            except Exception as exception:
                print("Error in assuming the role in child account", exception)
                self.reason_data = "Error in assuming the role in child account" % exception
                LOGGER.error(self.reason_data)

        except Exception as exception:
            print("Error in scanning the DyanamoDB", exception)
            self.reason_data = "Error in scanning the DyanamoDB" % exception
            LOGGER.error(self.reason_data)

    def tag_exception_describe_images(self, assumerolesession, regions, ami_owners, exception_amis):
        try:
            for region in regions:
                ec2_client = assumerolesession.client('ec2', region_name=region)
                print("ENTERING INTO REGION", region)
                response = ec2_client.describe_images(
                    Owners=ami_owners,
                    Filters=[
                        {'Name': 'name', 'Values': exception_amis}
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
        except Exception as exception:
            print("ERROR AMI Tagging", exception)
            self.reason_data = "Exception in AMI Tagging %s" % exception
            LOGGER.error(self.reason_data)


def lambda_handler(event, context):
    try:
        tag_exception_ami_obj = TagExceptionAMIsScheduled(event, context)
        tag_exception_ami_obj.get_exception_ami_accounts()
    except Exception as exception:
        print("Error in Lambda Handler", exception)
