import boto3
import logging
import time
import json
import random
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

child_account_role_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))
TRUE = "TRUE"
FALSE = "FALSE"
SUCCESS = "SUCCESS"
FAILED = "FAILED"
PENDING = "PENDING"

class TGWAttachment(object):
    """
    # Class: DisassociateTGWAttachment
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        self.result = {'tgw_attachment_disassociate': {}}
        self.res_dict = {}
        try: 
            #Getting input paramteres
            
            logger.info("Getting relevant input params from event")
            self.account_id = self.event['ProvisionedProduct']['AccountNumber']
            self.regions = [item for item in self.event['RegionIpDictionary'] if self.event['RegionIpDictionary'][item] != "No-VPC"]
            self.payer_account = self.event['SSMParameters']['audit_account']
            self.account_type = ("Private" if "Private" in event['ProvisionedProduct']['OU'] else ("Hybrid"  if "Hybrid" in event['ProvisionedProduct']['OU'] else "Public")).upper()          
 
            logger.info("Creating Session and AWS Service Clients")
            session = boto3.session.Session()
            sts_client = session.client('sts')
            child_account_role_arn = "arn:aws:iam::" + str(self.account_id) + ":role/AWSControlTowerExecution"
            child_account_role_creds = sts_client.assume_role(RoleArn=child_account_role_arn,
                                                              RoleSessionName=child_account_role_session_name)
            credentials = child_account_role_creds.get('Credentials')
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)

        except Exception as ex:
            logger.error("Encountered error while getting input parameters".format(ex)) 
            self.result.update({'attachment_disassociate' : FAILED})

 
    def disassociate_TGW_attahment(self):     
        """
        # Takes request body
        # return: resource share status
        """
        try:
            for region in self.regions:
                self.region = region
                self.res_dict = {self.region : {}}
                self.result['tgw_attachment_disassociate'].update({'account_type': self.account_type})
                
                #Getting TGW Details
                self.tgw_table_name = self.get_ssm_param('tgw_table_name') 
                self.dynamodb_client = boto3.client("dynamodb")
                tgw_table = self.dynamodb_client.scan(TableName=self.tgw_table_name)
                for item in tgw_table['Items']:
                    if self.payer_account == item['account_id']['S'] and self.region == item['region']['S']:
                        self.environment = item['environment']['S']
                        self.url = item['TGW_ATTACH_POST_URL']['S']
                        self.key = item['TGW_API_KEY']['S']
                        self.transitgatewayid = item['TransitgatewayId']['S']
                        self.res_dict[self.region].update({'TransitGatewayId': self.transitgatewayid })
                self.result['tgw_attachment_disassociate'].update({'environment': self.environment}) 
                
                #Checking if TGW Attachment is present already
                self.child_account_ec2_client = self.assumeRoleSession.client('ec2',region_name = self.region)
                #Getting VPC Id
                vpc_response = self.child_account_ec2_client.describe_vpcs(
                    Filters=[
                        {
                            'Name': 'tag:Name',
                            'Values': ['platform-VPC']
                        }
                    ]
                )
                logger.info(vpc_response)
                if len(vpc_response['Vpcs']) > 0:
                    self.vpc_id = vpc_response['Vpcs'][0]['VpcId']
                    self.vpc_cidr = []
                    cidr_response = vpc_response['Vpcs'][0]['CidrBlockAssociationSet']
                    for item in cidr_response:
                        self.vpc_cidr.append(item['CidrBlock'])
                    print(self.vpc_cidr)
                    self.res_dict[self.region].update( {'vpc_id': self.vpc_id})
                    self.res_dict[self.region].update( {'vpc_cidr': self.vpc_cidr})
                    logger.info("platform-VPC - {}".format(self.vpc_id))
                else:
                    logger.info("No platform-VPC - {} available".format(self.vpc_id))
                    
                #Getting Subnet Ids
                subnet_response = self.child_account_ec2_client.describe_subnets(
                    Filters=[
                        {
                            'Name': 'vpc-id',
                            'Values': [self.vpc_id]
                        },
                    ],
                )
                logger.info(subnet_response)
                self.subnet_dict_name = {'PRIVATE': [], 'PUBLIC': []}
                self.subnet_dict_cidr = {'PRIVATE': [], 'PUBLIC': []}
                if len(subnet_response['Subnets']) > 0:
                   for item in subnet_response['Subnets']:
                       for tag in item['Tags']:
                            if tag['Key'] == 'Name':
                                temp = tag['Value'].split('-')
                                if 'private' in temp:
                                    self.subnet_dict_name['PRIVATE'].append(item['SubnetId'])
                                    self.subnet_dict_cidr['PRIVATE'].append(item['CidrBlock'])
                                elif 'public' in temp:
                                    self.subnet_dict_name['PUBLIC'].append(item['SubnetId'])
                                    self.subnet_dict_cidr['PUBLIC'].append(item['CidrBlock'])
                self.res_dict[self.region].update( {'subnet_id': self.subnet_dict_name})
                self.res_dict[self.region].update( {'subnet_cidr': self.subnet_dict_cidr})
                self.update_result()
                if self.account_type == 'PRIVATE' or self.account_type == 'HYBRID':
                    self.disassociate_attachment()
            return self.result
        except Exception as exception:
            logger.error(str(exception))
            self.result.update({'attachment_disassociate' : FAILED})
            return self.result

    def disassociate_attachment(self):
        try:
            logger.info("Proceeding to disassociate tgw attachment in {}".format(self.region))
            tgw_id_response = self.child_account_ec2_client.describe_transit_gateway_attachments()
            tgw_attachment = FALSE
            if len(tgw_id_response['TransitGatewayAttachments']) > 0:
                for item in tgw_id_response['TransitGatewayAttachments']:
                    if item['TransitGatewayId'] == self.transitgatewayid:
                        tgw_attachment = TRUE
                        self.attachment = item['TransitGatewayAttachmentId']
                        logger.info("Attachment {} for transitgateway {} is there".format(item['TransitGatewayAttachmentId'],self.transitgatewayid))

            if tgw_attachment == TRUE:
                #TGW Disassociation
                #Getting paload to pass to Global network account to disassociate TGW attachment
                payload = {'vpc': {},'attachment': {},'vpc_cidrs': {}, 'vpc_subnets':{}}
                payload['vpc'].update({'id': self.vpc_id})
                payload['vpc'].update({'account_id': self.account_id})
                payload['vpc'].update({'account_type': self.account_type})
                payload['attachment'].update({'id':self.attachment})
                payload['attachment'].update({'region':self.region})
                payload['attachment'].update({'environment':self.environment})
                payload['vpc_cidrs'] = []
                for item in self.vpc_cidr:
                    payload['vpc_cidrs'].append({'cidr': item})
                payload['vpc_subnets'] = []
                for key,value in self.subnet_dict_cidr.items():
                    for temp in value:
                        if key == 'PRIVATE':
                            payload['vpc_subnets'].append({'cidr': temp,'type': key})
                        elif key == 'PUBLIC':
                            payload['vpc_subnets'].append({'cidr': temp,'type': key})
                logger.info(json.dumps(payload))                    
                #Invoking global network accept transitgateway attachment post api call
                headers = {'x-api-key':self.key}
                logger.info("Entered DELETE API with '{0}".format(payload))
                request_response = requests.delete(url=self.url, data=json.dumps(payload), headers=headers)
                logger.info(request_response)
                status_code = request_response.status_code
                status_message = request_response.json()
                if status_code == 200:
                    logger.info("Successfully invoked tgw disassociate attachment api.")
                    self.res_dict[self.region].update({'status' : SUCCESS})
                    self.update_result()
                else:    
                    logger.info("Something wrong with invoking tgw attachment accept api.")
                    logger.info("Error code'{0}' and error message is '{1}'".format(status_code,status_message))
                    self.res_dict[self.region].update({'status' : FAILED})
                    self.update_result()
                    self.alert_operations(self.account_id, self.region,self.event['RequestEventData']['RequestNo'], status_message)  
            return self.result       
        except Exception as exception:
            logger.error(str(exception))
            self.res_dict[self.region].update({'status' : FAILED})
            self.update_result()
            return self.result

            
    def update_result(self):
        try:
            if self.region == 'us-east-1':
                self.result['tgw_attachment_disassociate'].update({'us-east-1': self.res_dict[self.region]})
            elif self.region == 'eu-west-1':
                self.result['tgw_attachment_disassociate'].update({'eu-west-1':self.res_dict[self.region]})
            elif self.region == 'ap-southeast-1':
                self.result['tgw_attachment_disassociate'].update({'ap-southeast-1':self.res_dict[self.region]})
            return self.result
        except Exception as exception:
            logger.error(str(exception))
            self.result.update({'tgw_attachment_disassociate_update_result' : FAILED})
            return self.result 
            

    def get_ssm_param(self,parameter_name):
        """
        param: parametre_name
        return: parameter value for the given param name
        """
        try:
            self.ssm_client = boto3.client("ssm")
            parameter = self.ssm_client.get_parameter(Name=parameter_name,WithDecryption=True)
            if parameter:
                return parameter['Parameter']['Value']
        except Exception as ex:
            logger.error("Encountered error while getting parameters".format(ex))
            self.result.update({'tgw_attachment_disassociate_get_parameter' : FAILED})
            return self.result 

            
    def alert_operations(self,account_id, region_name,request_id, message):
        try:
            self.ses_client = boto3.client('ses')
            logger.info("Sending failed email")
            failure_operation_dl_str = self.get_ssm_param("failure_operation_dl")
            sender_id = self.get_ssm_param("sender_id")
            body_text = """Hello Team\n The following error occurred during disassociate TGW Attachment request""" \
                + """.\n• Account Id : """ + str(account_id) + " "\
                    + """.\n• Region """ + str(region_name) + " "\
                        + """.\n• Error : """ + str(message) + " "\
                        + """\nBest Regards,\n AWS Platform Engineering team"""

            # The HTML body of the email.
            body_html = body_html = """<html>
                    <body>
                    <p style="font-family:'Arial Nova'">Hello Team,<p>
                    <p></p>
                    <p style="font-family:'Arial Nova'">The following error occurred during TGW Attachment disassociate operation..</p>
                    <ul>
                    <li style="font-family:'Arial Nova'">Account Id: """ + str(account_id) + """</li>
                    </ul>
                    <ul>
                    <li style="font-family:'Arial Nova'">Request Number: """ + str(request_id) + """</li>
                    </ul>
                    <ul>
                    <li style="font-family:'Arial Nova'">Region: """ + str(region_name) + """</li>
                    </ul>
                    <ul>
                    <li style="font-family:'Arial Nova'">Error: """ + str(message) + """</li>
                    </ul>
                    <p style="font-family:'Arial Nova'"></p>
                    <p style="font-family:'Arial Nova'">Thanks,</p>
                    <p style="font-family:'Arial Nova'"> AWS Platform Engineering Team.</p>
                    </body>
                    </html>
                """

            send_mail_response = self.ses_client.send_email(
                Source= sender_id,
                Destination={
                    'ToAddresses': [failure_operation_dl_str]
                },
                Message={
                    'Subject': {
                        'Data':' ALERT: Disassociate TGW Attachment Failed'
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
            logger.info(send_mail_response)
            return send_mail_response
        except Exception as e:
            logger.error(str(e))
            return str(e)

            
def lambda_handler(event, context):
    """
    Lambda handler calls the function which disassociates the TGW attachment in the child account
    """
    result = {}
    print('event ' + str(event))
    result.update(event)
    try:
        tgw_integration = TGWAttachment(event, context)
        output = tgw_integration.disassociate_TGW_attahment()
        result.update(output)
        return result
    except Exception as exception:
        logger.error(str(exception))
        result.update({'tgw_attachment_disassociate' : FAILED})
        return result
