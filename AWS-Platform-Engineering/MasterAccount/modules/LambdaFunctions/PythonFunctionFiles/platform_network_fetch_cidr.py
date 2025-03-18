"""
This module is used to Fetches cidr block from ip management table
"""
import random
import json
import boto3
import logging
import requests


logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

SUCCESS = "SUCCESS"
FAILED = "FAILED"
FALSE = "false"
TRUE = "true"


class FetchCIDR(object):
    """
    # Class: FetchCIDR
    # Description: Fetches specified CIDR ranges for VPC creation and extension
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        self.res_dict = {}
        try:

            self.resource_properties = self.event['ResourceProperties']
            # get relevant input params from event
            self.account_id = self.resource_properties['AccountNumber']
            self.regions = self.event['region_ip_dict'].keys()
            self.region_ip_dict = self.event['region_ip_dict']
            print(self.regions)
            self.environment = self.resource_properties['Environment']
            self.response_data = self.event['response_data']
            self.cidr_row = {}
            self.event['fetch_cidr'] = TRUE
            self.consolidated_keys = []
            session = boto3.session.Session()
            ssm_client = session.client('ssm')
            sts_client = session.client('sts')
            self.dynamodb_client = session.client('dynamodb')

            self.cidr_table_name = ssm_client.get_parameter(Name='cidr_table_name')['Parameter']['Value']
            self.cidr_table_index = ssm_client.get_parameter(Name='cidr_table_index')['Parameter']['Value']
            self.sender_id = ssm_client.get_parameter(Name='sender_id')['Parameter']['Value']
            self.operations_dl = ssm_client.get_parameter(Name='failure_operation_dl')['Parameter']['Value']
            self.network_table_name = ssm_client.get_parameter(Name='platform_network_table_name')['Parameter']['Value']
            child_account_role_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))
            child_account_role_arn = "arn:aws:iam::" + self.account_id + ":role/AWSControlTowerExecution"
            child_account_role_creds = sts_client.assume_role(RoleArn=child_account_role_arn,
                                                              RoleSessionName=child_account_role_session_name)
            credentials = child_account_role_creds.get('Credentials')
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)

        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))
            raise Exception(str(exception))

    def fetch_vpc_cidr(self):
        try:
            cidr_list = []
            print("inside fetch_vpc_cidr")
            # Fetch free CIDR for selected regions for vpc creation
            for region, ip in self.region_ip_dict.items():
                if self.event['fetch_cidr'] == FALSE:
                        break
                print(region, ip)
                cidr_row = {}
                child_account_ec2_client = self.assumeRoleSession.client('ec2',region_name=region)
                vpc_response = child_account_ec2_client.describe_vpcs(
                    Filters=[
                        {
                            'Name': 'tag:Name',
                            'Values': ['platform-VPC']
                        }
                    ]
                )
                print (vpc_response)
                if len(vpc_response['Vpcs']) > 0:
                    print("inside row preparation")
                    cidr_row['vpc_id'] = vpc_response['Vpcs'][0]['VpcId']
                    print(cidr_row)
                    cidr_row['cidr'] = vpc_response['Vpcs'][0]['CidrBlock']
                    cidr_row['region'] = region
                    cidr_row['environment'] = self.environment
                    print(cidr_row)
                    logger.info("VPC already present. Hence skipping VPC Provision...")
                else:
                    cidr_row = self.get_cidr(region,ip)
                    if self.event['fetch_cidr'] == FALSE:
                        break
                cidr_list.append(cidr_row)
            self.event['CIDR_List'] = cidr_list
        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))
            return exception

    def fetch_extension_cidr(self):
        ''' Fetch free CIDR for vpc extension
             Also validates vpcid for extension'''
        try:

            print("Get extension details")
            for vpc_row in self.event['Extension_data']:
                print("Inside Extension",vpc_row['vpc_id'],vpc_row['ip'])

                # get region from network table
                query_response = \
                    self.dynamodb_client.query(TableName=self.network_table_name,
                                              Select='ALL_ATTRIBUTES', ConsistentRead=False,
                                              KeyConditionExpression="VPC_Id = :vi",
                                              ExpressionAttributeValues={":vi": {"S": vpc_row['vpc_id']}
                                                                          })
                print(query_response)

                if len(query_response['Items'])==1 and query_response['Items'][0]['AccountName']['S'] == self.event['business_account']:
                    # Valid vpc for extension
                    print("Network Items",query_response['Items'][0]['Region']['S'])
                    region = query_response['Items'][0]['Region']['S']
                    child_account_ec2_client = self.assumeRoleSession.client('ec2',region_name = region)

                    # Describe vpc to check existing extension
                    vpc_response =  child_account_ec2_client.describe_vpcs(
                                VpcIds=[
                                    vpc_row['vpc_id']
                                ])
                    print("VPC response",vpc_response)
                    cidr_set = vpc_response['Vpcs'][0]['CidrBlockAssociationSet']
                    cidr_count = len(cidr_set)
                    print(cidr_count,list(self.event['ResourceProperties'].values()).count(vpc_row['vpc_id']))
                    # checks if the number of existing associations for vpc is same as existing extension request
                    if cidr_count == list(self.event['ResourceProperties'].values()).count(vpc_row['vpc_id']):
                        # get cidr range
                        cidr_row = self.get_cidr(region,vpc_row['ip'])
                        if self.event['fetch_cidr'] == FALSE:
                            break
                        vpc_row.update(cidr_row)
                        print(vpc_row)
                else:
                    print("VPC  Not valid")
                    self.send(self.event, self.context, FAILED, self.response_data, "VPC Not available in network table")
                    self.event['fetch_cidr'] = FALSE
                    return

        except Exception as exception:
            print(str(exception))
            logger.error(str(exception))
            return exception

    def get_cidr(self,region,ip):
        '''Get IP from IP Management Table'''
        try:
            is_allocated = "FALSE"
            consolidated_key = ip + "|" + region + "|" + self.environment.lower()
            print(consolidated_key)
            # self.consolidated_keys.append(consolidated_key)
            print(self.cidr_table_index,self.cidr_table_name)
            query_response = \
                self.dynamodb_client.query(TableName=self.cidr_table_name,
                                          IndexName=self.cidr_table_index,
                                          Select='ALL_PROJECTED_ATTRIBUTES', ConsistentRead=False,
                                          KeyConditionExpression="consolidated_key = :ck AND is_allocated = :ia",
                                          ExpressionAttributeValues={":ck": {"S": consolidated_key},
                                                                      ":ia": {"S": is_allocated}})
            print(query_response)
            if len(query_response['Items']) < 1:
                print("No free CIDR ranges available to provision the VPC")
                print("VPC creation process will fail")
                self.event['fetch_cidr'] = FALSE
                self.send_email(consolidated_key,self.event['business_account'])
                self.send(self.event, self.context, FAILED, self.response_data, "No CIDR in IPMNGMTTable")
                return
            cidr_row = {
                'cidr': query_response['Items'][0]['cidr']['S'],
                'available_ips': ip,
                'is_allocated': query_response['Items'][0]['is_allocated']['S'],
                'region': region,
                'consolidated_key': query_response['Items'][0]['consolidated_key']['S'],
                'environment': self.environment
            }
            insert_response = self.dynamodb_client.put_item(
                TableName=self.cidr_table_name,
                Item={
                    'cidr': {"S": cidr_row['cidr']},
                    'available_ips': {"S": cidr_row['available_ips']},
                    'is_allocated': {"S": 'FLAG'},
                    'region': {"S": cidr_row['region']},
                    'consolidated_key': {"S": cidr_row['consolidated_key']},
                    'environment': {"S": cidr_row['environment']}
                })
            self.event['fetch_cidr'] = TRUE
            return cidr_row
        except Exception as e:
            print(str(e))
            self.event['fetch_cidr'] = FALSE

    def send_email(self, ip,account_name):
        try:
            # This address must be verified with Amazon SES.
            sender_id = self.sender_id
            session = boto3.session.Session()
            ses_client = session.client('ses')

            # The email body for recipients with non-HTML email clients.
            body_text = "Hello Team,\r\n VPC Creation/Extension for Account " + account_name+\
                        " failed as the CIDR blocks for " + str(ip) + " exhausted.\
                        Please add more IPs to IP Management table in master account and update the network product."

            # The HTML body of the email.
            body_html = """
                                <html>
                                <head></head>
                                <body>
                                <h2>Hello Team,</h2>
                                <p>VPC Creation/Extension for Account """ + account_name+\
                                 """ failed as the CIDR blocks for """ + str(ip) + """ exhausted.\
                                  Please add more IPs to IP Management table in master account and update the network product.</p>
                                <p>Regards,</p>
                                <p>Cloud Services Team</p>
                                </body>
                                </html>
                                """

            # Provide the contents of the email.
            send_mail_response = ses_client.send_email(
                Source=sender_id,
                Destination={
                    'ToAddresses': [self.operations_dl]
                },
                Message={
                    'Subject': {
                        'Data': 'VPC Creation/extension Failed'

                    },
                    'Body': {
                        'Text': {
                            'Data': body_text

                        },
                        'Html': {
                            'Data': body_html

                        }
                    }
                }
            )
            print(send_mail_response)
            return send_mail_response
        except Exception as e:
            print(str(e))
            return str(e)

    def send(self, event, context, response_status, response_data, reason_data):
        '''
        Send status to the cloudFormation
        Template.
        '''
        print("Inside send method")
        response_url = event['ResponseURL']

        response_body = {}
        response_body['Status'] = response_status
        response_body['Reason'] = reason_data + ' See the details in CloudWatch Log Stream: ' + \
                                  context.log_stream_name
        if self.event['RequestType'] == 'Update' or self.event['RequestType'] == 'Delete':
            response_body['PhysicalResourceId'] = event['RequestId']
        response_body['StackId'] = event['StackId']
        response_body['RequestId'] = event['RequestId']
        response_body['LogicalResourceId'] = event['LogicalResourceId']
        response_body['Data'] = response_data

        json_responsebody = json.dumps(response_body)

        print("Response body:{}".format(json_responsebody))

        headers = {
            'content-type': '',
            'content-length': str(len(json_responsebody))
        }

        try:
            response = requests.put(response_url,
                                    data=json_responsebody,
                                    headers=headers)
            print("Status code:{} ".format(response.reason))
        except Exception as exception:
            print("send(..) failed executing requests.put(..):{} ".format(str(exception)))


def lambda_handler(event, context):
    """
    Lambda handler calls the function that fetches CIDR block
    """
    try:
        fetch_cidr_obj = FetchCIDR(event, context)
        fetch_cidr_obj.fetch_vpc_cidr()
        fetch_cidr_obj.fetch_extension_cidr()
        print(event)
        return event
    except Exception as exception:
        logger.error(str(exception))
