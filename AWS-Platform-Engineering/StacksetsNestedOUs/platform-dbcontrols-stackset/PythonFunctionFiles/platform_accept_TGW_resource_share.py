import boto3
import logging
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
TRUE = "TRUE"
FALSE = "FALSE"
SUCCESS = "SUCCESS"
FAILED = "FAILED"

class AcceptTGWResourceShare(object):
    """
    # Class: AcceptTGWResourceShare
    # Description: Accept the TGW Resource to be shared in the child account
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        self.result = {'accept_tgw_resource_share': {}}
        self.res_dict = {}
        try: 
            #Getting input paramteres
            
            logger.info("Getting relevant input params from event")
            self.resource_properties = self.event['ResourceProperties']
            self.account_id = self.event['ResourceProperties']['AccountNumber']
            self.payer_account = self.resource_properties['AWSAccountId']
            self.regions = list([item for item in self.event['region_ip_dict'].keys()])
            self.resourceArn = ''
            self.environment = ''
            self.invite_arn = ''
            self.tgw_account = ''
  
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
            self.result.update({'accepting_tgw_resource_share' : FAILED})

 
    def accept_TGW_resource_share(self):     
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
                        self.transitgatewayid = item['TransitgatewayId']['S']
                        self.tgw_account = item['TGW_Account']['S']
                self.accept_resource_share()
            return self.result            
        except Exception as exception:
            logger.error(str(exception))
            self.result.update({'accepting_tgw_resource_share' : FAILED})
            return self.result

        
    def accept_resource_share(self):
        try:
            logger.info("proceeding to accept shared resource in {}".format(self.region))
            #Checking if TGW Resource shared and present already
            resource_accepted = FALSE
            self.child_account_ram_client = self.assumeRoleSession.client('ram', region_name=self.region)
            ram_response = self.child_account_ram_client.list_resources(
                resourceOwner='OTHER-ACCOUNTS',
                resourceType='ec2:TransitGateway'
            )
            logger.info(ram_response)
            if len(ram_response['resources']) > 0:
                for item in ram_response['resources']:
                    if item['arn'] == self.resourceArn and item['status'] == 'AVAILABLE':
                        resource_accepted = TRUE
                        self.res_dict[self.region].update({'status': "PASSED"})
                        self.update_result()
                        logger.info("TGW Resource is already shared and is in available state")
            
            pending_invite = FALSE
            if resource_accepted == FALSE:         
                #getting resource share invitaion arn
                invite_arn_response = self.child_account_ram_client.get_resource_share_invitations()
                logger.info(invite_arn_response)
                if len(invite_arn_response['resourceShareInvitations']) > 0:
                    for item in invite_arn_response['resourceShareInvitations']:
                        if item['senderAccountId'] == self.tgw_account:
                            self.invite_arn = item['resourceShareInvitationArn']
                if self.invite_arn:
                    #listing pending invitation arns            
                    pending_invite_response = self.child_account_ram_client.list_pending_invitation_resources(
                        resourceShareInvitationArn=self.invite_arn
                    )
                    logger.info(pending_invite_response)
                    if len(pending_invite_response['resources']) > 0:
                        for item in pending_invite_response['resources']:
                            if item['arn'] == self.resourceArn and item['status'] == 'PENDING':
                                pending_invite = TRUE
                                logger.info("TGW Resource share invite {} is in pending state, proceeding to accept...".format(self.invite_arn))                            
            if pending_invite == TRUE:           
                tgw_accept_response = self.child_account_ram_client.accept_resource_share_invitation(
                    resourceShareInvitationArn=self.invite_arn
                )
                if tgw_accept_response:
                    if tgw_accept_response['resourceShareInvitation']['status'] == 'ACCEPTED':
                        logger.info("TGW Resource is Accepted")
                        self.res_dict[self.region].update({'status': SUCCESS})
                        self.update_result()
                    else:
                        logger.info("Failed to accept TGW Resource")
                        self.res_dict[self.region].update({'status': FAILED})
                        self.update_result()
                        status_message = "Failed to accept TGW Resource"
                        self.alert_operations(self.account_id, self.region,self.event['ResourceProperties']['RequestNo'], status_message)
            else:
                logger.info("No pending resource share invite is available to accept")  
            return self.result          
        except Exception as exception:
            logger.error(str(exception))
            self.res_dict[self.region].update({'status' : FAILED})
            self.update_result()
            return self.result
            

    def update_result(self):
        try:
            if self.region == 'us-east-1':
                self.result['accept_tgw_resource_share'].update({'us-east-1': self.res_dict[self.region]})
            elif self.region == 'eu-west-1':
                self.result['accept_tgw_resource_share'].update({'eu-west-1':self.res_dict[self.region]})
            elif self.region == 'ap-southeast-1':
                self.result['accept_tgw_resource_share'].update({'ap-southeast-1':self.res_dict[self.region]})
            return self.result
        except Exception as exception:
            logger.error(str(exception))    
            self.result.update({'accept_tgw_resource_update_result' : FAILED})
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
            self.result.update({'accept_tgw_resource_get_parameter' : FAILED})
            return self.result


    def alert_operations(self,account_id, region_name,request_id, message):
        try:
            self.ses_client = boto3.client('ses')
            logger.info("Sending failed email")
            failure_operation_dl_str = self.get_ssm_param("failure_operation_dl")
            sender_id = self.get_ssm_param("sender_id")
            body_text = """Hello Team\n The following error occurred during Accepting TGW resource share """ \
                + """.\n• Account Id : """ + str(account_id) + " "\
                    + """.\n• Region """ + str(region_name) + " "\
                        + """.\n• Error : """ + str(message) + " "\
                        + """\nBest Regards,\n AWS Platform Engineering team"""

            # The HTML body of the email.
            body_html = body_html = """<html>
                    <body>
                    <p style="font-family:'Arial Nova'">Hello Team,<p>
                    <p></p>
                    <p style="font-family:'Arial Nova'">The following error occurred during Accepting TGW resource share operation..</p>
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
                        'Data':' ALERT: Accepting TGW Resource Share Failed'
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
  
            
def lambda_handler(event, context):
    """
    Lambda handler calls the function which accepts the TGW resource share in the child account
    """
    result = {}
    print('event ' + str(event))
    result.update(event)
    try:
        tgw_integration = AcceptTGWResourceShare(event, context)
        output = tgw_integration.accept_TGW_resource_share()
        result.update(output)
        return result
    except Exception as exception:
        logger.error(str(exception))
        result.update({'accept_tgw_resource_share' : FAILED})
        return result
