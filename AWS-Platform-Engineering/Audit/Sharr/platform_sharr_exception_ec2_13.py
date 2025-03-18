import json, boto3, logging, os, datetime


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')


class SshRdpException(object):
    """
    
    # Class: SSH RDP Exception
    # Description: Skip the SHARR workflow based on tags and approval for Open SSH/RDP ports finding
    """
    def __init__(self, event, context):
        try:
            self.event = event
            self.context = context
            LOGGER.info("Event: %s" % self.event)
            LOGGER.info("Context: %s" % self.context)
            #Capturing current timestamp in IST timezone to use in Step Function execution name
            self.timestamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).strftime('%Y-%m-%d-%H-%M-%S')
            print(f'Current timestamp in IST is {self.timestamp}')
            #Fetching Security Group ID, target member AWS Account ID and AWS region from Security Hub finding event
            self.security_group_id = event['detail']['findings'][0]['Resources'][0]['Details']['AwsEc2SecurityGroup']['GroupId']
            print(f'Security Group ID: {self.security_group_id}')
            self.account_id = event['detail']['findings'][0]['Resources'][0]['Details']['AwsEc2SecurityGroup']['OwnerId']
            print(f'Account ID: {self.account_id}')
            self.region = event['detail']['findings'][0]['Resources'][0]['Region']
            print(f'AWS Region: {self.region}')
            #Assuming cross-account IAM role from target member AWS account
            print(f'Creating Session and EC2 Client for target AWS account {self.account_id}')
            ec2_session = boto3.session.Session()
            ec2_sts_client = ec2_session.client('sts')
            child_account_role_arn = "arn:aws:iam::" + self.account_id + ":role/SO0111-SHARR-Orchestrator-Member"
            child_account_role_creds = ec2_sts_client.assume_role(RoleArn=child_account_role_arn,
                                                                RoleSessionName='DescribeSgTagsSession',
                                                                DurationSeconds=900)
            ec2_credentials = child_account_role_creds.get('Credentials')
            ec2_accessKeyID = ec2_credentials.get('AccessKeyId')
            ec2_secretAccessKey = ec2_credentials.get('SecretAccessKey')
            ec2_sessionToken = ec2_credentials.get('SessionToken')
            self.ec2_assumeRoleSession = boto3.session.Session(ec2_accessKeyID, ec2_secretAccessKey, ec2_sessionToken)
            self.ec2_client = self.ec2_assumeRoleSession.client('ec2', region_name=self.region)
            #Assuming cross-account IAM role from payer AWS account
            print("Creating Session and DynamoDB Client for payer AWS account")
            ddb_session = boto3.session.Session()
            ddb_client = ddb_session.client('sts')
            payer_account_role_arn = "arn:aws:iam::" + os.environ['PAYER_ACCOUNT_ID'] + ":role/platform-sharr-exception-ec2-13-role"
            payer_account_role_creds = ddb_client.assume_role(RoleArn=payer_account_role_arn,
                                                                RoleSessionName='SHARRDynamoDBSession',
                                                                DurationSeconds=900)
            ddb_credentials = payer_account_role_creds.get('Credentials')
            ddb_accessKeyID = ddb_credentials.get('AccessKeyId')
            ddb_secretAccessKey = ddb_credentials.get('SecretAccessKey')
            ddb_sessionToken = ddb_credentials.get('SessionToken')
            self.ddb_assumeRoleSession = boto3.session.Session(ddb_accessKeyID, ddb_secretAccessKey, ddb_sessionToken)
            self.ddb_client = self.ddb_assumeRoleSession.client('dynamodb', region_name=AWS_REGION)
            #Step Function Session
            self.sf_client = boto3.client('stepfunctions', region_name=AWS_REGION)
            #Security Hub Session
            self.sh_client = boto3.client('securityhub', region_name=AWS_REGION)
            #Storing Lambda function environment variables values
            self.exception_tag_key = os.environ['EXCEPTION_TAG_KEY'].lower()
            self.exception_tag_value = os.environ['EXCEPTION_TAG_VALUE'].lower()
            self.ddb_table_name = os.environ['EXCEPTION_DDB_TABLE']
            self.sf_arn = os.environ['STEP_FUNCTION_ARN']
        except Exception as error:
            LOGGER.info(error)
            return error

    def start_sharr_execution(self):
        """
        Starts SHARR framework Step Function execution if requested exception is not approved
        """
        try:
            print("Entering start_sharr_execution function...")
            sf_response = self.sf_client.start_execution(
                stateMachineArn=self.sf_arn,
                name=f'{self.account_id}-{self.region}-{self.security_group_id}-{self.timestamp}',
                input=json.dumps(self.event)
            )
            print(sf_response)
            return True
        except Exception as ex:
            LOGGER.info("Could not start Step Function execution. Error Code: %s, Error Reason: %s", ex.response['Error']['Code'], ex.response['Error']['Message'])
            return False

    def suppress_sh_finding(self):
        """
        Suppresses Security Hub findings if requested exception is approved
        """
        try:
            print("Entering suppress_sh_finding function...")
            sh_response = self.sh_client.batch_update_findings(
                FindingIdentifiers=[
                    {
                        'Id': self.event['detail']['findings'][0]['Id'],
                        'ProductArn': self.event['detail']['findings'][0]['ProductArn']
                    }
                ],
                Workflow={
                    'Status':'SUPPRESSED'
                },
                Note={
                    'Text': 'Suppressed finding by SHARR SSH/RDP Port Exception Lambda function',
                    'UpdatedBy': os.environ['AWS_LAMBDA_FUNCTION_NAME']
                }
            )
            print(sh_response)
            return True
        except Exception as ex:
            LOGGER.info("Could not suppress Security Hub findings %s. Error Code: %s, Error Reason: %s", self.event['detail']['findings'][0]['Id'], ex.response['Error']['Code'], ex.response['Error']['Message'])
            return False

    def verify_ddb(self):
        """
        Verifies Security Group ID from DynamoDB table in Payer account
        """
        try:
            print("Entering verify_ddb function...")
            ddb_response = self.ddb_client.query(
                TableName=self.ddb_table_name,
                Select='ALL_ATTRIBUTES',
                ExpressionAttributeValues={
                    ':v1': {
                        'S': self.security_group_id,
                    },
                },
                KeyConditionExpression='SecurityGroupID = :v1',
            )
            print("Printing DynamoDB table response")
            print(ddb_response)
            if ddb_response['Count'] == 0:
                print(f'Security Group ID {self.security_group_id} does not exist in exception DynamoDB table {self.ddb_table_name}')
                return False
            else:
                print(f"Query Response from Port Exception DynamoDB Table: {ddb_response['Items'][0]}")
                return ddb_response['Items'][0]
        except Exception as ex:
            LOGGER.info("Could not verify entry from DynamoDB table for Security Group %s. Error Code: %s, Error Reason: %s", self.security_group_id, ex.response['Error']['Code'], ex.response['Error']['Message'])
            return False

    def port_exception_verification(self):
        """
        Fetches the tags of Security Group from target member account 
        """
        if self.security_group_id is None:
            LOGGER.info("No Security Group to describe")
            return False
        try:
            print("Entering port_exception_verification function...")   
            describe_sg_response = self.ec2_client.describe_security_groups(GroupIds=[self.security_group_id])
            print(describe_sg_response)
            print(f'Exception Tag Key: {self.exception_tag_key} & Exception Tag Value: {self.exception_tag_value}')
            print("Checking if the tag key pair of Security Group from input event matches with the exempted tags...")
            security_group = describe_sg_response.get('SecurityGroups', [])
            print(security_group)
            for group in security_group:
                tags = group.get('Tags', [])
                for tag in tags:
                    sg_tag_key = tag.get('Key').lower()
                    sg_tag_value = tag.get('Value').lower()
                    print(f'Target Security Group Tag Key: {sg_tag_key} & Target Security Group Tag Value: {sg_tag_value}')
                    if tag.get('Key').lower() == self.exception_tag_key and tag.get('Value').lower() == self.exception_tag_value:
                        print("Security Group tag key pair from input event matches with the exempted tag key pair. Hence, verifying its approval from DynamoDB table...")
                        verify_ddb_response = self.verify_ddb()
                        if verify_ddb_response:
                            print("Printing verify_ddb function results")
                            ddb_sg_id = verify_ddb_response.get('SecurityGroupID').get('S')
                            ddb_account_id = verify_ddb_response.get('AccountID').get('S')
                            ddb_aws_region = verify_ddb_response.get('AWSRegion').get('S')
                            ddb_ticket_id = verify_ddb_response.get('TicketID').get('S')
                            print(f'Security Group ID: {ddb_sg_id}\nAccount ID: {ddb_account_id}\nAWS Region: {ddb_aws_region}\nTicket ID: {ddb_ticket_id}')
                            if verify_ddb_response.get('AccountID').get('S') == self.account_id:
                                print("Both Account IDs match from input event & DynamoDB table. Checking AWS region...")
                                if verify_ddb_response.get('AWSRegion').get('S') == self.region:
                                    print("Both AWS regions match from input event & DynamoDB table. Will suppress Security Hub finding...")
                                    return True
                                else:
                                    print("Region entry in DynamoDB table does not match with the input event. Please confirm the DynamoDB table region entry with the requested region")
                                    print("Since, input event region does not match with the DynamoDB table region entry, will execute SHARR framework...")
                                    return False
                            else:
                                print("Account ID entry in DynamoDB table does not match with the input event. Please confirm the DynamoDB table account ID entry with the requested account ID")
                                print("Since, input event account ID does not match with the DynamoDB table account ID entry, will execute SHARR framework...")
                                return False
                        else:
                            print("Exception DynamoDB table verification failed")
                            return False
                    else:
                        print(f'Target Security Group tag key pair: {sg_tag_key} & {sg_tag_value} does not match with Exception tag key pair: {self.exception_tag_key} & {self.exception_tag_value}. Checking next tag key pair...')
                print("Exception tag key pair does NOT match with any of the tag key pair of Security Group from input event. Hence, executing SHARR Step Function...")
                return False
        except Exception as ex:
            LOGGER.info("Could not describe Security Group %s. Error Code: %s, Error Reason: %s", self.security_group_id, ex.response['Error']['Code'], ex.response['Error']['Message'])
            return False


def lambda_handler(event, context):
    """
    SHARR_Exception_SSH_RDP Lambda function handler
    """
    try:
        ssh_rdp_exception = SshRdpException(event, context)
        verification_response = ssh_rdp_exception.port_exception_verification()
        print(verification_response)
        if verification_response:
            sh_suppress_response = ssh_rdp_exception.suppress_sh_finding()
            print("Security Hub finding has been suppressed")
            print(sh_suppress_response)
            return sh_suppress_response
        else:
            ssh_rdp_exception.start_sharr_execution()
        return
    except Exception as ex:
        LOGGER.error("SHARR Exception Lambda has failed. Error Code: %s, Error Reason: %s", ex.response['Error']['Code'], ex.response['Error']['Message'])
        return event