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
PASSED = "PASSED"

class TGWAttachment(object):
    """
    # Class: ACCEPT TGW Attachment
    # Description: Request the TGW Attachment Accept API
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        self.result = {'tgw_accept_api': {}}
        self.res_dict = {}
        try: 
            #Getting input paramteres
            logger.info("Getting relevant input params from event")
            self.account_id = self.event['ResourceProperties']['AccountNumber']
            self.regions = list([item for item in self.event['region_ip_dict'].keys()])
            self.payer_account = self.event['ResourceProperties']['AWSAccountId']            
            self.tgw_details = self.event['tgw']
 
            logger.info("Creating Session and AWS Service Clients")
            session = boto3.session.Session()
            sts_client = session.client('sts')
            child_account_role_arn = "arn:aws:iam::" + self.account_id + ":role/AWSControlTowerExecution"
            child_account_role_creds = sts_client.assume_role(RoleArn=child_account_role_arn,
                                                              RoleSessionName=child_account_role_session_name)
            credentials = child_account_role_creds.get('Credentials')
            accessKeyID = credentials.get('AccessKeyId')
            secretAccessKey = credentials.get('SecretAccessKey')
            sessionToken = credentials.get('SessionToken')
            self.assumeRoleSession = boto3.session.Session(accessKeyID, secretAccessKey, sessionToken)

        except Exception as ex:
            logger.error("Encountered error while getting input parameters".format(ex)) 
            self.result.update({'tgw_attachment_accept' : FAILED})

 
    def Accept_TGW_attahment(self):     
        """
        # Takes request body
        # return: resource attachment status
        """
        try:
            for region in self.regions:
                self.region = region
                self.res_dict = {self.region : {}}
                #Getting URL Details
                self.tgw_table_name = self.get_ssm_param('tgw_table_name') 
                self.dynamodb_client = boto3.client("dynamodb")
                tgw_table = self.dynamodb_client.scan(TableName=self.tgw_table_name)
                for item in tgw_table['Items']:
                    if self.payer_account == item['account_id']['S'] and self.region == item['region']['S']:
                        self.url = item['TGW_ATTACH_POST_URL']['S']
                        self.key = item['TGW_API_KEY']['S']
                        print(self.url)
                self.accept_attachment()
            return self.result   
        except Exception as exception:
            logger.error(str(exception))
            self.result.update({'tgw_attachment_accept' : FAILED})
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
            self.result.update({'tgw_attachment_accept_get_parameter' : FAILED})
            return self.result

            
    def alert_operations(self,account_id, region_name,request_id, message):
        try:
            self.ses_client = boto3.client('ses')
            logger.info("Sending failed email")
            failure_operation_dl_str = self.get_ssm_param("failure_operation_dl")
            sender_id = self.get_ssm_param("sender_id")
            body_text = """Hello Team\n The following error occurred during TGW Attachment accept request""" \
                + """.\n• Account Id : """ + str(account_id) + " "\
                    + """.\n• Region """ + str(region_name) + " "\
                        + """.\n• Error : """ + str(message) + " "\
                        + """\nBest Regards,\n AWS Platform Engineering team"""

            # The HTML body of the email.
            body_html = body_html = """<html>
                    <body>
                    <p style="font-family:'Arial Nova'">Hello Team,<p>
                    <p></p>
                    <p style="font-family:'Arial Nova'">The following error occurred during TGW Attachment accept request operation..</p>
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
                        'Data':' ALERT: Accept TGW Attachment Failed'
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
 

    def update_result(self):
        try:
            if self.region == 'us-east-1':
                self.result['tgw_accept_api'].update({'us-east-1': self.res_dict[self.region]})
            elif self.region == 'eu-west-1':
                self.result['tgw_accept_api'].update({'eu-west-1':self.res_dict[self.region]})
            elif self.region == 'ap-southeast-1':
                self.result['tgw_accept_api'].update({'ap-southeast-1':self.res_dict[self.region]})
            return self.result
        except Exception as exception:
            logger.error(str(exception))
            self.result.update({'tgw_attachment_accept_update_result' : FAILED})
            return self.result          


    def accept_attachment(self):
        try:
            logger.info("Proceeding to accept attachment in {}".format(self.region))
            tgw_attachment = FALSE
            if self.tgw_details[self.region]['tgw_attachment_id']:
                self.child_account_ec2_client = self.assumeRoleSession.client('ec2',region_name=self.region)
                tgw_id_response = self.child_account_ec2_client.describe_transit_gateway_attachments(TransitGatewayAttachmentIds=[
                    self.tgw_details[self.region]['tgw_attachment_id'],
                ])
                logger.info(tgw_id_response)
                if len(tgw_id_response['TransitGatewayAttachments']) > 0:
                    for item in tgw_id_response['TransitGatewayAttachments']:
                        if item['State'] == 'pendingAcceptance' :
                            tgw_attachment = TRUE
                            logger.info("Attachment {} for transitgateway {} is ready to be accepted".format(item['TransitGatewayAttachmentId'],self.tgw_details[self.region]['TransitGatewayId']))
                        elif item['State'] == 'available':
                            logger.info("Attachment {} for transitgateway {} is in available state, nothing to be accepted".format(item['TransitGatewayAttachmentId'],self.tgw_details[self.region]['TransitGatewayId']))
                            self.res_dict[self.region].update({'status' : PASSED})
                            self.update_result()
            if tgw_attachment == TRUE:
                #Getting paload to pass to Global network account to accept TGW attachment
                payload = {}
                payload['vpc'] = { 'id' : self.tgw_details[self.region]['vpc_id'], 'account_id': self.account_id, "account_type":  self.tgw_details['account_type']}
                payload['attachment'] = {'id': self.tgw_details[self.region]['tgw_attachment_id'], 'region': self.region, 'environment': self.tgw_details['environment']}
                payload['vpc_cidrs'] = []
                for item in self.tgw_details[self.region]['vpc_cidr']:
                    payload['vpc_cidrs'].append({'cidr': item})
                payload['vpc_subnets'] = []
                for key,value in self.tgw_details[self.region]['subnet_cidr'].items():
                    for temp in value:
                        if key == 'PRIVATE':
                            payload['vpc_subnets'].append({'cidr': temp,'type': key})
                        elif key == 'PUBLIC':
                            payload['vpc_subnets'].append({'cidr': temp,'type': key})
                logger.info(json.dumps(payload))                   
                #Invoking global network accept transitgateway attachment post api call
                headers = {'x-api-key':self.key}
                logger.info("Entered Post with '{0}".format(payload))
                request_response = requests.post(url=self.url, data=json.dumps(payload), headers=headers)
                status_code = request_response.status_code
                status_message = request_response.json()
                if status_code == 200:
                    logger.info("Successfully invoked tgw accept attachment api.")
                    self.res_dict[self.region].update({'status' : SUCCESS})
                    self.update_result()
                else:    
                    logger.info("Something wrong with invoking tgw attachment accept api.")
                    logger.info("Error code'{0}' and error message is '{1}'".format(status_code,status_message))
                    self.res_dict[self.region].update({'status' : FAILED})
                    self.update_result()
                    self.alert_operations(self.account_id, self.region,self.event['ResourceProperties']['RequestNo'], status_message)            
            return self.result
        except Exception as exception:
            logger.error(str(exception))
            self.res_dict[self.region].update({'status' : FAILED})
            self.update_result()
            return self.result

            
def lambda_handler(event, context):
    """
    Lambda handler calls the tgw attach api to accept tgw attachment in the global network account
    """
    result = {}
    print('event ' + str(event))
    result.update(event)
    try:
        tgw_integration = TGWAttachment(event, context)
        output = tgw_integration.Accept_TGW_attahment()
        result.update(output)
        return result
    except Exception as exception:
        logger.error(str(exception))
        result.update({'tgw_attchment_accept' : FAILED})
        return result
