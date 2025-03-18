import boto3
import logging
import requests
import time
import json
import random


logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

child_account_role_session_name = "ChildAccountSession-" + str(random.randint(1, 100000))
SUCCESS = "SUCCESS"
FAILED = "FAILED"
PASSED = "PASSED"
TRUE = "TRUE"
FALSE = "FALSE"

class RemoveTGWResourceShare(object):
    """
    # Class: RemoveTGWResourceShare
    # Description: Remove the TGW Resource shared in the child account
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        self.result = {'remove_tgw_resource_share': {}}
        self.res_dict = {}
        try: 
            #Getting input paramteres
            
            logger.info("Getting relevant input params from event")
            self.account_id = self.event['ResourceProperties']['AccountNumber']
            self.regions = list([item for item in self.event['region_ip_dict'].keys()])
            self.payer_account = self.event['ResourceProperties']['AWSAccountId']
            self.account_type = self.event['ResourceProperties']['Environment'].upper()           
            self.resourceArn = ''
            self.environment = ''
            self.request_body = {}
  
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
            self.result.update({'removing_tgw_resource_share' : FAILED})
            
 
    def remove_TGW_resource_share(self):     
        """
        # Takes request body
        # return: resource share status
        """
        try:
            for region in self.regions:
                self.region = region
                self.res_dict = {self.region : {}}
                #Getting TGW Details
                self.tgw_table_name = self.get_ssm_param('tgw_table_name') 
                self.dynamodb_client = boto3.client("dynamodb")
                tgw_table = self.dynamodb_client.scan(TableName=self.tgw_table_name)
                for item in tgw_table['Items']:
                    if self.payer_account == item['account_id']['S'] and self.region == item['region']['S']:
                        self.resourceArn = item['TGW_ARN']['S']
                        self.environment = item['environment']['S']
                        self.url = item['TGW_SHARE_POST_URL']['S']
                        self.key = item['TGW_API_KEY']['S']
                        logger.info(self.url)
                if self.account_type == 'PRIVATE' or self.account_type == 'HYBRID':
                    self.remove_resource_share()                    
            return self.result
        except Exception as exception:
            logger.error(str(exception))
            self.result.update({'removing_tgw_resource_share' : FAILED})
            return self.result


    def remove_resource_share(self):
        try:
            logger.info("proceeding to remove resource share in {}".format(self.region))
            #Checking if TGW Resource share is already exists
            self.child_account_ram_client = self.assumeRoleSession.client('ram', region_name = self.region)
            ram_response = self.child_account_ram_client.list_resources(
                resourceOwner='OTHER-ACCOUNTS',
                resourceType='ec2:TransitGateway'
            )
            logger.info(ram_response)
            tgw_available = FALSE
            if len(ram_response['resources']) > 0:
                for item in ram_response['resources']:
                    if item['arn'] == self.resourceArn and item['status'] == 'AVAILABLE':
                        tgw_available = TRUE
                        logger.info("TGW Resource is there")
            if tgw_available == TRUE:
                #Requesting tgw resource share
                logger.info("Proceeding to DELETE API call...")
                self.request_body = {'account': {}}
                self.request_body['account'].update({'account_id': self.account_id})
                self.request_body['account'].update({'region': self.region})
                self.request_body['account'].update({'environment': self.environment})
                logger.info(json.dumps(self.request_body))
                headers = {'x-api-key':self.key}
                logger.info("Entered DELETE with '{0}".format(self.request_body))
                request_response = requests.delete(url=self.url, data=json.dumps(self.request_body), headers=headers)
                logger.info(request_response)
                status_code = request_response.status_code
                status_message = request_response.json()
                if status_code == 200:
                    logger.info("Successfully requested remove tgw resource share.")
                    self.res_dict[self.region].update({'status' : SUCCESS})
                    self.update_result()
                else:    
                    logger.info("Something wrong with requesting tgw resource share.")
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


    def update_result(self):
        try:
            if self.region == 'us-east-1':
                self.result['remove_tgw_resource_share'].update({'us-east-1': self.res_dict[self.region]})
            elif self.region == 'eu-west-1':
                self.result['remove_tgw_resource_share'].update({'eu-west-1':self.res_dict[self.region]})
            elif self.region == 'ap-southeast-1':
                self.result['remove_tgw_resource_share'].update({'ap-southeast-1':self.res_dict[self.region]})
            return self.result
        except Exception as exception:
            logger.error(str(exception))
            self.result.update({'remove_tgw_resource_share_update_result' : FAILED})
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
            self.result.update({'remove_tgw_resource_share_get_parameter' : FAILED})
            return self.result


    def alert_operations(self,account_id, region_name,request_id, message):
        try:
            self.ses_client = boto3.client('ses')
            logger.info("Sending failed email")
            failure_operation_dl_str = self.get_ssm_param("failure_operation_dl")
            sender_id = self.get_ssm_param("sender_id")
            body_text = """Hello Team\n The following error occurred during Request TGW resource share """ \
                + """.\n• Account Id : """ + str(account_id) + " "\
                    + """.\n• Region """ + str(region_name) + " "\
                        + """.\n• Error : """ + str(message) + " "\
                        + """\nBest Regards,\n AWS Platform Engineering team"""

            # The HTML body of the email.
            body_html = body_html = """<html>
                    <body>
                    <p style="font-family:'Arial Nova'">Hello Team,<p>
                    <p></p>
                    <p style="font-family:'Arial Nova'">The following error occurred during Requesting Remove TGW resource share operation..</p>
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
                        'Data':' ALERT: Disassociate TGW Resource Share Failed'
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
    Lambda handler calls the function which accepts the TGW resource share in the child account
    """
    result = {}
    print('event ' + str(event))
    result.update(event)
    try:
        tgw_integration = RemoveTGWResourceShare(event, context)
        output = tgw_integration.remove_TGW_resource_share()
        result.update(output)
        return result
    except Exception as exception:
        logger.error(str(exception))
        result.update({'removing_tgw_resource_share' : FAILED})
        return result
